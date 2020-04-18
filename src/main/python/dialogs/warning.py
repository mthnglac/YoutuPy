from PySide2.QtWidgets import QDialog
from UI.dialogs.warning.warning import Ui_Dialog


class WarningDialog(QDialog):

    def __init__(self, message='Something is wrong!'):
        super(WarningDialog, self).__init__()

        # ui setup
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # label setup
        self.label = self.ui.label
        self.label.setText(message)

        # close button
        self.ui.pushButton.clicked.connect(self.close_dialog)

    def close_dialog(self):
        self.close()
