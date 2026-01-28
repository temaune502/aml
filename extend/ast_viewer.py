import os
import pickle
import sys
import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QListWidget, QListWidgetItem, QTextEdit, QLabel, QSplitter,
    QPushButton, QMessageBox, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Додаємо шлях до проекту, щоб імпортувати AML компоненти
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from aml.parser import AST, Program, VarDeclaration, ConstDeclaration, FunctionDeclaration, NamespaceDeclaration

class ASTViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AML AST Cache Viewer")
        self.resize(1000, 700)
        
        self.cache_dir = os.path.join(os.getcwd(), ".aml_cache")
        
        self.init_ui()
        self.refresh_cache()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Toolbar-like area
        top_layout = QHBoxLayout()
        self.label_info = QLabel(f"Cache Directory: {self.cache_dir}")
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.refresh_cache)
        btn_clear = QPushButton("Clear Selection Cache")
        btn_clear.clicked.connect(self.clear_selected_cache)
        
        top_layout.addWidget(self.label_info)
        top_layout.addStretch()
        top_layout.addWidget(btn_refresh)
        top_layout.addWidget(btn_clear)
        main_layout.addLayout(top_layout)

        # Splitter for list and details
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left side: List of cache files
        self.list_widget = QListWidget()
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.splitter.addWidget(self.list_widget)
        
        # Right side: Details (Metadata and AST Tree)
        details_container = QWidget()
        details_layout = QVBoxLayout(details_container)
        
        self.metadata_label = QLabel("Select a cache file to view details")
        self.metadata_label.setWordWrap(True)
        self.metadata_label.setFont(QFont("Consolas", 10))
        details_layout.addWidget(self.metadata_label)
        
        self.ast_tree = QTreeWidget()
        self.ast_tree.setHeaderLabels(["AST Node", "Details"])
        self.ast_tree.setColumnWidth(0, 300)
        details_layout.addWidget(self.ast_tree)
        
        self.splitter.addWidget(details_container)
        self.splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(self.splitter)

    def refresh_cache(self):
        self.list_widget.clear()
        if not os.path.exists(self.cache_dir):
            return

        files = [f for f in os.listdir(self.cache_dir) if f.endswith(".ast")]
        for f in files:
            path = os.path.join(self.cache_dir, f)
            mtime = os.path.getmtime(path)
            dt = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            item = QListWidgetItem(f"{f} ({dt})")
            item.setData(Qt.UserRole, path)
            self.list_widget.addItem(item)

    def on_selection_changed(self):
        items = self.list_widget.selectedItems()
        if not items:
            return
        
        file_path = items[0].data(Qt.UserRole)
        self.load_ast_details(file_path)

    def load_ast_details(self, cache_file):
        try:
            with open(cache_file, 'rb') as f:
                ast_obj = pickle.load(f)
            
            # Show metadata
            meta = getattr(ast_obj, '_cache_metadata', {})
            meta_text = "<b>Cache Metadata:</b><br>"
            if meta:
                meta_text += f"Source File: {meta.get('file_path')}<br>"
                meta_text += f"Size: {meta.get('size')} bytes<br>"
                meta_text += f"Key: {meta.get('cache_key')}<br>"
                cached_at = datetime.datetime.fromtimestamp(meta.get('cached_at')).strftime('%Y-%m-%d %H:%M:%S')
                meta_text += f"Cached At: {cached_at}"
            else:
                meta_text += "No metadata found (legacy cache format)"
            
            self.metadata_label.setText(meta_text)
            
            # Show AST Tree
            self.ast_tree.clear()
            self.populate_tree(ast_obj, self.ast_tree.invisibleRootItem())
            self.ast_tree.expandToDepth(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load cache file: {e}")

    def populate_tree(self, node, parent_item):
        if isinstance(node, Program):
            item = QTreeWidgetItem(parent_item, ["Program", f"{len(node.statements)} statements"])
            for stmt in node.statements:
                self.populate_tree(stmt, item)
        elif isinstance(node, VarDeclaration):
            item = QTreeWidgetItem(parent_item, ["VarDeclaration", f"name: {node.name}"])
            self.populate_tree(node.value, item)
        elif isinstance(node, ConstDeclaration):
            item = QTreeWidgetItem(parent_item, ["ConstDeclaration", f"name: {node.name} (CONST)"])
            self.populate_tree(node.value, item)
        elif isinstance(node, FunctionDeclaration):
            params = ", ".join([p if isinstance(p, str) else p[0] for p in (node.params or [])])
            item = QTreeWidgetItem(parent_item, ["Function", f"{node.name}({params})"])
            body_item = QTreeWidgetItem(item, ["Body", ""])
            for stmt in node.body:
                self.populate_tree(stmt, body_item)
        elif isinstance(node, NamespaceDeclaration):
            item = QTreeWidgetItem(parent_item, ["Namespace", node.name])
            for stmt in node.body:
                self.populate_tree(stmt, item)
        elif hasattr(node, '__class__'):
            # Generic node representation
            details = ""
            if hasattr(node, 'value'): details = str(node.value)
            elif hasattr(node, 'op'): details = f"op: {node.op}"
            
            node_name = node.__class__.__name__
            item = QTreeWidgetItem(parent_item, [node_name, details])
            
            # Try to recursively add children for common structures
            if hasattr(node, 'left'): self.populate_tree(node.left, item)
            if hasattr(node, 'right'): self.populate_tree(node.right, item)
            if hasattr(node, 'expression'): self.populate_tree(node.expression, item)
            if hasattr(node, 'condition'): self.populate_tree(node.condition, item)
            if hasattr(node, 'target'): self.populate_tree(node.target, item)
        else:
            QTreeWidgetItem(parent_item, [str(type(node)), str(node)])

    def clear_selected_cache(self):
        items = self.list_widget.selectedItems()
        if not items:
            return
        
        file_path = items[0].data(Qt.UserRole)
        try:
            os.remove(file_path)
            self.refresh_cache()
            self.metadata_label.setText("Cache deleted.")
            self.ast_tree.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete cache: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ASTViewer()
    viewer.show()
    sys.exit(app.exec())
