import sys
import threading
from typing import Callable, Optional

try:
    from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QWidget, QVBoxLayout, QPushButton, QLabel, QStyle, QLineEdit, QCheckBox
    from PySide6.QtGui import QIcon, QAction
    from PySide6.QtCore import Qt, QTimer
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False

import aml_runtime_access

class UIManager:
    _instance = None
    
    def __init__(self):
        self.app = None
        self.tray_icons = {}
        self.widgets = {}
        self._next_id = 1

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def interpreter(self):
        return aml_runtime_access.get_interpreter()

    def ensure_app(self):
        if not PYSIDE_AVAILABLE:
            raise RuntimeError("PySide6 is not installed. Please install it to use UI features.")
        if self.app is None:
            self.app = QApplication.instance() or QApplication(sys.argv)
            self.app.setQuitOnLastWindowClosed(False)

    def create_tray(self, title: str, icon_path: Optional[str] = None):
        self.ensure_app()
        tray = QSystemTrayIcon(self.app)
        if icon_path:
            tray.setIcon(QIcon(icon_path))
        else:
            # Default icon if none provided
            tray.setIcon(self.app.style().standardIcon(QStyle.SP_ComputerIcon))
        
        tray.setToolTip(title)
        menu = QMenu()
        tray.setContextMenu(menu)
        
        id = f"tray_{self._next_id}"
        self._next_id += 1
        self.tray_icons[id] = {"tray": tray, "menu": menu}
        return id

    def add_menu_item(self, tray_id: str, label: str, callback: Callable):
        if tray_id not in self.tray_icons:
            return False
        
        menu = self.tray_icons[tray_id]["menu"]
        action = QAction(label, menu)
        
        def triggered():
            if self.interpreter and callback:
                # We need to run this in a way that the interpreter can handle
                # Since we are in the Qt thread, we can call the function
                try:
                    # In AML, functions are objects with a .call() method usually
                    # but here they might be passed as raw function objects
                    if hasattr(callback, 'call'):
                        callback.call(self.interpreter, [])
                    else:
                        callback()
                except Exception as e:
                    print(f"Error in UI callback: {e}")

        action.triggered.connect(triggered)
        menu.addAction(action)
        return True

    def show_tray(self, tray_id: str):
        if tray_id in self.tray_icons:
            self.tray_icons[tray_id]["tray"].show()
            return True
        return False

    def create_widget(self, title: str, width: int = 200, height: int = 150, transparent: bool = False, on_top: bool = False, draggable: bool = True):
        self.ensure_app()
        
        class DraggableWidget(QWidget):
            def __init__(self, parent=None, is_draggable=True):
                super().__init__(parent)
                self.is_draggable = is_draggable
                self.dragging = False
                self.drag_pos = None

            def mousePressEvent(self, event):
                if self.is_draggable and event.button() == Qt.LeftButton:
                    self.dragging = True
                    self.drag_pos = event.globalPos() - self.pos()
                    event.accept()

            def mouseMoveEvent(self, event):
                if self.is_draggable and self.dragging and event.buttons() & Qt.LeftButton:
                    self.move(event.globalPos() - self.drag_pos)
                    event.accept()

            def mouseReleaseEvent(self, event):
                self.dragging = False

        widget = DraggableWidget(is_draggable=draggable)
        widget.setWindowTitle(title)
        widget.resize(width, height)
        
        flags = Qt.Window
        if on_top:
            flags |= Qt.WindowStaysOnTopHint
        if transparent:
            widget.setAttribute(Qt.WA_TranslucentBackground)
            flags |= Qt.FramelessWindowHint
            
        widget.setWindowFlags(flags)
        
        layout = QVBoxLayout(widget)
        
        id = f"widget_{self._next_id}"
        self._next_id += 1
        self.widgets[id] = {"widget": widget, "layout": layout}
        return id

    def add_label(self, widget_id: str, text: str):
        if widget_id not in self.widgets: return False
        label = QLabel(text)
        self.widgets[widget_id]["layout"].addWidget(label)
        return True

    def add_spacer(self, widget_id: str):
        if widget_id not in self.widgets: return False
        from PySide6.QtWidgets import QSpacerItem, QSizePolicy
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.widgets[widget_id]["layout"].addItem(spacer)
        return True

    def add_button(self, widget_id: str, label: str, callback: Callable):
        if widget_id not in self.widgets: return False
        btn = QPushButton(label)
        
        def clicked():
            if self.interpreter and callback:
                try:
                    if hasattr(callback, 'call'):
                        callback.call(self.interpreter, [])
                    else:
                        callback()
                except Exception as e:
                    print(f"Error in UI callback: {e}")
                    
        btn.clicked.connect(clicked)
        self.widgets[widget_id]["layout"].addWidget(btn)
        return True

    def add_input(self, widget_id: str, placeholder: str = ""):
        if widget_id not in self.widgets: return None
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        self.widgets[widget_id]["layout"].addWidget(edit)
        
        input_id = f"input_{self._next_id}"
        self._next_id += 1
        if "inputs" not in self.widgets[widget_id]:
            self.widgets[widget_id]["inputs"] = {}
        self.widgets[widget_id]["inputs"][input_id] = edit
        return input_id

    def get_input_text(self, widget_id: str, input_id: str):
        if widget_id in self.widgets and "inputs" in self.widgets[widget_id]:
            if input_id in self.widgets[widget_id]["inputs"]:
                return self.widgets[widget_id]["inputs"][input_id].text()
        return ""

    def add_checkbox(self, widget_id: str, label: str, checked: bool = False):
        if widget_id not in self.widgets: return None
        cb = QCheckBox(label)
        cb.setChecked(checked)
        self.widgets[widget_id]["layout"].addWidget(cb)
        
        cb_id = f"cb_{self._next_id}"
        self._next_id += 1
        if "checkboxes" not in self.widgets[widget_id]:
            self.widgets[widget_id]["checkboxes"] = {}
        self.widgets[widget_id]["checkboxes"][cb_id] = cb
        return cb_id

    def is_checked(self, widget_id: str, cb_id: str):
        if widget_id in self.widgets and "checkboxes" in self.widgets[widget_id]:
            if cb_id in self.widgets[widget_id]["checkboxes"]:
                return self.widgets[widget_id]["checkboxes"][cb_id].isChecked()
        return False

    def show_widget(self, widget_id: str):
        if widget_id in self.widgets:
            self.widgets[widget_id]["widget"].show()
            return True
        return False

    def set_position(self, widget_id: str, x: int, y: int):
        if widget_id in self.widgets:
            self.widgets[widget_id]["widget"].move(x, y)
            return True
        return False

    def set_size(self, widget_id: str, w: int, h: int):
        if widget_id in self.widgets:
            self.widgets[widget_id]["widget"].resize(w, h)
            return True
        return False

    def set_style(self, widget_id: str, stylesheet: str):
        if widget_id in self.widgets:
            self.widgets[widget_id]["widget"].setStyleSheet(stylesheet)
            return True
        return False

    def set_color(self, widget_id: str, bg: str = None, fg: str = None):
        if widget_id not in self.widgets: return False
        style = ""
        if bg: style += f"background-color: {bg}; "
        if fg: style += f"color: {fg}; "
        if style:
            current = self.widgets[widget_id]["widget"].styleSheet()
            self.widgets[widget_id]["widget"].setStyleSheet(current + f" QWidget {{ {style} }}")
        return True

    def run(self):
        self.ensure_app()
        print("[UI] Starting Qt event loop...")
        result = self.app.exec()
        print(f"[UI] Qt event loop exited with code {result}")
        return result

# Plugin functions for AML
def create_tray(title, icon=None):
    return UIManager.get_instance().create_tray(title, icon)

def add_menu_item(tray_id, label, callback):
    return UIManager.get_instance().add_menu_item(tray_id, label, callback)

def show_tray(tray_id):
    return UIManager.get_instance().show_tray(tray_id)

def create_widget(title, width=200, height=150, transparent=False, on_top=True, draggable=True):
    return UIManager.get_instance().create_widget(title, width, height, transparent, on_top, draggable)

def add_button(widget_id, label, callback):
    return UIManager.get_instance().add_button(widget_id, label, callback)

def add_input(widget_id, placeholder=""):
    return UIManager.get_instance().add_input(widget_id, placeholder)

def get_input_text(widget_id, input_id):
    return UIManager.get_instance().get_input_text(widget_id, input_id)

def add_checkbox(widget_id, label, checked=False):
    return UIManager.get_instance().add_checkbox(widget_id, label, checked)

def is_checked(widget_id, cb_id):
    return UIManager.get_instance().is_checked(widget_id, cb_id)

def add_label(widget_id, text):
    return UIManager.get_instance().add_label(widget_id, text)

def add_spacer(widget_id):
    return UIManager.get_instance().add_spacer(widget_id)

def show_widget(widget_id):
    return UIManager.get_instance().show_widget(widget_id)

def set_position(widget_id, x, y):
    return UIManager.get_instance().set_position(widget_id, x, y)

def set_size(widget_id, w, h):
    return UIManager.get_instance().set_size(widget_id, w, h)

def set_style(widget_id, stylesheet):
    return UIManager.get_instance().set_style(widget_id, stylesheet)

def set_color(widget_id, bg=None, fg=None):
    return UIManager.get_instance().set_color(widget_id, bg, fg)

def run_loop():
    return UIManager.get_instance().run()

def stop():
    app = QApplication.instance()
    if app:
        app.quit()
    return True

def show_notification(title, message, icon_path=None):
    ui = UIManager.get_instance()
    ui.ensure_app()
    tray = QSystemTrayIcon(ui.app)
    if icon_path:
        tray.setIcon(QIcon(icon_path))
    else:
        tray.setIcon(ui.app.style().standardIcon(QStyle.SP_MessageBoxInformation))
    tray.show()
    tray.showMessage(title, message, QSystemTrayIcon.Information)
    # Give it some time to show before potential GC
    QTimer.singleShot(10000, tray.hide)
