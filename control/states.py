from PyQt5.QtCore import QDate
from data.models import Cliente

class States:
    def __init__(self, assets_path):
        self.assets_path = assets_path
        self.views = {}
        self.data = {}
        client_list = Cliente.objects.all()
        currentDate = QDate.currentDate()
        self.data['currentDate']=currentDate
        self.data['clent_list']=client_list