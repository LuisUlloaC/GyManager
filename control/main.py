import os
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QShortcut, QApplication, QMainWindow, QFileDialog, QWidget, QListWidgetItem, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.Qt import QPixmap, QPainter, QImage, QColor, QGraphicsOpacityEffect, QPalette, QGraphicsBlurEffect
from .states import States
from data.models import Cliente
from django.core.files.uploadedfile import SimpleUploadedFile

#dev
from views.developer import DevDialog
from .validators import CIValidator, InputsValidator

class ClientListItem(QWidget):
    view_changed = pyqtSignal(int, str)
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
        return os.path.join(media_path, file)

    def handle_view_changed(self):
        self.view_changed.emit(2, self.client['ci'])

    def handle_delete_client(self):
        self.delete_client_signal.emit(self.client['ci'])
    

class Main(QMainWindow):
    def __init__(self, states):
        self.states = States(states.assets_path)
        self.assets_path = states.assets_path
        super(Main, self).__init__()
        uic.loadUi(self.get_assets("mainWindow.ui"), self)
        self.setWindowTitle("GyManager")
        self.editing_client_ci = 0
        self.creating_client_picture = None
        self.creating_client_edit_picture = None
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
        self.picture_edit.mousePressEvent = self.select_client_edit_picture
        self.accept_button.clicked.connect(self.create_client)
        self.decline_button.clicked.connect(self.goto_clients_list)
        self.decline_button_edit.clicked.connect(self.goto_clients_list)
        ci_string_validator = CIValidator(self.error_ci)
        nombre_number_validator = InputsValidator(self.error_nombre)
        primer_apellido_number_validator = InputsValidator(self.error_primer_apellido)
        segundo_apellido_number_validator = InputsValidator(self.error_segundo_apellido)
        ci_edit_string_validator = CIValidator(self.error_ci_edit)
        nombre_edit_number_validator = InputsValidator(self.error_nombre_edit)
        primer_edit_apellido_number_validator = InputsValidator(self.error_primer_apellido_edit)
        segundo_edit_apellido_number_validator = InputsValidator(self.error_segundo_apellido_edit)
        self.lineEdit_ci.setValidator(ci_string_validator)
        self.lineEdit_nombre.setValidator(nombre_number_validator)
        self.lineEdit_primer_apellido.setValidator(primer_apellido_number_validator)
        self.lineEdit_segundo_apellido.setValidator(segundo_apellido_number_validator)
        self.lineEdit_ci_edit.setValidator(ci_edit_string_validator)
        self.lineEdit_nombre_edit.setValidator(nombre_edit_number_validator)
        self.lineEdit_primer_apellido_edit.setValidator(primer_edit_apellido_number_validator)
        self.lineEdit_segundo_apellido_edit.setValidator(segundo_edit_apellido_number_validator)
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.edit_button.clicked.connect(self.save_updated_client)
        self.setBackgroundBlur()
        self.setCardBlur()


    def setBackgroundBlur(self):
        background_path = self.get_media("views/ui/assets/background.svg").replace("\\","/")
        self.setStyleSheet("""
                           QMainWindow {
                            background-image:""" f'url({background_path})'""";
                            background-color: rgb(53, 53, 53);
                            background-repeat: no-repeat;
                            background-position: center;  
                           }
                           
                            QPushButton {
                                background-color: rgb(53, 53, 53);
                                color: rgb(255,170,0);
                                border-radius: 12px;
                            }

                            QLabel {
                                color:rgb(255,170,0);
                            }


                            """)
        self.background_widget = QWidget(self)
        self.background_widget.setGeometry(self.rect())
        self.background_widget.lower() 
        self.background_widget.setAutoFillBackground(True)
        palette = self.background_widget.palette()
        palette.setColor(QPalette.Background, QColor(53,53,53,110))
        self.background_widget.setPalette(palette)
        self.background_widget.lower()
        effect = QGraphicsBlurEffect()
        effect.setBlurRadius(1)
        effect.setBlurHints(QGraphicsBlurEffect.QualityHint)
        self.background_widget.setGraphicsEffect(effect)

    def setCardBlur(self):
        self.frame_10.setAutoFillBackground(True)
        palette = self.frame_10.palette()
        palette.setColor(QPalette.Background, QColor(53,53,53,200))
        self.frame_10.setPalette(palette)
        self.frame_10.lower()
        effect = QGraphicsBlurEffect()
        effect.setBlurRadius(1)
        effect.setBlurHints(QGraphicsBlurEffect.QualityHint)
        self.frame_10.setGraphicsEffect(effect)
        self.frame_7.setAutoFillBackground(True)
        palette = self.frame_7.palette()
        palette.setColor(QPalette.Background, QColor(53,53,53,200))
        self.frame_7.setPalette(palette)
        self.frame_7.lower()
        effect = QGraphicsBlurEffect()
        effect.setBlurRadius(1)
        effect.setBlurHints(QGraphicsBlurEffect.QualityHint)
        self.frame_7.setGraphicsEffect(effect)
        
    def resizeEvent(self, event):
       self.background_widget.setGeometry(self.rect())
       super().resizeEvent(event)
        
    def get_assets(self, file):
        return os.path.join(self.assets_path, file)

    def get_media(self, file):
        media_path = os.getcwd()
        media_path = media_path.replace("\\", "/")
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
                self.picture.setStyleSheet("""
                                              border-image:""" f'url({filename})'
                                              """0 0 0 0;
                                             """)

    def select_client_edit_picture(self, event):
        if event.button() == Qt.LeftButton:
            filename, _ = QFileDialog.getOpenFileName(self, "Choose Image")
            if filename:
                self.creating_client_edit_picture = filename
                self.picture_edit.setStyleSheet("""
                                              border-image:""" f'url({filename})'
                                              """0 0 0 0;
                                             """)
        
    
    def create_client(self):
        is_valid = True

        if not self.lineEdit_ci_edit.hasAcceptableInput() and not \
            self.lineEdit_nombre_edit.hasAcceptableInput() and not \
            self.lineEdit_primer_apellido_edit.hasAcceptableInput() and not \
            self.lineEdit_segundo_apellido_edit.hasAcceptableInput() and self.creating_client_picture == None or \
            len(self.creating_client_picture) != 0:
            
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

    def set_client_values_to_edit(self, ci_value):
        self.editing_client_ci = ci_value
        client = Cliente.objects.get(ci=ci_value)
        self.lineEdit_ci_edit.setText(client.ci)
        self.lineEdit_nombre_edit.setText(client.nombre)
        self.lineEdit_primer_apellido_edit.setText(client.primer_apellido)
        self.lineEdit_segundo_apellido_edit.setText(client.segundo_apellido)
        self.tipo_entrenamiento_edit.setCurrentText(client.tipo_entrenamiento)
        self.picture_edit.clear()
        picture_path = client.foto.url[1:]
        picture_path = self.get_media(picture_path).replace("\\", "/")
        self.picture_edit.setStyleSheet("""
                                              border-image:""" f'url({picture_path})'
                                              """0 0 0 0;
                                             """)

    def save_updated_client(self):
        client = Cliente.objects.get(ci=self.editing_client_ci)
        if not self.lineEdit_ci_edit.hasAcceptableInput() and not \
            self.lineEdit_nombre_edit.hasAcceptableInput() and not \
            self.lineEdit_primer_apellido_edit.hasAcceptableInput() and not \
            self.lineEdit_segundo_apellido_edit.hasAcceptableInput() and self.creating_client_edit_picture == None or \
            len(self.creating_client_edit_picture) != 0:
            with open(self.creating_client_edit_picture, 'rb') as picture:
                uploaded_file = SimpleUploadedFile(picture.name, picture.read(), content_type='image/jpeg')
                client.ci = self.lineEdit_ci_edit.text()
                client.nombre = self.lineEdit_nombre_edit.text()
                client.primer_apellido = self.lineEdit_primer_apellido_edit.text()
                client.segundo_apellido = self.lineEdit_segundo_apellido_edit.text()
                client.tipo_entrenamiento = self.tipo_entrenamiento_edit.currentText()
                client.foto = uploaded_file
            client.save()
            self.goto_clients_list()
            self.update_client_list()

    def delete_client(self, value):
        try:
            client = Cliente.objects.get(ci=value)
            client.delete()
            self.update_client_list()
        except Cliente.DoesNotExist:
            print("Client not found")
        except Exception as err:
            print(f'An error occurred: {err}')

    def handle_view_changed(self, index, ci_value):
       self.states.views['clients_view'] = index
       self.clients_switch_screen.setCurrentIndex(self.states.views['clients_view'])
       self.set_client_values_to_edit(ci_value)

    def update_client_list(self):
        self.states.reload_client_list()
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


# cambiar ui del la card 