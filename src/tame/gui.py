"""
This file provides the simple GUI implementation of the
built in Tame GUI.

Available under the MIT license.
Copyright (c) 2020 Christopher Johnstone
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

def main():
    """
    Starts the PyQT main loop.
    """
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.show()

    app.exec_()

if __name__ == "__main__":
    main()
