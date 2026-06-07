import sys

from PyQt5.QtWidgets import QApplication

from controller.main_controller import MainController
from view.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Weather Data Analysis System")

    window = MainWindow()
    controller = MainController(window)
    window.controller = controller
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
