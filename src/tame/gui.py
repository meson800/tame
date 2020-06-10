"""
This file provides the simple GUI implementation of the
built in Tame GUI.

Available under the MIT license.
Copyright (c) 2020 Christopher Johnstone
"""
from PySide2.QtWidgets import QApplication, QLabel

def main():
    """
    Starts the PyQt5 main loop.
    """
    app = QApplication([])
    label = QLabel('Hello World!')
    label.show()

    app.exec_()

if __name__ == "__main__":
    main()
