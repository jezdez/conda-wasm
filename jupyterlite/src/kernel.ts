import { WebWorkerKernel } from '@jupyterlite/xeus';
import type { KernelMessage } from '@jupyterlab/services';

const CONDA_RE = /^([%!]?)conda\s+(\w+)/gm;

/**
 * Kernel subclass that rewrites `%conda` / `!conda` / bare `conda`
 * commands to `%conda_wasm` before the message reaches the
 * WebWorker. This prevents mambajs's `processMagics` from intercepting
 * the command, letting it pass through to Python where real conda
 * (via the conda-wasm Python package and WASM runtime) handles it.
 */
export class CondaWasmWebWorkerKernel extends WebWorkerKernel {
  async handleMessage(msg: KernelMessage.IMessage): Promise<void> {
    if (msg.header.msg_type === 'execute_request') {
      const content = msg.content as KernelMessage.IExecuteRequestMsg['content'];
      content.code = content.code.replace(CONDA_RE, '%conda_wasm $2');
    }
    await super.handleMessage(msg);
  }
}
