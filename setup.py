import sys
from cx_Freeze import setup, Executable


import os

os.environ['TCL_LIBRARY'] = "C:\\Anaconda3\\tcl\\tcl8.6"
os.environ['TK_LIBRARY'] = "C:\\Anaconda3\\tcl\\tk8.6"


base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
        Executable("main.py", base = base, targetName="KuKuLogAnalyzer.exe")
    ]

buildOptions = dict(
    includes = ["pyqtgraph", "numpy"],
    include_files = ["event", "MainUI.ui", "WaitDlg.ui"],
)

setup(
    name = "KuKuLogAnalyzer",
    version = "0.1",
    description = "Analyzer logs and show time graph",
    options = dict(build_exe = buildOptions),
    executables = executables
)