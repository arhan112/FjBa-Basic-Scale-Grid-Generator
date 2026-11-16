
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon

from .fjba_basic_grid import main


class FjBaBasicGridPlugin:

    MENU_NAME = "&FjBa Basic Grid Generator"

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.window = None
        self.toolbar = None

    def initGui(self):

        icon_path = self.get_icon_path()

        self.action = QAction(
            QIcon(icon_path),
            "FjBa Basic Scale Grid Generator",
            self.iface.mainWindow()
        )

        self.action.setToolTip(
            "Create scale-based map grid frames"
        )

        self.action.triggered.connect(self.run)

        self.iface.addPluginToMenu(
            self.MENU_NAME,
            self.action
        )

        self.iface.addToolBarIcon(self.action)

    def get_icon_path(self):

        import os

        return os.path.join(
            os.path.dirname(__file__),
            "icon.png"
        )

    def run(self, checked=False):

        try:

            if (
                self.window is not None
                and self.window.isVisible()
            ):

                self.window.raise_()
                self.window.activateWindow()
                return

            self.window = main(self.iface)

        except Exception as error:

            from qgis.PyQt.QtWidgets import QMessageBox

            QMessageBox.critical(
                self.iface.mainWindow(),
                "FjBa Basic Grid Generator",
                str(error)
            )

    def unload(self):

        if self.window is not None:

            self.window.close()
            self.window = None

        if self.action is not None:

            self.iface.removePluginMenu(
                self.MENU_NAME,
                self.action
            )

            self.iface.removeToolBarIcon(
                self.action
            )

            self.action.deleteLater()
            self.action = None
