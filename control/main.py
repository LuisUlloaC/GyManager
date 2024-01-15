from datetime import date
import os
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QShortcut, QApplication, QMainWindow, QFileDialog, QWidget, QListWidgetItem, QLabel, QListWidget, QToolBox, QDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.Qt import QColor, QPalette, QGraphicsBlurEffect, QIcon, QPixmap
from .states import States
from data.models import Cliente, BackgroundImage
from django.core.files.uploadedfile import SimpleUploadedFile

#dev
from views.developer import DevDialog
from .validators import CIValidator, InputsValidator, TelefonoValidator


class ClientListItem(QWidget):
    view_changed = pyqtSignal(int, str)
    delete_client_signal = pyqtSignal(str)

    def __init__(self, client, assets_path):
        self.assets_path = assets_path
        super(ClientListItem, self).__init__()
        uic.loadUi(self.get_assets("client_card_item.ui"), self)
        self.client = client
        picture_path = self.client['foto'].url[1:]
        print(picture_path+'   aaaaaaaaaa')
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
        self.phone_number.setText(f'{self.client["numero_de_telefono"]}')
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


class DeudorListItem(QWidget):
    marcar_notificado_signal = pyqtSignal(bool, str)
    cobrar_deuda_signal = pyqtSignal(str)
    def __init__(self, client, assets_path):
        self.assets_path = assets_path
        super(DeudorListItem, self).__init__()
        uic.loadUi(self.get_assets("deudor_card_item.ui"), self)
        self.notificado.setStyleSheet("""
                                        QCheckBox::indicator {
                                                background-color: rgb(53,53,53);
                                                border-style:solid;
                                                border-width:1px;
                                                border-color: rgb(255,170,0);
                                                border-radius:5px;
                                        }
                                        QCheckBox::indicator:checked {
                                            background-color: rgb(255,170,0);
                                        }

                                        """)
        self.client = client
        picture_path = self.client['foto'].url[1:]
        picture_path = self.get_media(picture_path).replace("\\", "/")
        self.list_item_picture.setStyleSheet("""
                                              border-image:""" f'url({picture_path})'
                                              """0 0 0 0;
                                             """)
        self.notificado.setChecked(self.client["notificado"])
        self.name_deudor.setText(f'{self.client["nombre"]} {self.client["primer_apellido"]} {self.client["segundo_apellido"]}')
        self.training_type_deudor.setText(f'{self.client["tipo_entrenamiento"]}')
        self.phone_number_deudor.setText(f'{self.client["numero_de_telefono"]}')
        if self.client["ultimo_pago"] == None:
            self.last_pay_deudor.setText(f'-')
        else:
            self.last_pay_deudor.setText(f'{self.client["ultimo_pago"]}')
        self.cobrar_button.clicked.connect(self.handle_cobrar)
        self.notificado.stateChanged.connect(self.handle_notificar)


    def get_assets(self, file):
        return os.path.join(self.assets_path, file)
    
    def get_media(self, file):
        media_path = os.getcwd()
        media_path = media_path.replace("\\", "/")
        return os.path.join(media_path, file)
    
    def handle_cobrar(self):
        self.cobrar_deuda_signal.emit(self.client['ci'])

    def handle_notificar(self):
        self.marcar_notificado_signal.emit(self.notificado.isChecked(), self.client['ci'])

    

class Main(QMainWindow):
    def __init__(self, states, credentials):
        self.states = States(states.assets_path)
        self.assets_path = states.assets_path
        self.credentials = credentials
        super(Main, self).__init__()
        uic.loadUi(self.get_assets("mainWindow.ui"), self)
        self.setWindowTitle("GyManager")
        self.editing_client_ci = 0
        self.creating_client_picture = None
        self.creating_client_edit_picture = None
        self.error_ci.hide()
        self.error_telefono.hide()
        self.error_nombre.hide()
        self.error_primer_apellido.hide()
        self.error_segundo_apellido.hide()
        #edit
        self.error_ci_edit.hide()
        self.error_telefono_edit.hide()
        self.error_nombre_edit.hide()
        self.error_primer_apellido_edit.hide()
        self.error_segundo_apellido_edit.hide()
        #admin
        self.error_ci_admin.hide()
        self.error_telefono_admin.hide()
        self.error_nombre_admin.hide()
        self.error_primer_apellido_admin.hide()
        self.error_segundo_apellido_admin.hide()

        #admin
        self.error_ci_admin_edit.hide()
        self.error_telefono_admin_edit.hide()
        self.error_nombre_admin_edit.hide()
        self.error_primer_apellido_admin_edit.hide()
        self.error_segundo_apellido_admin_edit.hide()
        
        self.date.setText(self.states.data['currentDate'].toString("dd/MM/yyyy"))
        self.clients_total.setText(str(self.states.data['clients_amount']))
        self.total_unpaids.setText(str(self.states.data['unpaids_amount']))
        self.total_notify.setText(str(self.states.data['notify_amount']))
        self.home_button.clicked.connect(self.goto_home)
        self.clients_button.clicked.connect(self.goto_clients)
        self.close_sidebar_button.clicked.connect(self.close)
        self.add_client_button.clicked.connect(self.goto_client_creation_form)
        self.picture.mousePressEvent = self.select_client_picture
        self.picture_edit.mousePressEvent = self.select_client_edit_picture
        self.picture_admin.mousePressEvent = self.select_client_picture
        self.picture_admin_edit.mousePressEvent = self.select_client_edit_picture
        self.accept_button.clicked.connect(self.create_client)
        self.accept_button_admin.clicked.connect(self.create_client_as_admin)
        self.decline_button.clicked.connect(self.goto_clients_list)
        self.decline_button_edit.clicked.connect(self.goto_clients_list)

        ci_string_validator = CIValidator(self.error_ci)
        telefono_string_validator = TelefonoValidator(self.error_telefono)
        nombre_number_validator = InputsValidator(self.error_nombre)
        primer_apellido_number_validator = InputsValidator(self.error_primer_apellido)
        segundo_apellido_number_validator = InputsValidator(self.error_segundo_apellido)
        #edit
        ci_edit_string_validator = CIValidator(self.error_ci_edit)
        telefono_edit_string_validator = TelefonoValidator(self.error_telefono_edit)
        nombre_edit_number_validator = InputsValidator(self.error_nombre_edit)
        primer_edit_apellido_number_validator = InputsValidator(self.error_primer_apellido_edit)
        segundo_edit_apellido_number_validator = InputsValidator(self.error_segundo_apellido_edit)
        
        #admin
        ci_admin_string_validator = CIValidator(self.error_ci_admin)
        telefono_admin_string_validator = TelefonoValidator(self.error_telefono_admin)
        nombre_admin_number_validator = InputsValidator(self.error_nombre_admin)
        primer_admin_apellido_number_validator = InputsValidator(self.error_primer_apellido_admin)
        segundo_admin_apellido_number_validator = InputsValidator(self.error_segundo_apellido_admin)

        #admin
        ci_admin_edit_string_validator = CIValidator(self.error_ci_admin_edit)
        telefono_admin_edit_string_validator = TelefonoValidator(self.error_telefono_admin_edit)
        nombre_admin_edit_number_validator = InputsValidator(self.error_nombre_admin_edit)
        primer_admin_edit_apellido_number_validator = InputsValidator(self.error_primer_apellido_admin_edit)
        segundo_admin_edit_apellido_number_validator = InputsValidator(self.error_segundo_apellido_admin_edit)

        self.lineEdit_ci.setValidator(ci_string_validator)
        self.lineEdit_telefono.setValidator(telefono_string_validator)
        self.lineEdit_nombre.setValidator(nombre_number_validator)
        self.lineEdit_primer_apellido.setValidator(primer_apellido_number_validator)
        self.lineEdit_segundo_apellido.setValidator(segundo_apellido_number_validator)
        
        #edit
        self.lineEdit_ci_edit.setValidator(ci_edit_string_validator)
        self.lineEdit_telefono_edit.setValidator(telefono_edit_string_validator)
        self.lineEdit_nombre_edit.setValidator(nombre_edit_number_validator)
        self.lineEdit_primer_apellido_edit.setValidator(primer_edit_apellido_number_validator)
        self.lineEdit_segundo_apellido_edit.setValidator(segundo_edit_apellido_number_validator)
        
        #admin
        self.lineEdit_ci_admin.setValidator(ci_admin_string_validator)
        self.lineEdit_telefono_admin.setValidator(telefono_admin_string_validator)
        self.lineEdit_nombre_admin.setValidator(nombre_admin_number_validator)
        self.lineEdit_primer_apellido_admin.setValidator(primer_admin_apellido_number_validator)
        self.lineEdit_segundo_apellido_admin.setValidator(segundo_admin_apellido_number_validator)

        #admin
        self.lineEdit_ci_admin_edit.setValidator(ci_admin_edit_string_validator)
        self.lineEdit_telefono_admin_edit.setValidator(telefono_admin_edit_string_validator)
        self.lineEdit_nombre_admin_edit.setValidator(nombre_admin_edit_number_validator)
        self.lineEdit_primer_apellido_admin_edit.setValidator(primer_admin_edit_apellido_number_validator)
        self.lineEdit_segundo_apellido_admin_edit.setValidator(segundo_admin_edit_apellido_number_validator)


        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.edit_button.clicked.connect(self.save_updated_client)
        self.edit_button_admin.clicked.connect(self.save_updated_client_as_admin)
        self.setBackgroundBlur()
        self.update_all_data()
        self.home_button.setStyleSheet("""
                                        border-style:solid;
                                        border-width:1px;
                                        border-color:rgb(255,170,0);
                                            """)


    def setBackgroundBlur(self):
        self.setStyleSheet(
            """
            QMainWindow { 
                background-image:url('./views/ui/assets/background.svg');
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
    
    def setCardCreateBlur(self):
        self.frame_10.setAutoFillBackground(True)
        palette = self.frame_10.palette()
        palette.setColor(QPalette.Background, QColor(53,53,53,200))
        self.frame_10.setPalette(palette)
        self.frame_10.lower()
        effect = QGraphicsBlurEffect()
        effect.setBlurRadius(1)
        effect.setBlurHints(QGraphicsBlurEffect.QualityHint)
        self.frame_10.setGraphicsEffect(effect)

    def setCardEditBlur(self):
        self.frame_7.setAutoFillBackground(True)
        palette = self.frame_7.palette()
        palette.setColor(QPalette.Background, QColor(53,53,53,200))
        self.frame_7.setPalette(palette)
        self.frame_7.lower()
        effect = QGraphicsBlurEffect()
        effect.setBlurRadius(1.5)
        effect.setBlurHints(QGraphicsBlurEffect.QualityHint)
        self.frame_7.setGraphicsEffect(effect)
        
    def resizeEvent(self, event):
       self.background_widget.setGeometry(self.rect())
       super().resizeEvent(event)

    def update_all_data(self):
        self.states.initialize_data()
        self.update_client_list()
        self.update_deudor_list()
        self.update_notify_list()

    def get_assets(self, file):
        return os.path.join(self.assets_path, file)

    def get_media(self, file):
        media_path = os.getcwd()
        media_path = media_path.replace("\\", "/")
        return os.path.join(media_path, file)
    
    def get_background(self, file):
        media_path = os.path.join(self.assets_path, "assets/")
        return os.path.join(media_path, file)

    def goto_home(self):
        self.clients_button.setStyleSheet("")
        self.home_button.setStyleSheet("""
                                        border-style:solid;
                                        border-width:1px;
                                        border-color:rgb(255,170,0);
                                            """)
        self.update_all_data()
        self.states.views['main_view']=0
        self.switch_screen.setCurrentIndex(self.states.views['main_view'])

    def goto_clients(self):
        self.home_button.setStyleSheet("")
        self.clients_button.setStyleSheet("""
                                            border-style:solid;
                                            border-width:1px;
                                            border-color:rgb(255,170,0);
                                            """)
        self.update_all_data()
        self.states.views['main_view']=1
        self.states.views['clients_view']=0
        self.switch_screen.setCurrentIndex(self.states.views['main_view'])
        self.clients_switch_screen.setCurrentIndex(self.states.views['clients_view'])

    def goto_clients_list(self):
        self.update_client_list()
        self.states.views['clients_view']=0
        self.clients_switch_screen.setCurrentIndex(self.states.views['clients_view'])

    def goto_client_creation_form(self):
        self.setCardCreateBlur()
        if self.credentials == 'admin':
            self.states.views['clients_view']=3
            self.clients_switch_screen.setCurrentIndex(self.states.views['clients_view'])
        else:
            self.states.views['clients_view']=1
            self.clients_switch_screen.setCurrentIndex(self.states.views['clients_view'])
    
    def select_client_picture(self, event):
        self.picture.clear()
        if event.button() == Qt.LeftButton:
            filename, _ = QFileDialog.getOpenFileName(self, "Choose Image")
            if filename:
                self.creating_client_picture = filename
                self.picture.setStyleSheet("""
                                              border-image:""" f'url({filename})'
                                              """0 0 0 0;
                                             """)
                
    def select_client_picture(self, event):
        self.picture_admin.clear()
        if event.button() == Qt.LeftButton:
            filename, _ = QFileDialog.getOpenFileName(self, "Choose Image")
            if filename:
                self.creating_client_picture = filename
                self.picture_admin.setStyleSheet("""
                                              border-image:""" f'url({filename})'
                                              """0 0 0 0;
                                             """)

    def select_client_edit_picture(self, event):
        if event.button() == Qt.LeftButton:
            filename, _ = QFileDialog.getOpenFileName(self, "Choose Image")
            if filename:
                self.creating_client_edit_picture = filename
                self.picture_edit.setStyleSheet(f"""
                                              border-image: url({filename})0 0 0 0;
                                             """)
                
    def select_client_edit_picture(self, event):
        if event.button() == Qt.LeftButton:
            filename, _ = QFileDialog.getOpenFileName(self, "Choose Image")
            if filename:
                self.creating_client_edit_picture = filename
                self.picture_admin_edit.setStyleSheet(f"""
                                              border-image: url({filename})0 0 0 0;
                                             """)
        
    
    def create_client(self):
        is_valid = True

        if not self.lineEdit_ci.hasAcceptableInput() and not \
            self.lineEdit_nombre.hasAcceptableInput() and not \
            self.lineEdit_primer_apellido.hasAcceptableInput() and not \
            self.lineEdit_segundo_apellido.hasAcceptableInput() and not \
            self.lineEdit_telefono.hasAcceptableInput() and self.creating_client_picture is not None:

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
                        numero_de_telefono= self.lineEdit_telefono.text(),
                        foto = uploaded_file,
                    )
                self.goto_clients_list()
            else:
                self.error_ci.setText('Ya existe un cliente con ese carné de identidad')
                self.error_ci.show()

                
    def create_client_as_admin(self):
        is_valid = True
        fecha_ingreso = self.fecha_entrada_admin.date()
        fecha_ingreso_datetime = date(fecha_ingreso.year(), fecha_ingreso.month(), fecha_ingreso.day())
        ultimo_pago = self.ultimo_pago_admin.date()
        ultimo_pago_datetime = date(ultimo_pago.year(), ultimo_pago.month(), ultimo_pago.day())

        if not self.lineEdit_ci_admin.hasAcceptableInput() and not \
            self.lineEdit_nombre_admin.hasAcceptableInput() and not \
            self.lineEdit_primer_apellido_admin.hasAcceptableInput() and not \
            self.lineEdit_segundo_apellido_admin.hasAcceptableInput() and not \
            self.lineEdit_telefono_admin.hasAcceptableInput() and self.creating_client_picture is not None:

            for client in self.states.data['client_list']:
                if self.lineEdit_ci_admin.text() == client['ci']:
                    is_valid = False
                    break

            if is_valid:
                with open(self.creating_client_picture, 'rb') as picture:
                    uploaded_file = SimpleUploadedFile(picture.name, picture.read(), content_type='image/jpeg')
                    Cliente.objects.create(
                        ci = self.lineEdit_ci_admin.text(),
                        nombre = self.lineEdit_nombre_admin.text(),
                        primer_apellido = self.lineEdit_primer_apellido_admin.text(),
                        segundo_apellido = self.lineEdit_segundo_apellido_admin.text(),
                        tipo_entrenamiento = self.tipo_entrenamiento_admin.currentText(),
                        numero_de_telefono= self.lineEdit_telefono_admin.text(),
                        fecha_ingreso = fecha_ingreso_datetime,
                        ultimo_pago = ultimo_pago_datetime,
                        foto = uploaded_file,
                    )
                self.goto_clients_list()
            else:
                self.error_ci_admin.setText('Ya existe un cliente con ese carnet de identidad')
                self.error_ci_admin.show()

    def set_client_values_to_edit(self, ci_value):
        self.editing_client_ci = ci_value
        client = Cliente.objects.get(ci=ci_value)
        self.lineEdit_ci_edit.setText(client.ci)
        self.lineEdit_nombre_edit.setText(client.nombre)
        self.lineEdit_primer_apellido_edit.setText(client.primer_apellido)
        self.lineEdit_segundo_apellido_edit.setText(client.segundo_apellido)
        self.tipo_entrenamiento_edit.setCurrentText(client.tipo_entrenamiento)
        self.lineEdit_telefono_edit.setText(client.numero_de_telefono)
        self.picture_edit.clear()
        picture_path = client.foto.url[1:]
        picture_path = self.get_media(picture_path).replace("\\", "/")
        self.picture_edit.setStyleSheet("""
                                              border-image:""" f'url({picture_path})'
                                              """0 0 0 0;
                                             """)
        
    def set_client_values_to_edit_as_admin(self, ci_value):
        self.editing_client_ci = ci_value
        client = Cliente.objects.get(ci=ci_value)
        self.lineEdit_ci_admin_edit.setText(client.ci)
        self.lineEdit_nombre_admin_edit.setText(client.nombre)
        self.lineEdit_primer_apellido_admin_edit.setText(client.primer_apellido)
        self.lineEdit_segundo_apellido_admin_edit.setText(client.segundo_apellido)
        self.tipo_entrenamiento_admin_edit.setCurrentText(client.tipo_entrenamiento)
        self.lineEdit_telefono_admin_edit.setText(client.numero_de_telefono)
        self.fecha_entrada_admin_edit.setDate(client.fecha_ingreso)
        self.ultimo_pago_admin_edit.setDate(client.ultimo_pago)
        self.picture_admin_edit.clear()
        picture_path = client.foto.url[1:]
        picture_path = self.get_media(picture_path).replace("\\", "/")
        self.picture_admin_edit.setStyleSheet("""
                                              border-image:""" f'url({picture_path})'
                                              """0 0 0 0;
                                             """)

    def save_updated_client(self):
        client = Cliente.objects.get(ci=self.editing_client_ci)
        if not self.lineEdit_ci_edit.hasAcceptableInput() and not \
            self.lineEdit_nombre_edit.hasAcceptableInput() and not \
            self.lineEdit_primer_apellido_edit.hasAcceptableInput() and not \
            self.lineEdit_segundo_apellido_edit.hasAcceptableInput():
            if self.creating_client_edit_picture is not None:
                with open(self.creating_client_edit_picture, 'rb') as picture:
                    uploaded_file = SimpleUploadedFile(picture.name, picture.read(), content_type='image/jpeg')
                    client.ci = self.lineEdit_ci_edit.text()
                    client.nombre = self.lineEdit_nombre_edit.text()
                    client.primer_apellido = self.lineEdit_primer_apellido_edit.text()
                    client.segundo_apellido = self.lineEdit_segundo_apellido_edit.text()
                    client.tipo_entrenamiento = self.tipo_entrenamiento_edit.currentText()
                    client.numero_de_telefono = self.lineEdit_telefono_edit.text()
                    client.foto = uploaded_file
            else:
                client.ci = self.lineEdit_ci_edit.text()
                client.nombre = self.lineEdit_nombre_edit.text()
                client.primer_apellido = self.lineEdit_primer_apellido_edit.text()
                client.segundo_apellido = self.lineEdit_segundo_apellido_edit.text()
                client.tipo_entrenamiento = self.tipo_entrenamiento_edit.currentText()
                client.numero_de_telefono = self.lineEdit_telefono_edit.text()
            client.save()
            self.goto_clients_list()
            self.update_client_list()

    def save_updated_client_as_admin(self):
        client = Cliente.objects.get(ci=self.editing_client_ci)
        fecha_ingreso = self.fecha_entrada_admin_edit.date()
        fecha_ingreso_datetime = date(fecha_ingreso.year(), fecha_ingreso.month(), fecha_ingreso.day())
        ultimo_pago = self.ultimo_pago_admin_edit.date()
        ultimo_pago_datetime = date(ultimo_pago.year(), ultimo_pago.month(), ultimo_pago.day())

        if not self.lineEdit_ci_admin_edit.hasAcceptableInput() and not \
            self.lineEdit_nombre_admin_edit.hasAcceptableInput() and not \
            self.lineEdit_primer_apellido_admin_edit.hasAcceptableInput() and not \
            self.lineEdit_segundo_apellido_admin_edit.hasAcceptableInput():
            if self.creating_client_edit_picture is not None:
                with open(self.creating_client_edit_picture, 'rb') as picture:
                    uploaded_file = SimpleUploadedFile(picture.name, picture.read(), content_type='image/jpeg')
                    client.ci = self.lineEdit_ci_admin_edit.text()
                    client.nombre = self.lineEdit_nombre_admin_edit.text()
                    client.primer_apellido = self.lineEdit_primer_apellido_admin_edit.text()
                    client.segundo_apellido = self.lineEdit_segundo_apellido_admin_edit.text()
                    client.tipo_entrenamiento = self.tipo_entrenamiento_admin_edit.currentText()
                    client.numero_de_telefono = self.lineEdit_telefono_admin_edit.text()
                    client.fecha_ingreso = str(fecha_ingreso_datetime)
                    client.ultimo_pago = str(ultimo_pago_datetime)
                    client.foto = uploaded_file
            else:
                client.ci = self.lineEdit_ci_admin_edit.text()
                client.nombre = self.lineEdit_nombre_admin_edit.text()
                client.primer_apellido = self.lineEdit_primer_apellido_admin_edit.text()
                client.segundo_apellido = self.lineEdit_segundo_apellido_admin_edit.text()
                client.tipo_entrenamiento = self.tipo_entrenamiento_admin_edit.currentText()
                client.numero_de_telefono = self.lineEdit_telefono_admin_edit.text()
                client.fecha_ingreso = str(fecha_ingreso_datetime)
                client.ultimo_pago = str(ultimo_pago_datetime)
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
        self.setCardEditBlur()
        if self.credentials == 'admin':
            self.states.views['clients_view'] = 4
            self.clients_switch_screen.setCurrentIndex(self.states.views['clients_view'])
            self.set_client_values_to_edit_as_admin(ci_value)
        else:
            self.states.views['clients_view'] = index
            self.clients_switch_screen.setCurrentIndex(self.states.views['clients_view'])
            self.set_client_values_to_edit(ci_value)

    def handle_notificar(self, checked, ci):
        if checked:
            client = Cliente.objects.get(ci=ci)
            client.notificado = checked
            client.debe_notificarse = False
            client.save()
            self.update_all_data()
        else:
            client = Cliente.objects.get(ci=ci)
            client.notificado = checked
            client.debe_notificarse = True
            client.save()
            self.update_all_data()

    def handle_cobrar(self, value):
        try:
            client = Cliente.objects.get(ci=value)
            client.ultimo_pago = date.today()
            client.debe_notificarse = False
            client.deudor = False
            client.notificado = False 
            client.save()
            self.update_client_list()
        except Exception as err:
            print(f'{err}')


    def update_client_list(self):
        self.listWidget.clear()
        self.states.initialize_data()
        self.clients_total.setText(str(self.states.data['clients_amount']))
        self.total_unpaids.setText(str(self.states.data['unpaids_amount']))
        self.total_notify.setText(str(self.states.data['notify_amount']))
        for client in self.states.data['client_list']:
            item_widget = ClientListItem(client, self.assets_path)
            item_widget.view_changed.connect(self.handle_view_changed)
            item_widget.delete_client_signal.connect(self.delete_client)
            list_item = QListWidgetItem(self.listWidget)
            list_item.setSizeHint(item_widget.sizeHint())
            self.listWidget.setItemWidget(list_item, item_widget)

    def update_deudor_list(self):
        self.deudors_list.clear()
        self.states.initialize_data()
        for client in self.states.data['deudor_list']:
            item_widget = DeudorListItem(client, self.assets_path)
            item_widget.marcar_notificado_signal.connect(self.handle_notificar)
            item_widget.cobrar_deuda_signal.connect(self.handle_cobrar)
            list_item = QListWidgetItem(self.deudors_list)
            list_item.setSizeHint(item_widget.sizeHint())
            self.deudors_list.setItemWidget(list_item, item_widget)

    def update_notify_list(self):
        self.notify_list.clear()
        self.states.initialize_data()
        for client in self.states.data['notify_client_list']:
            item_widget = DeudorListItem(client, self.assets_path)
            item_widget.marcar_notificado_signal.connect(self.handle_notificar)
            item_widget.cobrar_deuda_signal.connect(self.handle_cobrar)
            list_item = QListWidgetItem(self.notify_list)
            list_item.setSizeHint(item_widget.sizeHint())
            self.notify_list.setItemWidget(list_item, item_widget)



class Session(QDialog):
    def __init__(self, states):
        self.credentials = None
        self.states = States(states.assets_path)
        self.assets_path = states.assets_path
        super(Session, self).__init__()
        uic.loadUi(self.get_assets("login.ui"), self)
        self.setWindowIcon(QIcon('icon.png'))
        self.error_credentials.hide()
        self.login.clicked.connect(self.validate)

    def get_assets(self, file):
        return os.path.join(self.assets_path, file)
    
    def get_icon(self, file):
        media_path = os.getcwd()
        media_path = media_path.replace("\\", "/")
        
        return os.path.join(media_path, file)

    def validate(self):
        if self.username.text() == 'admin' and self.password.text() == 'admin':
            self.credentials = 'admin'
            main = Main(self.states, self.credentials)
            self.close()
            main.showMaximized()
        elif self.username.text() == 'user' and self.password.text() == 'user':
            self.credentials = 'user'
            main = Main(self.states, self.credentials)
            self.close()
            main.showMaximized()
        else:
            self.error_credentials.setText('Credenciales incorrectas')
            self.error_credentials.show()



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

    mainWin = Session(states)
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

    mainWin.show()
    sys.exit(app.exec_())