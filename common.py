from PyQt6.QtWidgets import QMessageBox, QWidget


def show_error(parent: QWidget, info: str):
    QMessageBox(parent, '错误', info)
