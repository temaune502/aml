
import os
from .parser import (
    Program, VarDeclaration, FunctionDeclaration, NamespaceDeclaration,
    ImportAml, ImportPy, Assignment, IfStatement, WhileStatement, ForStatement,
    TryCatchStatement, ParallelBlock, ReturnStatement, FunctionCall, MethodCall,
    BinaryOperation, UnaryOperation, Identifier, Number, String, Boolean, Null,
    ListLiteral, DictLiteral
)
from .tokens import TokenType

class Symbol:
    def __init__(self, name, type_info='any', is_const=False, decl_node=None, index=-1):
        self.name = name
        self.type_info = type_info  # 'number', 'string', 'boolean', 'list', 'dict', 'function', 'namespace', 'any'
        self.is_const = is_const
        self.decl_node = decl_node
        self.index = index

class Scope:
    def __init__(self, name="global", parent=None):
        self.name = name
        self.parent = parent
        self.symbols = {}
        self.children = []
        self.next_index = 0

    def define(self, name, symbol):
        if symbol.index == -1:
            symbol.index = self.next_index
            self.next_index += 1
        self.symbols[name] = symbol
        return symbol

    def lookup(self, name):
        depth = 0
        curr = self
        while curr:
            if name in curr.symbols:
                return curr.symbols[name], depth
            curr = curr.parent
            depth += 1
        return None, -1

    def lookup_local(self, name):
        if name in self.symbols:
            return self.symbols[name], 0
        return None, -1

class AnalysisResult:
    def __init__(self):
        self.symbols = Scope()
        self.imports_aml = set()
        self.imports_py = set()
        self.errors = []
        self.warnings = []

class StaticAnalyzer:
    def __init__(self, search_paths=None):
        self.result = AnalysisResult()
        self.current_scope = self.result.symbols
        self.search_paths = search_paths or [os.getcwd()]
        self.analyzed_modules = set()
        self._dispatch = {
            Program: self.analyze_Program,
            VarDeclaration: self.analyze_VarDeclaration,
            FunctionDeclaration: self.analyze_FunctionDeclaration,
            NamespaceDeclaration: self.analyze_NamespaceDeclaration,
            ImportAml: self.analyze_ImportAml,
            ImportPy: self.analyze_ImportPy,
            Assignment: self.analyze_Assignment,
            IfStatement: self.analyze_IfStatement,
            WhileStatement: self.analyze_WhileStatement,
            ForStatement: self.analyze_ForStatement,
            TryCatchStatement: self.analyze_TryCatchStatement,
            ParallelBlock: self.analyze_ParallelBlock,
            ReturnStatement: self.analyze_ReturnStatement,
            FunctionCall: self.analyze_FunctionCall,
            MethodCall: self.analyze_MethodCall,
            BinaryOperation: self.analyze_BinaryOperation,
            UnaryOperation: self.analyze_UnaryOperation,
            Identifier: self.analyze_Identifier,
            ListLiteral: self.analyze_ListLiteral,
            DictLiteral: self.analyze_DictLiteral,
        }

    def analyze(self, node):
        if node is None: return None
        
        # Try to use dispatch first
        method = self._dispatch.get(type(node))
        if method:
            res = method(node)
            return res if res is not None else node
        
        # Fallback to generic traversal for nodes not in dispatch
        if isinstance(node, Program):
            for i, stmt in enumerate(node.statements):
                node.statements[i] = self.analyze(stmt)
        elif isinstance(node, BinaryOperation):
            node.left = self.analyze(node.left)
            node.right = self.analyze(node.right)
            # Constant folding for binary operations
            return self._fold_binary(node)
        elif isinstance(node, UnaryOperation):
            node.expr = self.analyze(node.expr)
            # Constant folding for unary operations
            return self._fold_unary(node)
        elif isinstance(node, ListLiteral):
            for i, el in enumerate(node.elements):
                node.elements[i] = self.analyze(el)
        elif isinstance(node, DictLiteral):
            for i, (k, v) in enumerate(node.elements):
                node.elements[i] = (self.analyze(k), self.analyze(v))
        
        return node

    def _fold_binary(self, node):
        if isinstance(node.left, (Number, String, Boolean, Null)) and \
           isinstance(node.right, (Number, String, Boolean, Null)):
            # Use the existing folder in Parser as a reference or implement here
            from .parser import Parser
            p = Parser([]) # Dummy parser for access to _try_fold_binary
            folded = p._try_fold_binary(node.left, node.op, node.right)
            if folded:
                return folded
        
        # Additional folding for constants like true and true, false or true
        if isinstance(node.left, Boolean) and isinstance(node.right, Boolean):
            if node.op == TokenType.AND:
                return Boolean(node.left.value and node.right.value, token=node.token)
            if node.op == TokenType.OR:
                return Boolean(node.left.value or node.right.value, token=node.token)
                
        return node

    def _fold_unary(self, node):
        if isinstance(node.expr, (Number, String, Boolean)):
            if node.op == TokenType.MINUS and isinstance(node.expr, Number):
                return Number(-node.expr.value, token=node.token)
            if node.op == TokenType.NOT:
                # Basic truthiness for folding
                val = not node.expr.value
                return Boolean(val, token=node.token)
        return node

    def analyze_Program(self, node):
        for i, stmt in enumerate(node.statements):
            node.statements[i] = self.analyze(stmt)
        return node

    def analyze_ImportPy(self, node):
        for mod in node.modules:
            self.result.imports_py.add(mod)
        return node

    def analyze_ImportAml(self, node):
        from .lexer import Lexer
        from .parser import Parser

        for mod in node.modules:
            self.result.imports_aml.add(mod)
            if mod in self.analyzed_modules:
                continue
            
            self.analyzed_modules.add(mod)
            
            # Find the file
            normalized_name = mod.replace('\\', os.path.sep).replace('/', os.path.sep).replace('.', os.path.sep)
            file_path = None
            for base in self.search_paths:
                candidate = os.path.join(base, f"{normalized_name}.aml")
                if os.path.exists(candidate):
                    file_path = candidate
                    break
            
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    lexer = Lexer(source)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    module_ast = parser.parse()
                    
                    # Analyze the module AST (this will return the analyzed AST)
                    module_ast = self.analyze(module_ast)
                    # We don't replace anything here as it's an import, but we could store it
                except Exception as e:
                    self.result.errors.append(f"Error analyzing module '{mod}': {e}")
            else:
                self.result.warnings.append(f"AML module '{mod}' not found for static analysis")
        return node

    def analyze_VarDeclaration(self, node):
        node.value = self.analyze(node.value)
        type_info = self._infer_type(node.value)
        
        # Check if it's a constant value for basic constant propagation
        # We only mark it as constant if it's actually declared as const (if AML supported it)
        # or if we were doing proper SSA/flow analysis. 
        # For now, let's disable this aggressive propagation as it breaks loops.
        is_const = False # isinstance(node.value, (Number, String, Boolean, Null))
        
        if node.name in self.current_scope.symbols:
            self.result.warnings.append(f"Redeclaration of variable '{node.name}' at line {node.line}")
        
        symbol = Symbol(node.name, type_info=type_info, is_const=is_const, decl_node=node)
        self.current_scope.define(node.name, symbol)
        
        # Attach resolution info to the node
        node.resolved_depth = 0 # Declarations are always in current scope
        node.resolved_index = symbol.index
        return node

    def analyze_Identifier(self, node):
        sym, depth = self.current_scope.lookup(node.name)
        if not sym:
            # We don't warn for all undefineds here because some might be built-ins
            # that are not yet in the static symbol table.
            pass
        else:
            node.resolved_depth = depth
            node.resolved_index = sym.index
            
            # Basic constant propagation: replace identifier with its constant value if available
            if sym.is_const and hasattr(sym.decl_node, 'value') and isinstance(sym.decl_node.value, (Number, String, Boolean, Null)):
                # Return a copy of the literal to replace the identifier
                val = sym.decl_node.value
                if isinstance(val, Number): return Number(val.value, token=node.token)
                if isinstance(val, String): return String(val.value, token=node.token)
                if isinstance(val, Boolean): return Boolean(val.value, token=node.token)
                if isinstance(val, Null): return Null(token=node.token)
                
        return node

    def analyze_FunctionDeclaration(self, node):
        symbol = Symbol(node.name, type_info='function', decl_node=node)
        self.current_scope.define(node.name, symbol)
        
        # New scope for function body
        prev_scope = self.current_scope
        self.current_scope = Scope(name=node.name, parent=prev_scope)
        prev_scope.children.append(self.current_scope)
        
        # Define params in function scope
        for i, p in enumerate(node.params or []):
            p_name = p if isinstance(p, str) else p[0]
            sym, _ = self.current_scope.lookup_local(p_name)
            if sym:
                self.result.warnings.append(f"Redeclaration of parameter '{p_name}' at line {node.line}")
            # Params also get indices
            self.current_scope.define(p_name, Symbol(p_name, type_info='any'))
            
        for i, stmt in enumerate(node.body):
            node.body[i] = self.analyze(stmt)
            
        # Store the number of local variables for the interpreter
        node.locals_count = self.current_scope.next_index
        
        self.current_scope = prev_scope
        return node

    def analyze_NamespaceDeclaration(self, node):
        prev_scope = self.current_scope
        ns_name = ".".join(node.name) if isinstance(node.name, list) else node.name
        
        # Check if namespace already exists in current scope
        sym, depth = self.current_scope.lookup_local(ns_name)
        if sym and sym.type_info == 'namespace':
            new_scope = sym.decl_node # We store the Scope in decl_node for namespaces during analysis
        else:
            new_scope = Scope(name=ns_name, parent=self.current_scope)
            self.current_scope.define(ns_name, Symbol(ns_name, type_info='namespace', decl_node=new_scope))
            self.current_scope.children.append(new_scope)
        
        self.current_scope = new_scope
        for i, stmt in enumerate(node.body):
            node.body[i] = self.analyze(stmt)
        self.current_scope = prev_scope
        return node

    def analyze_Assignment(self, node):
        node.value = self.analyze(node.value)
        
        if not node.target_expr:
            # Simple assignment: name = value
            sym, depth = self.current_scope.lookup(node.name)
            if not sym:
                self.result.warnings.append(f"Assignment to undeclared variable '{node.name}' at line {node.line}")
                sym = self.current_scope.define(node.name, Symbol(node.name, type_info='any'))
                depth = 0
            
            node.resolved_depth = depth
            node.resolved_index = sym.index
            
            val_type = self._infer_type(node.value)
            if sym and val_type != 'any':
                sym.type_info = val_type
        else:
            node.target_expr = self.analyze(node.target_expr)
            
        return node

    def analyze_IfStatement(self, node):
        node.condition = self.analyze(node.condition)
        for i, stmt in enumerate(node.if_body):
            node.if_body[i] = self.analyze(stmt)
        if node.else_body:
            for i, stmt in enumerate(node.else_body):
                node.else_body[i] = self.analyze(stmt)
        return node

    def analyze_WhileStatement(self, node):
        node.condition = self.analyze(node.condition)
        for i, stmt in enumerate(node.body):
            node.body[i] = self.analyze(stmt)
        return node

    def analyze_ForStatement(self, node):
        # For iterator variable
        if node.var_name in self.current_scope.symbols:
             pass # Already exists, fine for for-loop
        self.current_scope.define(node.var_name, Symbol(node.var_name, type_info='any'))
        
        node.iterable = self.analyze(node.iterable)
        for i, stmt in enumerate(node.body):
            node.body[i] = self.analyze(stmt)
        return node

    def analyze_TryCatchStatement(self, node):
        for i, stmt in enumerate(node.try_body):
            node.try_body[i] = self.analyze(stmt)
        if node.catch_body:
            if node.error_var:
                self.current_scope.define(node.error_var, Symbol(node.error_var, type_info='any'))
            for i, stmt in enumerate(node.catch_body):
                node.catch_body[i] = self.analyze(stmt)
        return node

    def analyze_ParallelBlock(self, node):
        for i, stmt in enumerate(node.body):
            node.body[i] = self.analyze(stmt)
        return node

    def analyze_ReturnStatement(self, node):
        if node.value:
            node.value = self.analyze(node.value)
        return node

    def analyze_FunctionCall(self, node):
        # Check if function name is a string (direct call)
        if isinstance(node.name, str):
            sym, depth = self.current_scope.lookup(node.name)
            if sym:
                # Track usage if needed
                pass
        else:
            node.name = self.analyze(node.name)
        
        for i, arg in enumerate(node.args):
            node.args[i] = self.analyze(arg)
        for i, (k, val) in enumerate(node.kwargs):
            node.kwargs[i] = (k, self.analyze(val))
        return node

    def analyze_MethodCall(self, node):
        if node.object_expr:
            node.object_expr = self.analyze(node.object_expr)
        
        for i, arg in enumerate(node.args):
            node.args[i] = self.analyze(arg)
        for i, (k, val) in enumerate(node.kwargs):
            node.kwargs[i] = (k, self.analyze(val))
        return node

    def analyze_BinaryOperation(self, node):
        node.left = self.analyze(node.left)
        node.right = self.analyze(node.right)
        
        left_t = self._infer_type(node.left)
        right_t = self._infer_type(node.right)
        
        # Basic type check for obvious errors
        if left_t and right_t and left_t != 'any' and right_t != 'any':
            if left_t != right_t:
                # Some operations allow mixed types (e.g. string + number)
                if node.op == TokenType.PLUS and (left_t == 'string' or right_t == 'string'):
                    pass
                else:
                    self.result.warnings.append(
                        f"Potential type mismatch: '{left_t}' {node.op} '{right_t}' at line {node.line}"
                    )
        return self._fold_binary(node)

    def analyze_UnaryOperation(self, node):
        node.expr = self.analyze(node.expr)
        return self._fold_unary(node)

    def analyze_ListLiteral(self, node):
        for i, el in enumerate(node.elements):
            node.elements[i] = self.analyze(el)
        return node

    def analyze_DictLiteral(self, node):
        for i, (k, v) in enumerate(node.elements):
            node.elements[i] = (self.analyze(k), self.analyze(v))
        return node

    def _infer_type(self, node):
        if isinstance(node, Number): return 'number'
        if isinstance(node, String): return 'string'
        if isinstance(node, Boolean): return 'boolean'
        if isinstance(node, Null): return 'null'
        if isinstance(node, ListLiteral): return 'list'
        if isinstance(node, DictLiteral): return 'dict'
        if isinstance(node, Identifier):
            sym, depth = self.current_scope.lookup(node.name)
            return sym.type_info if sym else 'any'
        if isinstance(node, BinaryOperation):
            # Simplify: if any operand is string and op is PLUS, result is string
            if node.op == TokenType.PLUS:
                lt = self._infer_type(node.left)
                rt = self._infer_type(node.right)
                if lt == 'string' or rt == 'string': return 'string'
                return 'number'
            return 'number' # Most other ops result in number or boolean
        return 'any'
