import os
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QShortcut, QApplication, QMainWindow, QFileDialog, QWidget, QListWidgetItem, QListWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.Qt import QPixmap
from .states import States
from data.models import Cliente
from django.core.files.uploadedfile import SimpleUploadedFile

#dev
from views.developer import DevDialog
from .validators import CIValidator, InputsValidator

class ClientListItem(QWidget):
    view_changed = pyqtSignal(int)
    delete_client_signal = pyqtSignal(str)

    def __init__(self, client, assets_path):
        self.assets_path = assets_path
        super(ClientListItem, self).__init__()
        uic.loadUi(self.get_assets("client_card_item.ui"), self)
        self.client = client
        picture_path = self.client['foto'].url[1:]
        picture_path = self.get_media(picture_path).replace("\\", "/")
        self.list_item_picture.setStyleSheet("""
                                              border-image:""" f'url({picture_path})'
                                              """0 0 0 0;
                                             """)
        self.name.setText(f'{self.client["nombre"]} {self.client["primer_apellido"]} {self.client["segundo_apellido"]}')
        self.training_type.setText(f'{self.client["tipo_entrenamiento"]}')
        self.date_joined.setText(f'{self.client["fecha_ingreso"]}')
        if self.client["ultimo_pago"] == None:
            self.last_pay.setText(f'-')
        else:
            self.last_pay.setText(f'{self.client["ultimo_pago"]}')
        self.edit_button.clicked.connect(self.handle_view_changed)
        self.delete_button.clicked.connect(self.handle_delete_client)


    def get_assets(self, file):
        return os.path.join(self.assets_path, file)
    
    def get_media(self, file):
        media_path = os.getcwd()
        media_path = media_path.replace("\\", "/")
        print('La ruta: '+ os.path.join(media_path, file))
        return os.path.join(media_path, file)

    def handle_view_changed(self):
        self.view_changed.emit(2)

    def handle_delete_client(self):
        self.delete_client_signal.emit(self.client['ci'])

    def edit_client(self):
        pass

    

class Main(QMainWindow):
    def __init__(self, states):
        self.states = States(states.assets_path)
        self.assets_path = states.assets_path
        super(Main, self).__init__()
        uic.loadUi(self.get_assets("mainWindow.ui"), self)
        self.setWindowTitle("GyManager")
        self.creating_client_picture = None
        self.error_ci.hide()
        self.error_nombre.hide()
        self.error_primer_apellido.hide()
        self.error_segundo_apellido.hide()
        self.error_ci_edit.hide()
        self.error_nombre_edit.hide()
        self.error_primer_apellido_edit.hide()
        self.error_segundo_apellido_edit.hide()
        self.date.setText(self.states.data['currentDate'].toString("dd/MM/yyyy"))
        self.home_button.clicked.connect(self.goto_home)
        self.clients_button.clicked.connect(self.goto_clients)
        self.close_sidebar_button.clicked.connect(self.close)
        self.add_client_button.clicked.connect(self.goto_client_creation_form)
        self.picture.mousePressEvent = self.select_client_picture
        self.accept_button.clicked.connect(self.create_client)
        self.decline_button.clicked.connect(self.goto_clients_list)
        ci_string_validator = CIValidator(self.error_ci)
        nombre_number_validator = InputsValidator(self.error_nombre)
        primer_apellido_number_validator = InputsValidator(self.error_primer_apellido)
        segundo_apellido_number_validator = InputsValidator(self.error_segundo_apellido)
        ci_edit_string_validator = CIValidator(self.error_ci)
        nombre_edit_number_validator = InputsValidator(self.error_nombre)
        primer_edit_apellido_number_validator = InputsValidator(self.error_primer_apellido)
        segundo_edit_apellido_number_validator = InputsValidator(self.error_segundo_apellido)
        self.lineEdit_ci.setValidator(ci_string_validator)
        self.lineEdit_nombre.setValidator(nombre_number_validator)
        self.lineEdit_primer_apellido.setValidator(primer_apellido_number_validator)
        self.lineEdit_segundo_apellido.setValidator(segundo_apellido_number_validator)
        self.lineEdit_ci_edit.setValidator(ci_edit_string_validator)
        self.lineEdit_nombre_edit.setValidator(nombre_edit_number_validator)
        self.lineEdit_primer_apellido_edit.setValidator(primer_edit_apellido_number_validator)
        self.lineEdit_segundo_apellido_edit.setValidator(segundo_edit_apellido_number_validator)
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
    def get_assets(self, file):
        return os.path.join(self.assets_path, file)

    def get_media(self, file):
        media_path = os.path.join(self.assets_path, "assets/")
        return os.path.join(media_path, file)
    
    def goto_home(self):
        self.states.views['main_view']=0
        self.switch_screen.setCurrentIndex(self.states.views['main_view'])

    def goto_clients(self):
        self.update_client_list()
        self.states.views['main_view']=1
        self.states.views['clients_view']=0
        self.switch_screen.setCurrentIndex(self.states.views['main_view'])
        self.clients_switch_screen.setCurrentIndex(self.states.views['clients_view'])

    def goto_clients_list(self):
        self.update_client_list()
        self.states.views['clients_view']=0
        self.clients_switch_screen.setCurrentIndex(self.states.views['clients_view'])

    def goto_client_creation_form(self):
        self.states.views['clients_view']=1
        self.clients_switch_screen.setCurrentIndex(self.states.views['clients_view'])
    
    def select_client_picture(self, event):
        if event.button() == Qt.LeftButton:
            filename, _ = QFileDialog.getOpenFileName(self, "Choose Image")
            if filename:
                self.creating_client_picture = filename
                pixmap = QPixmap(filename)
                pixmap = pixmap.scaled(self.picture.size(), Qt.KeepAspectRatio)
                self.picture.setPixmap(pixmap)
        
    
    def create_client(self):
        is_valid = True

        if not self.lineEdit_ci.hasAcceptableInput() and not \
            self.lineEdit_nombre.hasAcceptableInput() and not \
            self.lineEdit_primer_apellido.hasAcceptableInput() and not \
            self.lineEdit_segundo_apellido.hasAcceptableInput() and len(self.creating_client_picture) != 0:
            
            for client in self.states.data['client_list']:
                if self.lineEdit_ci.text() == client['ci']:
                    is_valid = False
                    break

            if is_valid:
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
                self.goto_clients_list()
            else:
                self.error_ci.setText('Ya existe un cliente con ese carné de identidad')
                self.error_ci.show()

    def edit_client(self):
        self.lineEdit_ci_edit.setText('123123123')

        if not self.lineEdit_ci_edit.hasAcceptableInput() and not \
            self.lineEdit_nombre_edit.hasAcceptableInput() and not \
            self.lineEdit_primer_apellido_edit.hasAcceptableInput() and not \
            self.lineEdit_segundo_apellido_edit.hasAcceptableInput() and len(self.creating_client_picture) != 0:

            with open(self.creating_client_picture, 'rb') as picture:
                uploaded_file = SimpleUploadedFile(picture.name, picture.read(), content_type='image/jpeg')
                Cliente.objects.create(
                    ci = self.lineEdit_ci_edit.text(),
                    nombre = self.lineEdit_nombre_edit.text(),
                    primer_apellido = self.lineEdit_primer_apellido_edit.text(),
                    segundo_apellido = self.lineEdit_segundo_apellido_edit.text(),
                    tipo_entrenamiento = self.tipo_entrenamiento_edit.currentText(),
                    foto = uploaded_file,
                )
            self.goto_clients_list()

    def delete_client(self, value):
        try:
            client = Cliente.objects.get(ci=value)
            client.delete()
            self.states.reload_client_list()
            self.update_client_list()
        except Cliente.DoesNotExist:
            print("Client not found")
        except Exception as err:
            print(f'An error occurred: {err}')


    def handle_view_changed(self, value):
       self.states.views['clients_view'] = value
       self.clients_switch_screen.setCurrentIndex(self.states.views['clients_view'])

    def update_client_list(self):
        self.listWidget.clear()
        for client in self.states.data['client_list']:
            item_widget = ClientListItem(client, self.assets_path)
            item_widget.view_changed.connect(self.handle_view_changed)
            item_widget.delete_client_signal.connect(self.delete_client)
            list_item = QListWidgetItem(self.listWidget)
            list_item.setSizeHint(item_widget.sizeHint())
            self.listWidget.setItemWidget(list_item, item_widget)



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