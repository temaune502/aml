import sys
import threading
import time
import os
from enum import Enum
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTextEdit, QTreeWidget, QTreeWidgetItem, 
                               QPushButton, QSplitter, QLabel, QComboBox, QPlainTextEdit,
                               QFileDialog, QTabWidget, QMenu, QGraphicsView, QGraphicsScene,
                               QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem,
                               QGraphicsEllipseItem, QGraphicsItemGroup)
from PySide6.QtCore import Qt, Signal, QObject, Slot, QThread, QPointF, QRectF
from PySide6.QtGui import (QColor, QTextCursor, QFont, QSyntaxHighlighter, 
                           QTextCharFormat, QPalette, QAction, QPainter, QPen, QBrush)

from aml.parser import Parser
from aml.lexer import Lexer
from aml.interpreter import Interpreter, Environment
from aml.tokens import TokenType

class FlowchartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # Toolbar for flowchart
        toolbar = QHBoxLayout()
        
        save_btn = QPushButton("Save PNG")
        save_btn.clicked.connect(self.save_as_png)
        toolbar.addWidget(save_btn)
        
        print_btn = QPushButton("Print AST to Console")
        print_btn.clicked.connect(self.print_ast_to_console)
        toolbar.addWidget(print_btn)
        
        toolbar.addSpacing(20)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(30, 30)
        zoom_in_btn.clicked.connect(lambda: self.zoom(1.2))
        toolbar.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedSize(30, 30)
        zoom_out_btn.clicked.connect(lambda: self.zoom(0.8))
        toolbar.addWidget(zoom_out_btn)
        
        fit_btn = QPushButton("Fit")
        fit_btn.setFixedSize(40, 30)
        fit_btn.clicked.connect(self.fit_view)
        toolbar.addWidget(fit_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        layout.addWidget(self.view)
        
        # Zoom support
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        self.node_width = 160
        self.node_height = 60
        self.level_gap = 80
        self.sibling_gap = 30
        self.layout_info = {}
        self.current_root = None

    def print_ast_to_console(self):
        if not self.current_root: return
        
        output = ["--- AST Text Representation ---"]
        self._serialize_ast(self.current_root, 0, output, set())
        output.append("--- End of AST ---")
        
        # We need to find the AMLDebugger instance to print to its console
        # or we can just print to sys.stdout if redirected
        print("\n".join(output))

    def _serialize_ast(self, n, indent, output, visited):
        if id(n) in visited:
            output.append("  " * indent + f"[Cycle detected: {n.__class__.__name__}]")
            return
        visited.add(id(n))
        
        name = n.__class__.__name__
        details = ""
        try:
            if hasattr(n, 'value'): details = f" (value={n.value})"
            elif hasattr(n, 'name'): details = f" (name='{n.name}')"
            elif hasattr(n, 'op'): details = f" (op='{n.op}')"
            elif hasattr(n, 'var_name'): details = f" (var='{n.var_name}')"
        except: pass
        
        loc = ""
        if hasattr(n, 'line'):
            loc = f" [L:{n.line} C:{n.column}]"
            
        output.append("  " * indent + f"- {name}{details}{loc}")
        
        children = self._get_children(n)
        for key, child in children:
            output.append("  " * (indent + 1) + f"@{key}:")
            self._serialize_ast(child, indent + 2, output, visited)

    def zoom(self, factor):
        self.view.scale(factor, factor)

    def fit_view(self):
        if not self.scene.items(): return
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        zoom_in_factor = 1.2
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            self.zoom(zoom_in_factor)
        else:
            self.zoom(zoom_out_factor)
        event.accept()

    def set_ast(self, root_node):
        self.current_root = root_node
        self.scene.clear()
        self.layout_info = {}
        if not root_node: return
        
        # Build logical tree structure first to calculate layout
        self._calculate_layout(root_node, 0, 0, set())
        self._draw_tree(root_node, set())
        
        # Adjust scene rect
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-100, -100, 100, 100))
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def save_as_png(self):
        from PySide6.QtGui import QPixmap, QImage
        from PySide6.QtWidgets import QFileDialog
        
        fname, _ = QFileDialog.getSaveFileName(self, "Save AST Visualization", "", "PNG Files (*.png)")
        if not fname: return
        
        # Determine the area to capture
        items_rect = self.scene.itemsBoundingRect()
        if items_rect.isEmpty(): return
        
        # Add some padding
        items_rect.adjust(-50, -50, 50, 50)
        
        # Create image with transparent background or specific color
        image = QImage(items_rect.size().toSize(), QImage.Format_ARGB32)
        image.fill(QColor("#1e1e1e")) # Match dark theme
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Render scene to the image
        self.scene.render(painter, QRectF(image.rect()), items_rect)
        painter.end()
        
        image.save(fname)

    def _get_children(self, n):
        children = []
        if hasattr(n, '__dict__'):
            # Specific order for common nodes
            keys = list(n.__dict__.keys())
            # Prioritize certain keys for better visualization
            for priority_key in ['condition', 'if_body', 'else_body', 'iterable', 'body', 'left', 'right', 'expr', 'value', 'target']:
                if priority_key in keys:
                    keys.remove(priority_key)
                    keys.insert(0, priority_key)

            for key in keys:
                val = n.__dict__[key]
                # Skip internal fields and op (since op is usually an Enum shown in details)
                if key in ['token', 'line', 'column', 'parent', 'enclosing', 'interpreter', '_cache_metadata', 'op']: continue
                
                # Only treat as child node if it's an object with __dict__ but NOT an Enum
                if hasattr(val, '__dict__') and val is not n and not isinstance(val, Enum):
                    children.append((key, val))
                elif isinstance(val, list):
                    for i, child in enumerate(val):
                        if hasattr(child, '__dict__') and not isinstance(child, Enum):
                            children.append((f"{key}[{i}]", child))
        return children

    def _calculate_layout(self, n, x_offset, level, visited):
        if id(n) in visited: return x_offset
        visited.add(id(n))
        
        children_with_keys = self._get_children(n)
        children = [c[1] for c in children_with_keys]
        
        # Simple horizontal layout for children
        child_x = x_offset
        for child in children:
            child_x = self._calculate_layout(child, child_x, level + 1, visited)
            child_x += self.node_width + self.sibling_gap
            
        # Center parent over children
        if children:
            # Only consider children that were successfully laid out
            laid_out_children = [c for c in children if id(c) in self.layout_info]
            if laid_out_children:
                first_child_x = self.layout_info[id(laid_out_children[0])]['x']
                last_child_x = self.layout_info[id(laid_out_children[-1])]['x']
                x = (first_child_x + last_child_x) / 2
            else:
                x = x_offset
        else:
            x = x_offset
            
        y = level * (self.node_height + self.level_gap)
        self.layout_info[id(n)] = {'x': x, 'y': y, 'children': children_with_keys}
        
        return max(x, child_x - self.node_width - self.sibling_gap) if children else x

    def _draw_tree(self, n, visited):
        if id(n) in visited: return
        visited.add(id(n))
        
        if id(n) not in self.layout_info: return
        info = self.layout_info[id(n)]
        x, y = info['x'], info['y']
        
        # Determine color based on node type
        node_type = n.__class__.__name__
        bg_color = QColor("#2d2d2d")
        border_color = QColor("#569CD6") # Default Blue
        
        # Color Coding
        if any(keyword in node_type for keyword in ["Var", "Assignment", "Set", "Define"]):
            border_color = QColor("#C586C0") # Purple for Data/Assignments
        elif any(keyword in node_type for keyword in ["If", "While", "For", "Return", "Break", "Continue", "Try", "Catch"]):
            border_color = QColor("#D16969") # Red-ish for Control Flow
        elif any(keyword in node_type for keyword in ["Binary", "Unary", "Logic", "Comparison"]):
            border_color = QColor("#4EC9B0") # Teal for Expressions/Operators
        elif any(keyword in node_type for keyword in ["Call", "Function"]):
            border_color = QColor("#DCDCAA") # Yellow for Functions
        elif any(keyword in node_type for keyword in ["Literal", "Number", "String", "Boolean", "Null"]):
            border_color = QColor("#CE9178") # Orange-ish for Literals

        # Draw node box
        rect = QGraphicsRectItem(x, y, self.node_width, self.node_height)
        rect.setBrush(QBrush(bg_color))
        rect.setPen(QPen(border_color, 2))
        self.scene.addItem(rect)
        
        # Node Type (Title)
        type_text = QGraphicsTextItem(node_type)
        type_text.setDefaultTextColor(Qt.white)
        font = type_text.font()
        font.setBold(True)
        font.setPointSize(9)
        type_text.setFont(font)
        # Center horizontally, fixed top margin
        tw = type_text.boundingRect().width()
        type_text.setPos(x + (self.node_width - tw)/2, y + 5)
        self.scene.addItem(type_text)
        
        # Details
        details = ""
        try:
            if hasattr(n, 'value'): details = str(n.value)
            elif hasattr(n, 'name'): details = str(n.name)
            elif hasattr(n, 'op'): details = str(n.op)
            elif hasattr(n, 'var_name'): details = str(n.var_name)
            elif hasattr(n, 'attr_name'): details = f".{n.attr_name}"
            
            if node_type == "FunctionCall":
                details = f"{n.name}(...)"
            elif node_type == "VarDeclaration":
                details = f"var {n.name}"
        except: pass

        if details:
            details_text = QGraphicsTextItem(details)
            details_text.setDefaultTextColor(QColor("#CE9178"))
            # Truncate
            if len(details) > 20:
                details_text.setPlainText(details[:17] + "...")
            
            dw = details_text.boundingRect().width()
            details_text.setPos(x + (self.node_width - dw)/2, y + 22)
            self.scene.addItem(details_text)

        # Line/Col
        if hasattr(n, 'line'):
            loc_text = QGraphicsTextItem(f"L:{n.line} C:{n.column}")
            loc_text.setDefaultTextColor(QColor("#6A9955"))
            f = loc_text.font()
            f.setPointSize(7)
            loc_text.setFont(f)
            lw = loc_text.boundingRect().width()
            loc_text.setPos(x + (self.node_width - lw)/2, y + 40)
            self.scene.addItem(loc_text)

        # Draw lines to children
        for key, child in info['children']:
            if id(child) not in self.layout_info: continue
            child_info = self.layout_info[id(child)]
            line = QGraphicsLineItem(
                x + self.node_width / 2, y + self.node_height,
                child_info['x'] + self.node_width / 2, child_info['y']
            )
            line.setPen(QPen(QColor("#666"), 1))
            self.scene.addItem(line)
            
            # Key label on line
            label = QGraphicsTextItem(key)
            label.setDefaultTextColor(QColor("#999"))
            f = label.font()
            f.setPointSize(7)
            label.setFont(f)
            label.setPos((x + child_info['x'] + self.node_width)/2 - 20, (y + self.node_height + child_info['y'])/2 - 10)
            self.scene.addItem(label)
            
            self._draw_tree(child, visited)

class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("#569CD6")) # VS Code Blue
        keywordFormat.setFontWeight(QFont.Bold)
        keywords = ["var", "func", "if", "else", "while", "for", "return", 
                   "import_py", "import_aml", "try", "catch", "namespace", "spawn", 
                   "break", "continue", "in", "True", "False", "null", "meta"]
        for pattern in keywords:
            self.highlightingRules.append((f"\\b{pattern}\\b", keywordFormat))

        # Strings
        stringFormat = QTextCharFormat()
        stringFormat.setForeground(QColor("#CE9178")) # VS Code String Color
        self.highlightingRules.append(("\".*?\"", stringFormat))
        self.highlightingRules.append(("\'.*?\'", stringFormat))
        
        # Comments
        commentFormat = QTextCharFormat()
        commentFormat.setForeground(QColor("#6A9955")) # VS Code Comment Color
        self.highlightingRules.append(("//[^\n]*", commentFormat))

    def highlightBlock(self, text):
        import re
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)

class DebuggerWorker(QObject):
    step_signal = Signal(object, object) # node, env
    file_changed_signal = Signal(str, str) # filepath, source_code
    finished_signal = Signal()
    output_signal = Signal(str)

    def __init__(self, source_code, filepath):
        super().__init__()
        self.source_code = source_code
        self.filepath = os.path.abspath(filepath)
        self.interpreter = Interpreter()
        self.interpreter.set_debug_hook(self.debug_hook)
        self.paused = False
        self.step_mode = False
        self.lock = threading.Condition()
        self.running = True
        self.delay = 0
        self.current_file = self.filepath

    def run(self):
        # Redirect stdout
        import io
        from contextlib import redirect_stdout
        
        class StdoutRedirector:
            def __init__(self, signal):
                self.signal = signal
            def write(self, text):
                self.signal.emit(text)
            def flush(self):
                pass

        try:
            lexer = Lexer(self.source_code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            program = parser.parse()
            
            # Setup path for imports
            self.interpreter.aml_search_paths.append(os.path.dirname(self.filepath))
            
            # Manually push the main file context so the debugger knows where we are starting
            if hasattr(self.interpreter, 'push_file_context'):
                self.interpreter.push_file_context(self.filepath, self.source_code)
            
            with redirect_stdout(StdoutRedirector(self.output_signal)):
                self.interpreter.interpret(program)
        except Exception as e:
            self.output_signal.emit(f"Error: {e}\n")
        finally:
            if hasattr(self.interpreter, 'pop_file_context') and hasattr(self.interpreter, 'push_file_context'):
                 # Balance the manual push if interpret didn't crash before popping? 
                 # Actually interpret doesn't pop what it didn't push. We pushed it.
                 # But if interpret crashed, we might want to be clean.
                 pass
            self.finished_signal.emit()

    def debug_hook(self, interpreter, node, kind):
        if not self.running:
            return

        # Determine current file from interpreter context
        current_path = self.filepath
        current_source = self.source_code
        
        if hasattr(interpreter, '_file_ctx_stack') and interpreter._file_ctx_stack:
            ctx = interpreter._file_ctx_stack[-1]
            current_path = ctx.get('path', self.filepath)
            current_source = ctx.get('source', "")
        
        # If file changed, notify UI
        if current_path != self.current_file:
            self.current_file = current_path
            self.file_changed_signal.emit(current_path, current_source)

        # Check if we should pause
        should_pause = self.paused or self.step_mode
        
        if self.delay > 0:
            time.sleep(self.delay)

        if should_pause:
            # Emit signal to update UI with current state
            self.step_signal.emit(node, interpreter.environment)
            
            with self.lock:
                self.lock.wait() # Wait for UI to resume
                
        # Reset step mode so we don't pause on next instruction unless requested
        if self.step_mode:
             self.step_mode = False
             self.paused = True # Remain paused after step

    def resume(self):
        with self.lock:
            self.paused = False
            self.step_mode = False
            self.lock.notify()

    def step(self):
        with self.lock:
            self.paused = True
            self.step_mode = True
            self.lock.notify()
            
    def pause(self):
        self.paused = True

    def set_delay(self, seconds):
        self.delay = seconds

class AMLDebugger(QMainWindow):
    def __init__(self, initial_file=None):
        super().__init__()
        self.setWindowTitle("AML Debugger")
        self.resize(1400, 900)
        
        self.current_filepath = initial_file
        self.source_code = ""
        
        if self.current_filepath:
            self.load_file(self.current_filepath)
        else:
             self.source_code = "// Open a file to start debugging"
             self.current_filepath = "untitled.aml"

        # Map file paths to tab indices
        self.open_files = {} # path -> index

        self.setup_ui()
        self.worker_thread = None
        self.worker = None

    def load_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.source_code = f.read()
            self.current_filepath = os.path.abspath(path)
            self.setWindowTitle(f"AML Debugger - {self.current_filepath}")
            self.refresh_full_ast()
        except Exception as e:
            self.source_code = f"// Error loading file: {e}"

    def setup_ui(self):
        # Central Widget - Splitter
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        # Left Panel - Code Tabs
        self.code_tabs = QTabWidget()
        self.code_tabs.setTabsClosable(True)
        self.code_tabs.tabCloseRequested.connect(self.close_tab)
        splitter.addWidget(self.code_tabs)
        
        # Initial Tab
        self.add_code_tab(self.current_filepath, self.source_code)

        # Right Panel - Tabbed Info
        self.right_tabs = QTabWidget()
        splitter.addWidget(self.right_tabs)

        # Tab 1: AST Tree (Step)
        ast_widget = QWidget()
        ast_layout = QVBoxLayout()
        ast_widget.setLayout(ast_layout)
        self.ast_tree = QTreeWidget()
        self.ast_tree.setHeaderLabels(["Node Type", "Details"])
        ast_layout.addWidget(self.ast_tree)
        self.right_tabs.addTab(ast_widget, "AST Tree (Step)")

        # Tab 2: Full AST
        full_ast_widget = QWidget()
        full_ast_layout = QVBoxLayout()
        full_ast_widget.setLayout(full_ast_layout)
        self.full_ast_tree = QTreeWidget()
        self.full_ast_tree.setHeaderLabels(["Node Type", "Details"])
        full_ast_layout.addWidget(self.full_ast_tree)
        self.right_tabs.addTab(full_ast_widget, "Full AST")

        # Tab 3: AST Flowchart
        self.flowchart = FlowchartWidget()
        self.right_tabs.addTab(self.flowchart, "AST Flowchart")

        # Tab 4: Variables (All Data)
        vars_widget = QWidget()
        vars_layout = QVBoxLayout()
        vars_widget.setLayout(vars_layout)
        self.vars_tree = QTreeWidget()
        self.vars_tree.setHeaderLabels(["Variable", "Value", "Type"])
        self.vars_tree.itemDoubleClicked.connect(self.modify_variable)
        vars_layout.addWidget(self.vars_tree)
        self.right_tabs.addTab(vars_widget, "Variables & Data")

        # Tab 3: Output Console
        console_widget = QWidget()
        console_layout = QVBoxLayout()
        console_widget.setLayout(console_layout)
        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)
        console_layout.addWidget(self.console_output)
        self.right_tabs.addTab(console_widget, "Console Output")

        # Toolbar
        self.create_toolbar()
        
        # Menu Bar
        self.create_menu()

        # Style
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

    def create_toolbar(self):
        toolbar = self.addToolBar("Debug")
        
        self.btn_run = QPushButton("Run / Resume")
        self.btn_run.clicked.connect(self.on_run)
        toolbar.addWidget(self.btn_run)
        
        self.btn_step = QPushButton("Step")
        self.btn_step.clicked.connect(self.on_step)
        self.btn_step.setEnabled(False)
        toolbar.addWidget(self.btn_step)
        
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self.on_pause)
        self.btn_pause.setEnabled(False)
        toolbar.addWidget(self.btn_pause)

        toolbar.addWidget(QLabel("  Speed: "))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems([
            "Fast (0s)", 
            "Very Fast (0.01s)", 
            "Fast (0.05s)", 
            "Normal (0.1s)", 
            "Slow (0.5s)", 
            "Slower (1.0s)",
            "Crawl (2.0s)",
            "Very Slow (9.0s)"
        ])
        self.speed_combo.currentIndexChanged.connect(self.on_speed_change)
        toolbar.addWidget(self.speed_combo)

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open File...", self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_file_dialog(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open AML File", "", "AML Files (*.aml);;All Files (*)")
        if fname:
            self.load_file(fname)
            # Close existing tabs and reset
            self.code_tabs.clear()
            self.open_files.clear()
            self.add_code_tab(self.current_filepath, self.source_code)
            self.console_output.clear()
            self.ast_tree.clear()
            self.vars_tree.clear()

    def add_code_tab(self, filepath, content):
        if filepath in self.open_files:
            self.code_tabs.setCurrentIndex(self.open_files[filepath])
            return self.code_tabs.widget(self.open_files[filepath])
            
        editor = QTextEdit()
        editor.setPlainText(content)
        editor.setReadOnly(True)
        editor.setFont(QFont("Consolas", 12))
        Highlighter(editor.document())
        
        filename = os.path.basename(filepath)
        index = self.code_tabs.addTab(editor, filename)
        self.open_files[filepath] = index
        self.code_tabs.setCurrentIndex(index)
        return editor

    def close_tab(self, index):
        # Don't close if it's the only tab
        if self.code_tabs.count() <= 1: return
        
        # Find filepath for this index
        path_to_remove = None
        for path, idx in self.open_files.items():
            if idx == index:
                path_to_remove = path
                break
        
        if path_to_remove:
            del self.open_files[path_to_remove]
            # Reindex remaining
            for p, i in self.open_files.items():
                if i > index:
                    self.open_files[p] = i - 1
                    
        self.code_tabs.removeTab(index)

    def on_run(self):
        if self.worker is None:
            # Get current editor content
            current_editor = self.code_tabs.currentWidget()
            if not current_editor: return
            
            source = current_editor.toPlainText()
            # If we are in the main file tab, use self.current_filepath
            # But the user might have switched tabs.
            # We should always start from the main file loaded.
            
            self.console_output.clear()
            self.worker = DebuggerWorker(self.source_code, self.current_filepath)
            self.worker_thread = QThread()
            self.worker.moveToThread(self.worker_thread)
            
            self.worker_thread.started.connect(self.worker.run)
            self.worker.step_signal.connect(self.on_step_update)
            self.worker.file_changed_signal.connect(self.on_file_changed)
            self.worker.output_signal.connect(self.on_output)
            self.worker.finished_signal.connect(self.on_finished)
            
            self.worker_thread.start()
            self.btn_run.setText("Resume")
            self.btn_pause.setEnabled(True)
            self.btn_step.setEnabled(True)
        else:
            # Resume existing
            self.worker.resume()

    def on_step(self):
        if self.worker:
            self.worker.step()

    def on_pause(self):
        if self.worker:
            self.worker.pause()

    def on_speed_change(self, index):
        if not self.worker: return
        delays = [0, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0,9.0]
        if index < len(delays):
            self.worker.set_delay(delays[index])

    def on_output(self, text):
        self.console_output.moveCursor(QTextCursor.End)
        self.console_output.insertPlainText(text)
        self.console_output.moveCursor(QTextCursor.End)

    def on_finished(self):
        self.console_output.appendHtml("<br><b>Execution Finished</b>")
        self.worker_thread.quit()
        self.worker_thread.wait()
        self.worker = None
        self.worker_thread = None
        self.btn_run.setText("Run")
        self.btn_pause.setEnabled(False)
        self.btn_step.setEnabled(False)

    def on_file_changed(self, filepath, source):
        # Open the file in a new tab or switch to it
        self.add_code_tab(filepath, source)

    def on_step_update(self, node, env):
        # 1. Determine active file and highlight line
        # The worker guarantees we are in the correct file because of on_file_changed
        # But we need to make sure we are focusing the right tab.
        
        current_path = self.worker.current_file
        if current_path in self.open_files:
            idx = self.open_files[current_path]
            self.code_tabs.setCurrentIndex(idx)
            editor = self.code_tabs.widget(idx)
            
            if hasattr(node, 'line') and node.line > 0:
                cursor = QTextCursor(editor.document().findBlockByLineNumber(node.line - 1))
                editor.setTextCursor(cursor)
                
                # Highlight line background
                selection = QTextEdit.ExtraSelection()
                line_color = QColor(Qt.yellow).lighter(160)
                selection.format.setBackground(line_color)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = cursor
                selection.cursor.clearSelection()
                editor.setExtraSelections([selection])

        # 2. Update Variables
        self.update_variables(env)

        # 3. Update AST
        self.update_ast(node)

    def update_variables(self, env):
        self.vars_tree.clear()
        
        # Traverse environments up to global
        current = env
        scopes = []
        while current:
            scopes.append(current)
            current = current.enclosing
            
        for i, scope in enumerate(scopes):
            scope_name = "Global" if scope.enclosing is None else f"Scope {len(scopes)-i}"
            parent = QTreeWidgetItem(self.vars_tree, [scope_name, "", ""])
            parent.setExpanded(True)
            
            for name, value in scope.values.items():
                val_str = str(value)
                type_str = type(value).__name__
                item = QTreeWidgetItem(parent, [name, val_str, type_str])
                item.setFlags(item.flags() | Qt.ItemIsEditable)

    def modify_variable(self, item, column):
        # Only allow value modification (column 1) and only for variable items (depth 1)
        if column != 1 or item.parent() is None: return
        
        var_name = item.text(0)
        current_val = item.text(1)
        
        from PySide6.QtWidgets import QInputDialog
        new_val_str, ok = QInputDialog.getText(self, f"Edit {var_name}", "New Value:", text=current_val)
        
        if ok and new_val_str != current_val:
            # Parse value
            new_val = self._parse_value(new_val_str)
            
            # Update in environment logic (same as before)
            if self.worker and self.worker.interpreter:
                env = self.worker.interpreter.environment
                
                scope_index = self.vars_tree.indexOfTopLevelItem(item.parent())
                
                current = env
                scopes = []
                while current:
                    scopes.append(current)
                    current = current.enclosing
                
                if 0 <= scope_index < len(scopes):
                    target_env = scopes[scope_index]
                    target_env.values[var_name] = new_val
                    item.setText(1, str(new_val))
                    item.setText(2, type(new_val).__name__)

    def _parse_value(self, s):
        s = s.strip()
        if s == "null": return None
        if s == "True": return True
        if s == "False": return False
        if s.startswith('"') and s.endswith('"'): return s[1:-1]
        if s.startswith("'") and s.endswith("'"): return s[1:-1]
        try:
            if '.' in s: return float(s)
            return int(s)
        except:
            return s


    def update_ast(self, node):
        self.ast_tree.clear()
        self._populate_ast_tree(node, self.ast_tree, set(), 0)
        # Update flowchart if it's the active tab or just update it anyway
        self.flowchart.set_ast(node)

    def refresh_full_ast(self):
        if not self.source_code: return
        try:
            lexer = Lexer(self.source_code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            program = parser.parse()
            
            self.full_ast_tree.clear()
            self._populate_ast_tree(program, self.full_ast_tree, set(), 0)
            self.flowchart.set_ast(program)
        except Exception as e:
            self.full_ast_tree.clear()
            QTreeWidgetItem(self.full_ast_tree, ["Error", str(e)])

    def _populate_ast_tree(self, n, parent, visited, depth):
        if depth > 100: return # Safety limit
        if id(n) in visited: return
        visited.add(id(n))
        
        name = n.__class__.__name__
        details = ""
        
        # Comprehensive value extraction
        try:
            if hasattr(n, 'value'): details = str(n.value)
            elif hasattr(n, 'name'): details = str(n.name)
            elif hasattr(n, 'op'): details = str(n.op)
            elif hasattr(n, 'var_name'): details = str(n.var_name)
            elif hasattr(n, 'attr_name'): details = f".{n.attr_name}"
            
            # Context-specific details
            if name == "FunctionCall":
                details = f"{n.name}(...)"
            elif name == "VarDeclaration":
                details = f"var {n.name}"
            elif name == "Assignment":
                details = "Assign"
            elif name == "BinaryOperation":
                details = str(n.op)
        except:
            pass
        
        item = QTreeWidgetItem(parent, [name, details])
        item.setExpanded(True)
        
        # Add children reflectively
        if hasattr(n, '__dict__'):
            # Priority keys for children
            keys = list(n.__dict__.keys())
            for pk in ['condition', 'if_body', 'else_body', 'iterable', 'body', 'left', 'right', 'expr', 'value', 'target']:
                if pk in keys:
                    keys.remove(pk)
                    keys.insert(0, pk)

            for key in keys:
                val = n.__dict__[key]
                if key in ['token', 'line', 'column', 'parent', 'enclosing', 'interpreter', '_cache_metadata', 'op']: continue
                
                if hasattr(val, '__dict__') and val is not n and not isinstance(val, Enum): # Is an AST node
                    self._populate_ast_tree(val, item, visited, depth + 1)
                elif isinstance(val, list):
                    # Check if list contains AST nodes or just data
                    is_node_list = False
                    if val and hasattr(val[0], '__dict__') and not isinstance(val[0], Enum):
                         is_node_list = True
                    
                    if is_node_list or val:
                         list_item = QTreeWidgetItem(item, [key, f"List[{len(val)}]"])
                         for child in val:
                             if hasattr(child, '__dict__') and child is not n:
                                 self._populate_ast_tree(child, list_item, visited, depth + 1)


from PySide6.QtGui import QTextFormat

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Dark Theme Palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.black)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    app.setPalette(palette)
    
    # Additional Stylesheet for consistency
    app.setStyleSheet("""
        QToolTip { 
            color: #ffffff; 
            background-color: #2a82da; 
            border: 1px solid white; 
        }
        QTabWidget::pane {
            border: 1px solid #444;
            background-color: #2d2d2d;
        }
        QTabBar::tab {
            background: #353535;
            color: #b0b0b0;
            border: 1px solid #1e1e1e;
            padding: 5px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background: #1e1e1e;
            color: white;
            border-bottom-color: #1e1e1e;
        }
        QHeaderView::section {
            background-color: #353535;
            color: white;
            padding: 4px;
            border: 1px solid #444;
        }
        QTreeWidget, QListWidget, QTableWidget {
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: 1px solid #333;
        }
        QTreeWidget::item:hover {
            background-color: #2a2d2e;
        }
        QTreeWidget::item:selected {
            background-color: #37373d;
        }
        QTextEdit, QPlainTextEdit {
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: 1px solid #333;
        }
        QMenu {
            background-color: #2d2d2d;
            color: white;
            border: 1px solid #444;
        }
        QMenu::item:selected {
            background-color: #094771;
        }
        QSplitter::handle {
            background-color: #333;
        }
    """)

    # Check for command line argument
    initial_file = "all_features_test.aml"
    if len(sys.argv) > 1:
        initial_file = sys.argv[1]

    window = AMLDebugger(initial_file)
    window.show()
    sys.exit(app.exec())
