from PyQt5.QtCore import QDate, pyqtSignal
from data.models import Cliente

class States:
    def __init__(self, assets_path):
        self.assets_path = assets_path
        self.views = {'main_view': 0, 'clients_view': 0}
        self.data = {}
        currentDate = QDate.currentDate()
        self.data['currentDate']=currentDate
        self.initialize_data()

    def initialize_data(self):
        main_list = Cliente.objects.all()
        for client in main_list:
            client.get_date_30_days_after_ultimo_pago()
        self.get_all_clients_amount()
        self.reload_client_list()
        self.reload_notify_client_list()
        self.reload_deudor_list()

    def reload_client_list(self):
        client_list = Cliente.objects.all()
        client_list_dict = []
        for client in client_list:
            client_list_dict.append(client.get_dict())
        self.data['client_list'] = client_list_dict

    def reload_notify_client_list(self):
        client_list = Cliente.objects.filter(debe_notificarse=True)
        client_list_dict = []
        for client in client_list:
            if client.deudor == False:
                client_list_dict.append(client.get_dict())
        self.data['notify_client_list'] = client_list_dict

    def reload_deudor_list(self):
        client_list = Cliente.objects.filter(deudor=True)
        client_list_dict = []
        for client in client_list:
            client_list_dict.append(client.get_dict())
        self.data['deudor_list'] = client_list_dict

    def get_all_clients_amount(self):
        self.data['clients_amount'] = Cliente.objects.all().count()
        self.data['unpaids_amount'] = Cliente.objects.filter(deudor=True).count()
        self.data['notify_amount'] = Cliente.objects.filter(debe_notificarse=True).count()