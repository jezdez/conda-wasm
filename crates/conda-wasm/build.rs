/// Build script for conda-wasm: optionally embeds a lockfile, target platform,
/// and Emscripten SDK version into the WASM binary so JS consumers don't
/// need to pass them at runtime.
///
/// Set `CONDA_WASM_LOCKFILE=/path/to/conda-wasm.lock`, `CONDA_WASM_PLATFORM=emscripten-wasm32`,
/// and `CONDA_WASM_EMSCRIPTEN_VERSION=3.1.58` at build time to bake them in.
fn main() {
    println!("cargo::rustc-check-cfg=cfg(conda_wasm_embedded_lockfile)");
    println!("cargo::rustc-check-cfg=cfg(conda_wasm_embedded_platform)");
    println!("cargo::rustc-check-cfg=cfg(conda_wasm_embedded_emscripten_version)");
    println!("cargo:rerun-if-env-changed=CONDA_WASM_LOCKFILE");
    println!("cargo:rerun-if-env-changed=CONDA_WASM_PLATFORM");
    println!("cargo:rerun-if-env-changed=CONDA_WASM_EMSCRIPTEN_VERSION");

    let out_dir = std::env::var("OUT_DIR").unwrap();
    let out_path = std::path::Path::new(&out_dir);

    if let Ok(path) = std::env::var("CONDA_WASM_LOCKFILE")
        && !path.is_empty()
    {
        let lockfile_path = std::path::Path::new(&path);
        let lockfile_path = if lockfile_path.is_absolute() {
            lockfile_path.to_path_buf()
        } else {
            let manifest_dir = std::env::var("CARGO_MANIFEST_DIR").unwrap();
            std::path::Path::new(&manifest_dir).join(lockfile_path)
        };
        println!("cargo:rerun-if-changed={}", lockfile_path.display());
        let dest = out_path.join("embedded_lockfile.txt");
        std::fs::copy(&lockfile_path, &dest).unwrap_or_else(|e| {
            panic!(
                "conda-wasm: failed to copy CONDA_WASM_LOCKFILE '{}': {e}",
                lockfile_path.display()
            )
        });
        println!("cargo:rustc-cfg=conda_wasm_embedded_lockfile");
        eprintln!(
            "conda-wasm: embedding lockfile from {}",
            lockfile_path.display()
        );
    }

    if let Ok(platform) = std::env::var("CONDA_WASM_PLATFORM")
        && !platform.is_empty()
    {
        let dest = out_path.join("embedded_platform.txt");
        std::fs::write(&dest, &platform)
            .unwrap_or_else(|e| panic!("conda-wasm: failed to write embedded platform: {e}"));
        println!("cargo:rustc-cfg=conda_wasm_embedded_platform");
        eprintln!("conda-wasm: embedding platform '{platform}'");
    }

    if let Ok(version) = std::env::var("CONDA_WASM_EMSCRIPTEN_VERSION")
        && !version.is_empty()
    {
        let dest = out_path.join("embedded_emscripten_version.txt");
        std::fs::write(&dest, &version).unwrap_or_else(|e| {
            panic!("conda-wasm: failed to write embedded emscripten version: {e}")
        });
        println!("cargo:rustc-cfg=conda_wasm_embedded_emscripten_version");
        eprintln!("conda-wasm: embedding emscripten version '{version}'");
    }
}
