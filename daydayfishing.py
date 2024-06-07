# -*- coding: utf-8 -*-
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

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='log.md')

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception
PATH_APP = os.path.split(os.path.abspath(sys.argv[0]))[0]

PATH_CONFIG = "{}/config/config.ini".format(PATH_APP)
cf = configparser.ConfigParser(allow_no_value=True)

SETTINGS_TAG = "SETTINGS"
cf[SETTINGS_TAG] = {
    "POS_X": 640,
    "POS_Y": 1000,
    "SOFTWARE_WIDTH": 640,
    "SOFTWARE_HEIGHT": 60,
    "FONT_SIZE": 16,
    "PATH_READ": "",
    "ENCODING": "gbk"
}
cf.read(PATH_CONFIG, encoding="utf-8")

SOFTWARE_WIDTH = cf.getint(SETTINGS_TAG, "SOFTWARE_WIDTH")
SOFTWARE_HEIGHT = cf.getint(SETTINGS_TAG, "SOFTWARE_HEIGHT")

ENCODING = cf.get(SETTINGS_TAG, 'ENCODING').replace(" ", '')
FONT_SIZE = cf.getint(SETTINGS_TAG, "FONT_SIZE")
POS_X = cf.getint(SETTINGS_TAG, "POS_X")
POS_Y = cf.getint(SETTINGS_TAG, "POS_Y")
SAVE = cf.getint(SETTINGS_TAG, "SAVE")
WORD_NUM = cf.getint(SETTINGS_TAG, "WORD_NUM")
AUTO_READ_INTERVAL = cf.getfloat(SETTINGS_TAG, "AUTO_READ_INTERVAL")
TRANSPARENT = cf.getfloat(SETTINGS_TAG, "TRANSPARENT")
BAN_ADV = cf.get(SETTINGS_TAG, "BAN_ADV")
NEED_BAN_ADV = BAN_ADV is not None and len(BAN_ADV) > 0
PATH_READ = cf.get(SETTINGS_TAG, "PATH_READ")

if PATH_READ == "":
    PATH_READ = "{}/file/1.txt".format(PATH_APP)
cf.set(SETTINGS_TAG, "PATH_READ", PATH_READ)
with open(PATH_CONFIG, "w+", encoding='utf-8') as f:
    cf.write(f)

style_global = """
        *{
            font-family: "Microsoft YaHei";
            background:transparent;
            border-width:0;
            border-style:outset;
        }
        QTextBrowser{
            color: grey;
        }
    """


class DayDayFishing(object):

    def __init__(self, window) -> None:
        super().__init__()
        self.window = window
        self.txt = list()
        self.txt_len = 0
        self.now_line = SAVE
        self.last_pos = 0
        self.read_len = WORD_NUM
        self.now_pos = self.read_len
        self.read_finish = False
        self.back_to_last_page = False
        self.central_widget = None
        self.textBrowser = None
        self.ban_list = list()
        if NEED_BAN_ADV:
            self.ban_list = str(BAN_ADV).split("&&")
        logger.info(ENCODING)
        logger.info(PATH_READ)
        logger.info(PATH_CONFIG)

    # noinspection PyUnresolvedReferences
    def setup(self):
        self.window.setObjectName("day day fishing!!!")
        self.window.setFixedSize(SOFTWARE_WIDTH, SOFTWARE_HEIGHT)
        self.window.setStyleSheet(style_global)
        self.window.setAttribute(Qt.WA_TranslucentBackground)
        self.window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        self.central_widget = QtWidgets.QWidget(self.window)
        self.central_widget.setObjectName("central_widget")

        self.textBrowser = QtWidgets.QTextBrowser(self.central_widget)
        self.textBrowser.setGeometry(QtCore.QRect(0, 0, SOFTWARE_WIDTH, SOFTWARE_HEIGHT))
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setText("又是美好的一天~加油！")
        self.textBrowser.setStyleSheet("font-size:{}px".format(FONT_SIZE))
        self.window.setCentralWidget(self.central_widget)
        self.window.setWindowOpacity(TRANSPARENT)

        thread = self.KeyListenerThread(self)
        thread.breakSignal.connect(self.render_text)
        thread.start()

        self.read()
        self.init_position()
        QtCore.QMetaObject.connectSlotsByName(self.window)

    class KeyListenerThread(QThread):
        breakSignal = pyqtSignal(int)

        def __init__(self, p_win, parent=None):
            super().__init__(parent)
            self.p_win = p_win
            self.lock = False
            self.auto = False

        class AutoReadThread(QThread):

            def __init__(self, p_thread, parent=None):
                super().__init__(parent)
                self.p_thread = p_thread

            def run(self):
                while True:
                    try:
                        if self.p_thread.auto:
                            self.p_thread.next_page()
                    finally:
                        time.sleep(AUTO_READ_INTERVAL)

        def next_page(self):
            if not self.p_win.read_finish:
                self.p_win.textBrowser.setText('请等待加载')
                return
            if len(self.p_win.txt) <= 1:
                self.p_win.textBrowser.setText('先加载文件')
                return
            self.breakSignal.emit(1)

        def last_page(self):
            self.p_win.now_line = self.p_win.now_line - 1
            self.p_win.last_pos = 0
            self.p_win.now_pos = self.p_win.read_len
            self.p_win.back_to_last_page = True
            self.breakSignal.emit(1)

        def sponsor(self):
            QDesktopServices.openUrl(QUrl("https://gitee.com/Oops404/nas-guard/raw/"
                                          "master/%E6%AC%A2%E8%BF%8E%E6%94%AF%E6%8C%81.jpg"))

        def on_press(self, key):
            if key == Key.home:
                self.lock = not self.lock
            if self.lock:
                return
            if key == Key.end:
                QApplication.instance().quit()
                return
            key_str = str(key).replace("'", "")
            if key_str == 'a':
                self.auto = not self.auto
                # if self.auto:
                #     self.lock = self.auto
                return
            if key_str == 'x':
                self.p_win.window.setWindowOpacity(0.001)
                self.auto = False
                return
            if key_str == 'z':
                self.p_win.window.setWindowOpacity(TRANSPARENT)
                return
            if key_str == 'c':
                self.next_page()
                return
            if key_str == 'v':
                self.last_page()
                return
            if key_str == Key.ctrl_r:
                self.sponsor()
                return

        def run(self):
            auto_read_thread = self.AutoReadThread(self)
            auto_read_thread.start()
            with keyboard.Listener(on_press=self.on_press, on_release=None) as listener:
                listener.join()

    def init_position(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.window.geometry()
        if screen.width() >= POS_X > 0 and screen.height() >= POS_Y > 0:
            self.window.move(POS_X, POS_Y)
        else:
            self.window.move(int((screen.width() - size.width()) / 2), int(screen.height() - SOFTWARE_HEIGHT - 50))

    def replace_adv(self, line):
        for e in self.ban_list:
            line = line.replace(e, "")
        return line

    def read(self):
        if not os.path.exists(PATH_READ):
            QMessageBox(QMessageBox.Warning, "提示", "未找到文本文件").exec_()
            sys.exit()

        with open(PATH_READ, 'r', encoding=ENCODING, errors='ignore') as t:
            for line in t.readlines():
                if line == '\n' or line == '\r\n':
                    continue
                if NEED_BAN_ADV:
                    line = self.replace_adv(line)
                self.txt.append(line)
        self.txt_len = len(self.txt)
        self.read_finish = True

    def render_text(self):
        try:
            if self.now_line < 0:
                self.now_line = 0
            if self.now_line >= self.txt_len:
                self.textBrowser.setText('文本已完结，本程序由cheneyjin@outlook.com开发，感谢支持!')
                return
            text = self.txt[self.now_line][self.last_pos:self.now_pos]
            self.textBrowser.setText(text.lstrip())
            if len(text) < self.read_len:
                if self.back_to_last_page:
                    self.back_to_last_page = False
                    return
                self.now_line = self.now_line + 1
                self.last_pos = 0
                self.now_pos = self.read_len
            else:
                self.last_pos = self.now_pos
                self.now_pos = self.now_pos + self.read_len
        finally:
            cf.set(SETTINGS_TAG, "SAVE", str(self.now_line))
            with open(PATH_CONFIG, "w+") as fl:
                cf.write(fl)
