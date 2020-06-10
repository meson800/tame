"""
This file provides the simple GUI implementation of the
built in Tame GUI.

Available under the MIT license.
Copyright (c) 2020 Christopher Johnstone
"""
import wx

def main():
    """
    Starts the wxPython main loop.
    """
    app = wx.App()
    frame = wx.Frame(None, title='Hello World')
    frame.Show()

    app.MainLoop()

if __name__ == "__main__":
    main()
