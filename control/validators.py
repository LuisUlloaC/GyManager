from PyQt5 import QtCore, QtGui

class InputsValidator(QtGui.QValidator):
    def __init__(self, label):
        super().__init__()
        self.label = label

    def validate(self, string, position):
        if string.strip() != "":
            if QtCore.QRegExp('.*[0-9].*').exactMatch(string):
                self.label.setText("Este campo no puede contener números")
                self.label.show()
                return QtGui.QValidator.Acceptable, string, position
            else:
                self.label.hide()
                return QtGui.QValidator.Intermediate, string, position
        else:
            self.label.setText("Este campo está vacío")
            self.label.show()
            return QtGui.QValidator.Intermediate, string, position
        
class CIValidator(QtGui.QValidator):
   def __init__(self, label):
       super().__init__()
       self.label = label

   def validate(self, string, position):
       if string.strip() != "":
           if not QtCore.QRegExp('^[0-9]{6}$|^[0-9]{11}$').exactMatch(string):
               self.label.setText("El campo debe tener 6 o 11 dígitos")
               self.label.show()
               return QtGui.QValidator.Acceptable, string, position
           else:
               self.label.hide()
               return QtGui.QValidator.Intermediate, string, position
       else:
           self.label.setText("Este campo está vacío")
           self.label.show()
           return QtGui.QValidator.Intermediate, string, position