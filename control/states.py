from PyQt5.QtCore import QDate, pyqtSignal
from data.models import Cliente

class States:
    def __init__(self, assets_path):
        self.assets_path = assets_path
        self.views = {'main_view': 0, 'clients_view': 0}
        self.data = {}
        client_list = Cliente.objects.all()
        client_list_dict = []
        for client in client_list:
            client_list_dict.append(client.get_dict())
        currentDate = QDate.currentDate()
        self.data['currentDate']=currentDate
        self.data['client_list']=client_list_dict

    def reload_client_list(self):
        print('reloading...')
        client_list = Cliente.objects.all()
        client_list_dict = []
        for client in client_list:
            client_list_dict.append(client.get_dict())
        self.data['client_list'] = client_list_dict