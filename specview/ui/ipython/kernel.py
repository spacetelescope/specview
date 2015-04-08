"""Start an IPython kernel"""
from IPython import get_ipython
from IPython.qt.client import QtKernelClient
from IPython.qt.inprocess import QtInProcessKernelManager
from IPython.kernel.connect import get_connection_file
from IPython.kernel.inprocess.ipkernel import InProcessInteractiveShell


def ipython_kernel_start(**kwargs):
    shell = get_ipython()
    if shell is None or isinstance(shell, InProcessInteractiveShell):
        kernel_info = in_process_kernel(**kwargs)
    else:
        kernel_info = connected_kernel(**kwargs)

    return kernel_info


def in_process_kernel(**kwargs):
    """Connect to an in-process Kernel

    This only works on IPython v 0.13 and above

    Parameters
    ----------
    kwargs : Extra variables to put into the namespace
    """

    kernel_info = {}
    kernel_info['manager'] = QtInProcessKernelManager()
    kernel_info['manager'].start_kernel()

    kernel = kernel_info['manager'].kernel
    kernel.gui = 'qt4'

    kernel_info['client'] = kernel_info['manager'].client()
    kernel_info['client'].start_channels()
    kernel_info['shell'] = kernel.shell

    return kernel_info


def connected_kernel(**kwargs):
    """Connect to another kernel running in
       the current process

    This only works on IPython v1.0 and above

    Parameters
    ----------
    kwargs : Extra variables to put into the namespace
    """
    kernel_info = {}

    shell = get_ipython()
    if shell is None:
        raise RuntimeError("There is no IPython kernel in this process")

    try:
        client = QtKernelClient(connection_file=get_connection_file())
        client.load_connection_file()
        client.start_channels()
        kernel_info['client'] = client
    except Exception:
        print ('Detected running from an ipython interpreter.\n'
               'The GUI console will be disabled.')
        kernel_info['client'] = None
        pass
    kernel_info['shell'] = shell

    return kernel_info
