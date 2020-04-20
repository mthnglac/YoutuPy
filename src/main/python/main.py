from fbs_runtime.application_context.PySide2 import ApplicationContext
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide2.QtCore import QThreadPool, QRegExp, QUrl, Slot
from PySide2.QtGui import QRegExpValidator
from PySide2.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply
from youtube_dl import YoutubeDL
import sys
from UI.gui import Ui_MainWindow

from dialogs.success import SuccessDialog
from dialogs.warning import WarningDialog
from threads.worker import MyWorker
from utils.utils import verify_url, verify_spelling
from conf import settings


class MyMainWindow(QMainWindow):

    def __init__(self):
        super(MyMainWindow, self).__init__()

        # ui setup
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # check network setup
        self.net_manager = QNetworkAccessManager()
        self.test_url = QUrl("https://www.google.com/")
        self.test_req = QNetworkRequest(self.test_url)
        self.test_res = self.net_manager.get(self.test_req)
        # self.test_res.finished.connect(self.processRes)
        # noinspection All
        self.test_res.error.connect(self.processErr)
        self.test_msg = QMessageBox()

        # Thread setup
        self.pool = QThreadPool()

        # progress bar setup
        self.progress_bar = self.ui.progressBar

        # addURL line setup
        self.line_addURL = self.ui.lineEdit
        self.line_addURL.setValidator(QRegExpValidator(QRegExp(settings.regex_for_youtube_url)))
        # addURL button setup
        self.button_addURL = self.ui.pushButton_2
        self.button_addURL.clicked.connect(self.paste_to_url_line)

        # browse line setup
        self.line_browse = self.ui.lineEdit_2
        # browse button setup
        self.button_browse = self.ui.pushButton_4
        self.button_browse.clicked.connect(self.choose_path_and_set_line)

        # download button setup
        self.button_download = self.ui.pushButton_3
        self.button_download.setDisabled(True)
        self.button_download.clicked.connect(self.run)

    def paste_to_url_line(self):
        text = QApplication.clipboard().text()
        if verify_spelling(text):
            self.line_addURL.setText(text)
        else:
            self.warning_dialog(message='Please copy a valid URL!')
        return

    def choose_path_and_set_line(self):
        path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.line_browse.setText(path)
        if not self.button_download.isEnabled():
            self.button_download.setDisabled(False)
        return path

    def get_url_line(self):
        url = self.line_addURL.text()
        if verify_url(url):
            return url

    def get_browse_line(self):
        path = self.line_browse.text()
        return path

    def get_save_location(self):
        path = self.get_browse_line()
        return path + '/' + '%(title)s.%(ext)s'

    def launch_thread_pool(self, process, progress_fn, on_complete, on_not_complete):
        """Execute a function in the background with a worker"""
        worker = MyWorker(fn=process)
        self.pool.start(worker)
        worker.emitter.progress.connect(progress_fn)
        worker.emitter.finished.connect(on_complete)
        worker.emitter.unfinished.connect(on_not_complete)
        return

    def progress_fn(self, percentage):
        """Update progress"""
        self.progress_bar.setValue(percentage)
        return

    def run(self):
        """call process"""

        if not self.line_addURL.isModified() and len(self.line_addURL.text()) == 0:
            self.warning_dialog(message='Please enter URL!')
        else:
            # disabling components
            self.disable_components()
            self.button_download.setText('Downloading')
            # running thread
            return self.launch_thread_pool(
                self.download_mp3, self.progress_fn, self.success_dialog, self.warning_dialog)

    def download_mp3(self, progress_callback):
        """Do some process here"""

        class YdlLogger(object):
            @staticmethod
            def debug(msg):
                with open(settings.DEBUG, "w") as text_file:
                    print(f"DEBUG: {msg}", file=text_file)

            @staticmethod
            def warning(msg):
                with open(settings.WARNINGS, "w") as text_file:
                    print(f"WARNING: {msg}", file=text_file)

            @staticmethod
            def error(msg):
                with open(settings.ERRORS, "w") as text_file:
                    print(f"ERROR: {msg}", file=text_file)

        def hook_ydl(d):
            for i, j in d.items():
                if i == '_percent_str':
                    a = j.split('%')[0]
                    new_value = int(float(a))
                    progress_callback.emit(new_value)

        ydl_opts = {
            'format': 'bestaudio/best',  # the format that it can be
            # 'logger': YdlLogger(),  # this is used to log errors and such
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'FFmpegMetadata'
                },
            ],
            'noplaylist': 'true',  # that if the link is in a youtube playlist it wont download the whole playlist
            'progress_hooks': [hook_ydl],
            'outtmpl': self.get_save_location(),  # output location and name
            # 'ignoreerrors': 'true',  # if error move one
            # 'restrictfilenames': 'true'  # gets rid of spaces in output name
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.get_url_line()])
            return
        except Exception as e:
            return e

    def success_dialog(self):
        self.disable_components()

        dialog = SuccessDialog()
        dialog.show()
        dialog.exec_()

        # reset components
        self.enable_components()

    def warning_dialog(self, message):
        self.disable_components()

        dialog = WarningDialog(message)
        dialog.show()
        dialog.exec_()

        # reset components
        self.enable_components()

    def disable_components(self):
        self.button_download.setDisabled(True)
        self.button_browse.setDisabled(True)
        self.button_addURL.setDisabled(True)
        self.line_browse.setDisabled(True)
        self.line_addURL.setDisabled(True)

    def enable_components(self):
        self.button_download.setDisabled(False)
        self.button_browse.setDisabled(False)
        self.button_addURL.setDisabled(False)
        self.line_browse.setDisabled(False)
        self.line_addURL.setDisabled(False)
        self.button_download.setText('Download')
        self.progress_bar.setValue(0)

    # noinspection All
    @Slot()
    def processRes(self):
        if self.test_res.bytesAvailable():
            self.test_msg.information(self, "Info", "You arre connected to the Internet.")
        self.test_res.deleteLater()

    # noinspection All
    @Slot(QNetworkReply.NetworkError)
    def processErr(self, code):
        self.test_msg.critical(None, "Info", "You are not connected to the Internet")
        # print(code)


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = MyMainWindow()
    # window.resize(350, 250)
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
