use std::io::{Cursor, Read};

use bzip2_rs::DecoderReader;
use ruzstd::decoding::StreamingDecoder;
use serde::Serialize;

use crate::error::CondaWasmError;

const MAX_ENTRY_SIZE: u64 = 256 * 1024 * 1024; // 256 MB per file
const MAX_TOTAL_SIZE: u64 = 2 * 1024 * 1024 * 1024; // 2 GB total

#[derive(Debug, Default, Serialize)]
pub struct ExtractStats {
    pub file_count: usize,
    pub total_size: usize,
}

fn is_safe_tar_path(path: &str) -> bool {
    if path.is_empty() {
        return false;
    }
    if path.starts_with('/') || path.starts_with('\\') {
        return false;
    }
    if path.contains("..") {
        return false;
    }
    if path.contains('\\') {
        return false;
    }
    if path.starts_with("C:") || path.starts_with("c:") || path.contains(":\\") {
        return false;
    }
    true
}

fn normalize_tar_link_target(link_path: &str, link_target: &str) -> Option<String> {
    if link_target.is_empty()
        || link_target.starts_with('/')
        || link_target.starts_with('\\')
        || link_target.contains('\\')
        || link_target.starts_with("C:")
        || link_target.starts_with("c:")
        || link_target.contains(":\\")
    {
        return None;
    }

    let mut components = Vec::new();
    if let Some((parent, _)) = link_path.rsplit_once('/') {
        for part in parent.split('/') {
            if !part.is_empty() && part != "." {
                components.push(part);
            }
        }
    }

    for part in link_target.split('/') {
        match part {
            "" | "." => {}
            ".." => {
                components.pop()?;
            }
            _ => components.push(part),
        }
    }

    let normalized = components.join("/");
    is_safe_tar_path(&normalized).then_some(normalized)
}

fn stream_tar_entries<R: Read, F>(
    tar: &mut tar::Archive<R>,
    on_file: &mut F,
) -> Result<ExtractStats, CondaWasmError>
where
    F: FnMut(&str, &[u8]) -> Result<(), CondaWasmError>,
{
    use std::collections::HashMap;

    let mut stats = ExtractStats::default();
    let mut file_contents: HashMap<String, Vec<u8>> = HashMap::new();
    let mut deferred_links: Vec<(String, String)> = Vec::new();

    for entry_result in tar
        .entries()
        .map_err(|e| CondaWasmError::ExtractFailed(format!("tar entries error: {e}")))?
    {
        let mut entry = entry_result
            .map_err(|e| CondaWasmError::ExtractFailed(format!("tar entry error: {e}")))?;

        let entry_type = entry.header().entry_type();

        if matches!(
            entry_type,
            tar::EntryType::Char
                | tar::EntryType::Block
                | tar::EntryType::Fifo
                | tar::EntryType::GNUSparse
        ) {
            continue;
        }

        let path = entry
            .path()
            .map_err(|e| CondaWasmError::ExtractFailed(format!("tar path error: {e}")))?
            .to_string_lossy()
            .into_owned();

        if !is_safe_tar_path(&path) {
            return Err(CondaWasmError::ExtractFailed(format!(
                "unsafe tar path rejected: {path}"
            )));
        }

        if entry_type == tar::EntryType::Symlink || entry_type == tar::EntryType::Link {
            let link_target = entry
                .link_name()
                .map_err(|e| {
                    CondaWasmError::ExtractFailed(format!("reading link name for {path}: {e}"))
                })?
                .map(|p| p.to_string_lossy().into_owned())
                .unwrap_or_default();

            let resolved = if entry_type == tar::EntryType::Symlink {
                normalize_tar_link_target(&path, &link_target)
            } else {
                normalize_tar_link_target("", &link_target)
            }
            .ok_or_else(|| {
                CondaWasmError::ExtractFailed(format!(
                    "unsafe tar link target rejected: {path} -> {link_target}"
                ))
            })?;

            deferred_links.push((path, resolved));
            continue;
        }

        if !entry_type.is_file() {
            continue;
        }

        let declared_size = entry.size();
        if declared_size > MAX_ENTRY_SIZE {
            return Err(CondaWasmError::ExtractFailed(format!(
                "tar entry too large ({} bytes): {path}",
                declared_size
            )));
        }

        let capacity = (declared_size as usize).min(16 * 1024 * 1024);
        let mut buf = Vec::with_capacity(capacity);
        entry
            .read_to_end(&mut buf)
            .map_err(|e| CondaWasmError::ExtractFailed(format!("reading tar entry {path}: {e}")))?;

        stats.file_count += 1;
        stats.total_size += buf.len();

        if stats.total_size as u64 > MAX_TOTAL_SIZE {
            return Err(CondaWasmError::ExtractFailed(
                "extraction exceeded total size limit (2 GB)".into(),
            ));
        }

        on_file(&path, &buf)?;
        file_contents.insert(path, buf);
    }

    for (path, target) in deferred_links {
        if let Some(data) = file_contents.get(&target) {
            let total_size = stats.total_size + data.len();
            if total_size as u64 > MAX_TOTAL_SIZE {
                return Err(CondaWasmError::ExtractFailed(
                    "extraction exceeded total size limit (2 GB)".into(),
                ));
            }
            stats.total_size = total_size;
            on_file(&path, data)?;
            stats.file_count += 1;
        }
    }

    Ok(stats)
}

pub fn extract_conda_streaming<F>(
    bytes: &[u8],
    mut on_file: F,
) -> Result<ExtractStats, CondaWasmError>
where
    F: FnMut(&str, &[u8]) -> Result<(), CondaWasmError>,
{
    let reader = Cursor::new(bytes);
    let mut archive = zip::ZipArchive::new(reader)
        .map_err(|e| CondaWasmError::ExtractFailed(format!("opening ZIP: {e}")))?;

    let mut stats = ExtractStats::default();

    let entry_names: Vec<String> = (0..archive.len())
        .filter_map(|i| archive.by_index(i).ok().map(|e| e.name().to_string()))
        .collect();

    for name in &entry_names {
        if name.ends_with(".tar.zst") {
            let entry = archive.by_name(name).map_err(|e| {
                CondaWasmError::ExtractFailed(format!("reading ZIP entry {name}: {e}"))
            })?;
            let inner = extract_tar_zst_streaming(entry, &mut on_file)?;
            stats.file_count += inner.file_count;
            stats.total_size += inner.total_size;
        }
    }

    Ok(stats)
}

pub fn extract_tar_bz2_streaming<F>(
    bytes: &[u8],
    mut on_file: F,
) -> Result<ExtractStats, CondaWasmError>
where
    F: FnMut(&str, &[u8]) -> Result<(), CondaWasmError>,
{
    let reader = Cursor::new(bytes);
    let decoder = DecoderReader::new(reader);
    let mut tar = tar::Archive::new(decoder);
    stream_tar_entries(&mut tar, &mut on_file)
}

fn extract_tar_zst_streaming<R: Read, F>(
    zst_reader: R,
    on_file: &mut F,
) -> Result<ExtractStats, CondaWasmError>
where
    F: FnMut(&str, &[u8]) -> Result<(), CondaWasmError>,
{
    let mut zst_reader = zst_reader;
    let decoder = StreamingDecoder::new(&mut zst_reader)
        .map_err(|e| CondaWasmError::ExtractFailed(format!("zstd decode error: {e}")))?;

    let mut tar = tar::Archive::new(decoder);
    stream_tar_entries(&mut tar, on_file)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn build_tar(entries: &[(&str, &[u8])]) -> Vec<u8> {
        let mut builder = tar::Builder::new(Vec::new());
        for (name, data) in entries {
            let mut header = tar::Header::new_gnu();
            header.set_size(data.len() as u64);
            header.set_mode(0o644);
            header.set_entry_type(tar::EntryType::Regular);
            header.set_cksum();
            builder.append_data(&mut header, name, *data).unwrap();
        }
        builder.into_inner().unwrap()
    }

    fn build_tar_with_type(name: &str, entry_type: tar::EntryType) -> Vec<u8> {
        let mut builder = tar::Builder::new(Vec::new());
        let mut header = tar::Header::new_gnu();
        header.set_size(0);
        header.set_mode(0o644);
        header.set_entry_type(entry_type);
        header.set_cksum();
        builder
            .append_data(&mut header, name, &[] as &[u8])
            .unwrap();
        let mut h2 = tar::Header::new_gnu();
        h2.set_size(2);
        h2.set_mode(0o644);
        h2.set_entry_type(tar::EntryType::Regular);
        h2.set_cksum();
        builder
            .append_data(&mut h2, "ok.txt", b"ok" as &[u8])
            .unwrap();
        builder.into_inner().unwrap()
    }

    fn build_tar_with_link(name: &str, target: &str, entry_type: tar::EntryType) -> Vec<u8> {
        let mut builder = tar::Builder::new(Vec::new());
        let mut header = tar::Header::new_gnu();
        header.set_size(0);
        header.set_mode(0o644);
        header.set_entry_type(entry_type);
        header.set_link_name(target).unwrap();
        header.set_cksum();
        builder
            .append_data(&mut header, name, &[] as &[u8])
            .unwrap();
        builder.into_inner().unwrap()
    }

    fn extract_raw_tar(tar_bytes: &[u8]) -> Result<ExtractStats, CondaWasmError> {
        let mut archive = tar::Archive::new(tar_bytes);
        stream_tar_entries(&mut archive, &mut |_, _| Ok(()))
    }

    struct TarResult {
        stats: ExtractStats,
        files: Vec<(String, Vec<u8>)>,
    }

    fn extract_raw_tar_collecting(tar_bytes: &[u8]) -> Result<TarResult, CondaWasmError> {
        let mut files = Vec::new();
        let mut archive = tar::Archive::new(tar_bytes);
        let stats = stream_tar_entries(&mut archive, &mut |path, data| {
            files.push((path.to_string(), data.to_vec()));
            Ok(())
        })?;
        Ok(TarResult { stats, files })
    }

    // ── is_safe_tar_path ──

    #[test]
    fn test_safe_path_accepts_normal_paths() {
        assert!(is_safe_tar_path("info/index.json"));
        assert!(is_safe_tar_path("lib/python3.12/site-packages/foo.py"));
        assert!(is_safe_tar_path("a/b/c.txt"));
    }

    #[test]
    fn test_safe_path_rejects_empty() {
        assert!(!is_safe_tar_path(""));
    }

    #[test]
    fn test_safe_path_rejects_absolute() {
        assert!(!is_safe_tar_path("/etc/passwd"));
        assert!(!is_safe_tar_path("\\Windows\\system32"));
    }

    #[test]
    fn test_safe_path_rejects_traversal() {
        assert!(!is_safe_tar_path("../escape"));
        assert!(!is_safe_tar_path("a/../../escape"));
        assert!(!is_safe_tar_path("foo/.."));
    }

    #[test]
    fn test_safe_path_rejects_backslash() {
        assert!(!is_safe_tar_path("a\\b\\c"));
    }

    #[test]
    fn test_safe_path_rejects_windows_drive() {
        assert!(!is_safe_tar_path("C:\\Windows\\system32"));
        assert!(!is_safe_tar_path("c:\\users"));
        assert!(!is_safe_tar_path("D:\\data"));
    }

    #[test]
    fn test_normalize_link_target_rejects_escape_above_root() {
        assert_eq!(
            normalize_tar_link_target("lib/link.py", "../target.py").as_deref(),
            Some("target.py")
        );
        assert!(normalize_tar_link_target("link.py", "../escape.py").is_none());
        assert!(normalize_tar_link_target("lib/link.py", "../../escape.py").is_none());
        assert!(normalize_tar_link_target("lib/link.py", "/etc/passwd").is_none());
    }

    // ── stream_tar_entries: path traversal ──

    fn build_tar_raw_path(raw_path: &[u8], data: &[u8]) -> Vec<u8> {
        let mut buf = vec![0u8; 512];
        let len = raw_path.len().min(100);
        buf[..len].copy_from_slice(&raw_path[..len]);
        // mode
        buf[100..107].copy_from_slice(b"0000644");
        // size in octal
        let size_str = format!("{:011o}", data.len());
        buf[124..135].copy_from_slice(size_str.as_bytes());
        // entry type: regular file
        buf[156] = b'0';
        // magic "ustar\0" + version "00"
        buf[257..263].copy_from_slice(b"ustar\0");
        buf[263..265].copy_from_slice(b"00");
        // compute checksum
        buf[148..156].copy_from_slice(b"        ");
        let cksum: u32 = buf[..512].iter().map(|&b| b as u32).sum();
        let cksum_str = format!("{:06o}\0 ", cksum);
        buf[148..156].copy_from_slice(cksum_str.as_bytes());
        // data block (padded to 512)
        let mut data_block = data.to_vec();
        let padding = (512 - data.len() % 512) % 512;
        data_block.extend(vec![0u8; padding]);
        buf.extend(data_block);
        // end-of-archive marker (two zero blocks)
        buf.extend(vec![0u8; 1024]);
        buf
    }

    #[test]
    fn test_tar_rejects_path_traversal() {
        let tar_bytes = build_tar_raw_path(b"../escape.txt", b"bad");
        let result = extract_raw_tar(&tar_bytes);
        assert!(result.is_err());
        let err = result.unwrap_err().to_string();
        assert!(err.contains("unsafe tar path"), "error was: {err}");
    }

    #[test]
    fn test_tar_rejects_absolute_path() {
        let tar_bytes = build_tar_raw_path(b"/etc/passwd", b"root");
        let result = extract_raw_tar(&tar_bytes);
        assert!(result.is_err());
        let err = result.unwrap_err().to_string();
        assert!(err.contains("unsafe tar path"), "error was: {err}");
    }

    #[test]
    fn test_tar_rejects_unsafe_symlink_target() {
        let tar_bytes = build_tar_with_link("link.py", "../escape.py", tar::EntryType::Symlink);
        let result = extract_raw_tar(&tar_bytes);
        assert!(result.is_err());
        let err = result.unwrap_err().to_string();
        assert!(err.contains("unsafe tar link target"), "error was: {err}");
    }

    #[test]
    fn test_tar_skips_unresolved_links() {
        let tar_bytes = build_tar_with_link("link.py", "missing.py", tar::EntryType::Link);
        let result = extract_raw_tar_collecting(&tar_bytes).unwrap();
        assert_eq!(result.stats.file_count, 0);
        assert!(result.files.is_empty());
    }

    // ── stream_tar_entries: dangerous entry types ──

    #[test]
    fn test_tar_skips_char_device() {
        let tar_bytes = build_tar_with_type("dev/null", tar::EntryType::Char);
        let stats = extract_raw_tar(&tar_bytes).unwrap();
        assert_eq!(
            stats.file_count, 1,
            "should only extract ok.txt, not device"
        );
    }

    #[test]
    fn test_tar_skips_block_device() {
        let tar_bytes = build_tar_with_type("dev/sda", tar::EntryType::Block);
        let stats = extract_raw_tar(&tar_bytes).unwrap();
        assert_eq!(stats.file_count, 1);
    }

    #[test]
    fn test_tar_skips_fifo() {
        let tar_bytes = build_tar_with_type("tmp/pipe", tar::EntryType::Fifo);
        let stats = extract_raw_tar(&tar_bytes).unwrap();
        assert_eq!(stats.file_count, 1);
    }

    // ── stream_tar_entries: size limits ──

    #[test]
    fn test_tar_rejects_oversized_entry() {
        let mut builder = tar::Builder::new(Vec::new());
        let mut header = tar::Header::new_gnu();
        header.set_size(MAX_ENTRY_SIZE + 1);
        header.set_mode(0o644);
        header.set_entry_type(tar::EntryType::Regular);
        header.set_cksum();
        builder
            .append_data(&mut header, "big.bin", std::io::empty())
            .unwrap();
        let tar_bytes = builder.into_inner().unwrap();
        let result = extract_raw_tar(&tar_bytes);
        assert!(result.is_err());
        let err = result.unwrap_err().to_string();
        assert!(err.contains("too large"), "error was: {err}");
    }

    // ── normal extraction ──

    #[test]
    fn test_tar_extracts_normal_files() {
        let tar_bytes = build_tar(&[
            ("info/index.json", b"{\"name\": \"test\"}"),
            ("lib/foo.py", b"print('hello')"),
        ]);
        let result = extract_raw_tar_collecting(&tar_bytes).unwrap();
        assert_eq!(result.stats.file_count, 2);
        assert!(result.stats.total_size > 0);
        let names: Vec<&str> = result.files.iter().map(|(n, _)| n.as_str()).collect();
        assert!(names.contains(&"info/index.json"));
        assert!(names.contains(&"lib/foo.py"));
    }
}
