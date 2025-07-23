# themes.py

from PyQt5 import QtGui

def apply_gradient_theme(widget, theme="dark"):
    """
    Apply a vertical gradient background theme to a widget.
    :param widget: The QWidget to apply the theme to.
    :param theme: 'dark' or 'light'
    """
    palette = widget.palette()
    gradient = QtGui.QLinearGradient(0, 0, 0, widget.height())

    if theme == "dark":
        gradient.setColorAt(0, QtGui.QColor("#0A2647"))   # deep blue
        gradient.setColorAt(1, QtGui.QColor("#144272"))   # softer blue
    else:
        gradient.setColorAt(0, QtGui.QColor("#dfe9f3"))   # light gray
        gradient.setColorAt(1, QtGui.QColor("#ffffff"))   # white

    palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(gradient))
    widget.setAutoFillBackground(True)
    widget.setPalette(palette)
