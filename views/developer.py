import os
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

class DevDialog(QDialog):
    def __init__(self, states):
        self.states = states
        self.assets_path = self.states.assets_path
        super(DevDialog, self).__init__()
        uic.loadUi(self.get_assets("test.ui"), self)

        self.history = {}
        self.start_command = "{}"

        self.textBrowser.setAcceptRichText(True)
        self.textBrowser.setOpenExternalLinks(False)

        self.pushButton.clicked.connect(self.proccess)

    def get_assets(self, file):
        return os.path.join(self.assets_path, file)

    def get_media(self, file):
        media_path = os.path.join(self.assets_path, "assets/")
        return os.path.join(media_path, file)

    def write(self, data, mode="info"):

        data = "\n".join(["".join([f"&#{ord(n)};" for n in i]) for i in data.split("\n")])
            

        if mode == "info":
            bg_color = "#b0daff"
        elif mode == "error":
            bg_color = "#ff8989"
        data = data.replace('\n', "<br>")
        if data == "<br>|":
            return
        html = f"""
            <div>
                <h3 style="background-color: {bg_color};">
                    {mode}
                </h3>
                <div style="background-color: {bg_color}; white-space: pre;">{data}</div>
            </div> 
        """
        self.textBrowser.append(html)
        self.textBrowser.verticalScrollBar().setValue(self.textBrowser.verticalScrollBar().maximum())
        self.textBrowser.anchorClicked.connect(self.link_clicked)

    def proccess(self):
        import traceback
        import uuid
        text = self.plainTextEdit.toPlainText()
        try:
            token = str(uuid.uuid4())
            self.history[token] = text
            print("Input:\n"+text)
            self.textBrowser.append(f"""<a href="{token}">Copy</a>""")
            exec(self.start_command.format(text))
        except Exception as e:
            self.write("Exception: "+str(e)+"<br>"+traceback.format_exc(), "error")
        self.history["console"] = self.textBrowser.toHtml()
        self.plainTextEdit.setPlainText("")
    
    def link_clicked(self, url):
        self.textBrowser.setHtml(self.history["console"])
        self.textBrowser.verticalScrollBar().setValue(self.textBrowser.verticalScrollBar().maximum())
        self.plainTextEdit.setPlainText(self.history[url.url()])