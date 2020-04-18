from PySide2.QtWidgets import QDialog
from UI.dialogs.success.success import Ui_Dialog


class SuccessDialog(QDialog):

    def __init__(self):
        super(SuccessDialog, self).__init__()

        # ui setup
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # close button
        self.ui.pushButton.clicked.connect(self.close_dialog)

    def close_dialog(self):
        self.close()
