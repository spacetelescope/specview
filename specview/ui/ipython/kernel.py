"""Start and IPython kernel"""
from IPython.qt.inprocess import QtInProcessKernelManager


def ipython_inprocess_kernel_start():
    # Create an in-process kernel
    # >>> print_process_id()
    # will print the same process ID as the main process
    kernel_manager = QtInProcessKernelManager()
    kernel_manager.start_kernel()
    kernel = kernel_manager.kernel
    kernel.gui = 'qt4'

    kernel_client = kernel_manager.client()
    kernel_client.start_channels()

    def stop():
        kernel_client.stop_channels()
        kernel_manager.shutdown_kernel()

    kernel_info = {
        'kernel': kernel,
        'manager': kernel_manager,
        'client':  kernel_client,
        'shutdown': stop
    }
    return kernel_info
