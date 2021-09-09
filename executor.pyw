# -*- coding: UTF-8-*-
"""
@Project: daydayfishing
@Author: X41822N
@Time: 2021/9/7 20:07
"""
import _thread
import configparser
import logging
import os
import sys
import time
import typing

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import *
from pynput import *
from pynput.keyboard import Key
from daydayfishing import DayDayFishing

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = DayDayFishing(mainWindow)
    ui.setup()
    mainWindow.show()
    sys.exit(app.exec_())
