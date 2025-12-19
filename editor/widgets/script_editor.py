from PySide6 import QtWebEngineWidgets
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import Slot, QObject, Signal
from PySide6.QtWebChannel import QWebChannel
from editor.utils.path import get_resource_path
from pathlib import Path


class ScriptEditor(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, script, path):
        super().__init__()
        self.script = script
        self.path = path

        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        class Backend(QObject):
            requestCode = Signal()
            setCode = Signal(str)

            def __init__(self, webview):
                super().__init__()
                self.webview = webview
            
            @Slot(str)
            def receiveCode(self, code):
                self.webview._save_code(code)

            @Slot()
            def requestCodeFromEditor(self):
                with open(self.webview.path / self.webview.script, 'r') as f:
                    code = f.read()
                self.setCode.emit(code)

        self.channel = QWebChannel()
        self.backend = Backend(self)
        self.channel.registerObject('backend', self.backend)
        self.page().setWebChannel(self.channel)

        with open(get_resource_path(Path('editor') / 'widgets' / 'script_editor.html')) as f:
            self.setHtml(f.read(), 'qrc:///')

    def save(self):
        self.backend.requestCode.emit()

    def _save_code(self, code):
        with open(self.path / self.script, 'w') as f:
            f.write(code)
