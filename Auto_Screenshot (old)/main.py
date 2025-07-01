import sys
import gui
import log
from PyQt6.QtWidgets import QApplication

log.logger.info("App start")

app = QApplication(sys.argv)
window = gui.Maingui()
window.show()
app.exec()