import os
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QShortcut, QApplication, QMainWindow, QLabel, QFileDialog
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.Qt import QPixmap
from .states import States
from data.models import Cliente
from django.core.files.uploadedfile import SimpleUploadedFile

#dev
from views.developer import DevDialog

class NumberValidator(QtGui.QValidator):
   def __init__(self, label):
       super().__init__()
       self.label = label

   def validate(self, string, position):
        if QtCore.QRegExp('.*[0-9].*').exactMatch(string):
            self.label.setText("Number detected: " + string)
            self.label.show()
            return QtGui.QValidator.Acceptable, string, position
        self.label.hide()
        return QtGui.QValidator.Intermediate, string, position

class Main(QMainWindow):
    def __init__(self, states):
        self.states = states
        self.assets_path = self.states.assets_path
        super(Main, self).__init__()
        uic.loadUi(self.get_assets("mainWindow.ui"), self)
        self.setWindowTitle("GyManager")
        self.creating_client_picture = None
        self.error_ci.hide()
        self.error_nombre.hide()
        self.error_primer_apellido.hide()
        self.error_segundo_apellido.hide()
        self.date.setText(self.states.data['currentDate'].toString("dd/MM/yyyy"))
        self.home_button.clicked.connect(self.goto_home)
        self.clients_button.clicked.connect(self.goto_clients)
        self.close_sidebar_button.clicked.connect(self.close)
        self.add_client_button.clicked.connect(self.goto_client_creation_form)
        self.picture.mousePressEvent = self.select_client_picture
        self.accept_button.clicked.connect(self.create_client)
        nombre_number_validator = NumberValidator(self.error_nombre)
        primer_apellido_number_validator = NumberValidator(self.error_primer_apellido)
        segundo_apellido_number_validator = NumberValidator(self.error_segundo_apellido)
        self.lineEdit_nombre.setValidator(nombre_number_validator)
        self.lineEdit_primer_apellido.setValidator(primer_apellido_number_validator)
        self.lineEdit_segundo_apellido.setValidator(segundo_apellido_number_validator)



    def get_assets(self, file):
        return os.path.join(self.assets_path, file)

    def get_media(self, file):
        media_path = os.path.join(self.assets_path, "assets/")
        return os.path.join(media_path, file)
    
    def goto_home(self):
        self.switch_screen.setCurrentIndex(0)

    def goto_clients(self):
        self.switch_screen.setCurrentIndex(1)
    
    def goto_client_creation_form(self):
        self.clients_switch_screen.setCurrentIndex(1)
    
    def select_client_picture(self, event):
        if event.button() == Qt.LeftButton:
            filename, _ = QFileDialog.getOpenFileName(self, "Choose Image")
            if filename:
                self.creating_client_picture = filename
                pixmap = QPixmap(filename)
                pixmap = pixmap.scaled(self.picture.size(), Qt.KeepAspectRatio)
                self.picture.setPixmap(pixmap)
        
    
    def create_client(self):
        if self.lineEdit_ci:
            print('vacio')
        with open(self.creating_client_picture, 'rb') as picture:
            uploaded_file = SimpleUploadedFile(picture.name, picture.read(), content_type='image/jpeg')
            Cliente.objects.create(
                ci = self.lineEdit_ci.text(),
                nombre = self.lineEdit_nombre.text(),
                primer_apellido = self.lineEdit_primer_apellido.text(),
                segundo_apellido = self.lineEdit_segundo_apellido.text(),
                tipo_entrenamiento = self.tipo_entrenamiento.currentText(),
                foto = uploaded_file,
            )



def start_app(assets_path, debug=False):
    app = QApplication(sys.argv)
    states = States(assets_path)


    if debug:
        dev = DevDialog(states)
        stdout = sys.stdout
        print("stdout -> dev window")
        sys.stdout = dev
        print("stdout -> dev window")
        app.dev = dev
        return app

    mainWin = Main(states)
    states.views["mainWin"] = mainWin

    def callback():
        dev = DevDialog(states)
        stdout = sys.stdout
        print("stdout -> dev window")
        sys.stdout = dev
        print("stdout -> dev window")
        dev.context = dev_shortcut.parent()
        dev.exec()
        sys.stdout = stdout
        print("stdout -> sys.stdout")


    dev_shortcut = QShortcut("Ctrl+Alt+D", mainWin)
    states.dev_shortcut = dev_shortcut
    dev_shortcut.setContext(Qt.ApplicationShortcut)
    dev_shortcut.activated.connect(callback)

    @app.focusChanged.connect
    def change(old, new):
        if new:
            if not isinstance(new.window(), DevDialog):
                dev_shortcut.setParent(new.window())

    mainWin.showMaximized()
    sys.exit(app.exec_())