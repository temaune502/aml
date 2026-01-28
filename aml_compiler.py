import json
import os
import base64
from enum import Enum
from aml.lexer import Lexer
from aml.parser import *

class AMLCompiler:
    def __init__(self, search_paths=None):
        self.search_paths = search_paths or ["."]
        self.modules = {} # path -> ast_dict
        self.parsed_asts = {} # path -> AST object
        self.obfuscation_map = {}
        self.declared_names = set()
        self.id_counter = 0
        self.reserved_names = {
            # Built-ins
            'print', 'len', 'str', 'int', 'float', 'bool', 'type', 'exit', 'exit_now', 'tick', 'import',
            'signal', 'effect', 'global', 'spec', 'runtime', 'meta',
            'args', 'range', 'list', 'dict', 'set'
        }

    def _get_obfuscated_name(self, name):
        if name in self.reserved_names or name.startswith("__"):
            return name
        if name not in self.declared_names:
            return name
        if name not in self.obfuscation_map:
            self.obfuscation_map[name] = f"v{self.id_counter}"
            self.id_counter += 1
        return self.obfuscation_map[name]

    def ast_to_dict(self, node, obfuscate=False):
        if node is None: return None
        if isinstance(node, (int, float, str, bool)): return node
        if isinstance(node, Enum):
            return {"_e": node.__class__.__name__, "v": node.name}
        if isinstance(node, list): return [self.ast_to_dict(item, obfuscate) for item in node]
        if isinstance(node, tuple): return [self.ast_to_dict(item, obfuscate) for item in node]

        if not isinstance(node, AST):
            return str(node)

        data = {"_t": node.__class__.__name__}
        
        for attr, value in vars(node).items():
            if attr in ('token', 'line', 'column'): continue
            
            # Obfuscation logic
            if obfuscate:
                if isinstance(node, (VarDeclaration, ConstDeclaration, FunctionDeclaration, NamespaceDeclaration)) and attr == 'name':
                    value = self._get_obfuscated_name(value)
                elif isinstance(node, Identifier) and attr == 'name':
                    value = self._get_obfuscated_name(value)
                elif isinstance(node, FunctionCall) and attr == 'name':
                    value = self._get_obfuscated_name(value)
                elif isinstance(node, (MethodCall, AttributeAccess)) and attr in ('object_name', 'attr_name', 'method_name'):
                    # Obfuscate object names and members
                    if value:
                        value = self._get_obfuscated_name(value)
                elif isinstance(node, Assignment) and attr == 'name' and value:
                    value = self._get_obfuscated_name(value)
                elif isinstance(node, (ListComprehension, DictComprehension, ForStatement)) and attr == 'var_name':
                    value = self._get_obfuscated_name(value)

            data[attr] = self.ast_to_dict(value, obfuscate)
        return data

    def collect_declarations(self, node):
        if node is None: return
        if isinstance(node, list):
            for item in node: self.collect_declarations(item)
            return
        if not isinstance(node, AST): return

        if isinstance(node, (VarDeclaration, ConstDeclaration, FunctionDeclaration, NamespaceDeclaration)):
            if node.name: self.declared_names.add(node.name)
        if isinstance(node, FunctionDeclaration):
            for param in node.params:
                self.declared_names.add(param)
        if isinstance(node, (ListComprehension, DictComprehension, ForStatement)):
            if node.var_name: self.declared_names.add(node.var_name)
        
        for attr, value in vars(node).items():
            if attr in ('token', 'line', 'column'): continue
            self.collect_declarations(value)

    def _find_dependencies(self, node, deps):
        if node is None: return
        if isinstance(node, list):
            for item in node: self._find_dependencies(item, deps)
            return
        if not isinstance(node, AST): return

        if isinstance(node, ImportPy):
            for mod in node.modules:
                name = mod[1] if isinstance(mod, tuple) else mod.split('.')[-1]
                self.reserved_names.add(name)
        elif isinstance(node, ImportAml):
            for mod in node.modules:
                name = mod[1] if isinstance(mod, tuple) else mod.split('.')[-1]
                self.reserved_names.add(name)
                deps.append(mod[0] if isinstance(mod, tuple) else mod)
        elif isinstance(node, FunctionCall) and node.name == "import":
            if node.args and isinstance(node.args[0], String):
                deps.append(node.args[0].value)
        
        for attr, value in vars(node).items():
            if attr in ('token', 'line', 'column'): continue
            self._find_dependencies(value, deps)

    def _discover_and_parse(self, file_path):
        abs_path = os.path.abspath(file_path)
        if abs_path in self.parsed_asts:
            return
        
        with open(abs_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        self.parsed_asts[abs_path] = program
        
        # Track dependencies and reserve names
        deps = []
        self._find_dependencies(program, deps)
        
        # Recurse
        for dep in deps:
            dep_path = self._resolve_aml_path(dep, os.path.dirname(abs_path))
            if dep_path:
                self._discover_and_parse(dep_path)

    def compile_file(self, file_path, obfuscate=True):
        # 1. Discover and parse all modules recursively
        self._discover_and_parse(file_path)
        
        # 2. Collect declarations for obfuscation (across all modules)
        if obfuscate:
            for program in self.parsed_asts.values():
                self.collect_declarations(program)
        
        # 3. Serialize all modules
        for path, program in self.parsed_asts.items():
            self.modules[path] = self.ast_to_dict(program, obfuscate)

    def _resolve_aml_path(self, module_name, current_dir):
        normalized = module_name.replace('.', os.path.sep).replace('/', os.path.sep).replace('\\', os.path.sep)
        for base in [current_dir] + self.search_paths:
            candidate = os.path.join(base, f"{normalized}.aml")
            if os.path.exists(candidate):
                return os.path.abspath(candidate)
        return None

    def save(self, output_path, entry_file):
        data = {
            "version": "1.0",
            "entry": os.path.abspath(entry_file),
            "modules": self.modules,
            "obfuscated": True
        }
        json_str = json.dumps(data)
        # Simple "encryption" / encoding to make it not easily readable but not using pickle
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(encoded)
        print(f"Compiled to {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python aml_compiler.py <entry_file.aml> [output.caml]")
        sys.exit(1)
    
    entry = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else entry.replace(".aml", ".caml")
    
    compiler = AMLCompiler()
    compiler.compile_file(entry, obfuscate=False)
    compiler.save(out, entry)
