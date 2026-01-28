# Interpreter for AML language
# Executes the Abstract Syntax Tree (AST)

import importlib.util
import os
import sys
from .parser import *
import threading
import re
import hashlib
import json
import pickle
import base64


# Create a unique sentinel for "not provided" arguments
MISSING_ARG = object()


class Signal:
    __slots__ = ('_value', '_interpreter', '_subscribers')
    def __init__(self, value, interpreter):
        self._value = value
        self._interpreter = interpreter
        self._subscribers = set()

    def get(self):
        # Register current effect as a subscriber
        if hasattr(self._interpreter, '_current_effect') and self._interpreter._current_effect:
            self._subscribers.add(self._interpreter._current_effect)
        return self._value

    def set(self, new_value):
        if self._value != new_value:
            self._value = new_value
            # Trigger all subscriber effects
            for effect in list(self._subscribers):
                # If effect is already running, avoid recursion
                if effect != getattr(self._interpreter, '_current_effect', None):
                    effect.run()

    def __repr__(self):
        return f"<Signal value={self._value}>"

class Effect:
    __slots__ = ('func', 'interpreter')
    def __init__(self, func, interpreter):
        self.func = func
        self.interpreter = interpreter
        # Run immediately to collect dependencies
        self.run()
    
    def run(self):
        prev = getattr(self.interpreter, '_current_effect', None)
        self.interpreter._current_effect = self
        try:
            if isinstance(self.func, Function):
                self.func.call(self.interpreter, [])
            elif callable(self.func):
                self.func()
        finally:
            self.interpreter._current_effect = prev

class Environment:
    __slots__ = ('values', 'slots', 'enclosing', '_version', 'name_to_index', 'constants')
    _MISSING = object()

    def __init__(self, enclosing=None, size=0):
        self.values = {}
        self.slots = [None] * size
        self.name_to_index = {}
        self.enclosing = enclosing
        self.constants = set()
        self._version = 0

    def define(self, name, value, index=-1, is_const=False):
        if is_const:
            self.constants.add(name)
        
        if index != -1:
            if index >= len(self.slots):
                self.slots.extend([None] * (index - len(self.slots) + 1))
            self.slots[index] = value
            self.name_to_index[name] = index
        
        self.values[name] = value
        self._version += 1

    def get_at(self, depth, index):
        curr = self
        for _ in range(depth):
            curr = curr.enclosing
            if not curr: return None
        
        if index < len(curr.slots):
            return curr.slots[index]
        return None

    def assign_at(self, depth, index, value, name=None):
        curr = self
        for _ in range(depth):
            curr = curr.enclosing
            if not curr: return
        
        if name and name in curr.constants:
            raise RuntimeError(f"Cannot reassign constant '{name}'")

        if index >= len(curr.slots):
            curr.slots.extend([None] * (index - len(curr.slots) + 1))
        
        # print(f"[DEBUG] Environment.assign_at: depth={depth}, index={index}, value={value}, name={name}")
        curr.slots[index] = value
        if name:
            curr.values[name] = value
        curr._version += 1

    def get(self, name):
        curr = self
        while curr:
            if name in curr.values:
                return curr.values[name]
            curr = curr.enclosing
        
        raise RuntimeError(f"Undefined variable '{name}'")
    
    def assign(self, name, value):
        curr = self
        while curr:
            if name in curr.values:
                if name in curr.constants:
                    raise RuntimeError(f"Cannot reassign constant '{name}'")
                curr.values[name] = value
                # Sync with slots if it has an index
                if name in curr.name_to_index:
                    idx = curr.name_to_index[name]
                    if idx < len(curr.slots):
                        curr.slots[idx] = value
                curr._version += 1
                return
            curr = curr.enclosing
        
        raise RuntimeError(f"Undefined variable '{name}'")

    # Optimized lookup helpers
    def try_get(self, name):
        curr = self
        while curr:
            if name in curr.values:
                return curr.values[name]
            curr = curr.enclosing
        return Environment._MISSING

    def has(self, name) -> bool:
        return self.try_get(name) is not Environment._MISSING

class GlobalNamespace:
    __slots__ = ('_interpreter',)
    def __init__(self, interpreter):
        object.__setattr__(self, '_interpreter', interpreter)
    
    def __getattr__(self, name):
        val = self._interpreter.global_env.try_get(name)
        if val is Environment._MISSING:
            raise AttributeError(f"Global variable '{name}' not found")
        return val
    
    def __setattr__(self, name, value):
        self._interpreter.global_env.define(name, value)
    
    def __repr__(self):
        return "<Namespace global>"

class RuntimeTick:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.tick = 1
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True, name="AMLTickThread")
        self.thread.start()
    
    def _run(self):
        import time
        while self.running:
            # Update tick in the spec namespace
            spec = self.interpreter.global_env.try_get('spec')
            if spec is not Environment._MISSING and isinstance(spec, Namespace):
                setattr(spec, 'tick', self.tick)
            
            self.tick = (self.tick % 20) + 1
            time.sleep(1/20.0)
    
    def stop(self):
        self.running = False

class Function:
    __slots__ = ('declaration', 'environment', 'bound_self', 'src_path', 'src_text', '_default_literals')

    def __init__(self, declaration, environment, bound_self=None):
        self.declaration = declaration
        self.environment = environment
        self.bound_self = bound_self
        self.src_path = None
        self.src_text = None
        specs = list(self.declaration.params or [])
        self._default_literals = {}
        for s in specs:
            if isinstance(s, tuple):
                name, expr = s
                if isinstance(expr, Number) or isinstance(expr, String) or isinstance(expr, Boolean):
                    self._default_literals[name] = expr.value
    
    def bind_to_self(self, obj):
        f = Function.__new__(Function)
        f.declaration = self.declaration
        f.environment = self.environment
        f.bound_self = obj
        f.src_path = self.src_path
        f.src_text = self.src_text
        f._default_literals = self._default_literals
        return f
    
    def call(self, interpreter, arguments, kwargs=None):
        # Initialize environment with the pre-calculated size from static analysis
        locals_count = getattr(self.declaration, 'locals_count', 0)
        environment = Environment(self.environment, size=locals_count)
        
        if self.bound_self is not None:
            # 'self' might not have a static index in some cases, but if it does, use it.
            # Usually 'self' is not explicitly in the params, so it might need special handling.
            environment.define('self', self.bound_self)
            
        param_specs = list(self.declaration.params or [])
        param_names = [p if isinstance(p, str) else p[0] for p in param_specs]
        
        # Pre-fill parameters with positional arguments
        for i, arg in enumerate(arguments):
            if i < len(param_names):
                # Parameters are always at the beginning of the local slots
                environment.define(param_names[i], arg, index=i)
            # Extra arguments are allowed and will be available via 'args' list
        
        # Fill remaining parameters with sentinel
        for i in range(len(arguments), len(param_names)):
            environment.define(param_names[i], MISSING_ARG, index=i)

        # Apply keyword arguments
        if kwargs:
            for key, val in kwargs.items():
                if key not in param_names:
                    raise RuntimeError(f"Unknown argument '{key}' for function '{self.declaration.name}'")
                
                idx = param_names.index(key)
                current_val = environment.get_at(0, idx)
                if current_val is not MISSING_ARG:
                    raise RuntimeError(f"Multiple values for argument '{key}'")
                
                environment.define(key, val, index=idx)

        # Define 'args' list locally for each function
        environment.define('args', list(arguments))

        # Handle remaining parameters (apply defaults or error if missing)
        for i, s in enumerate(param_specs):
            val = environment.get_at(0, i)
            if val is MISSING_ARG:
                if isinstance(s, tuple):
                    name, expr = s
                    if name in self._default_literals:
                        environment.define(name, self._default_literals[name], index=i)
                    else:
                        environment.define(name, interpreter.evaluate(expr), index=i)
                else:
                    raise RuntimeError(f"Missing required argument '{param_names[i]}' for function '{self.declaration.name}'")
        
        result = None
        did_push = False
        try:
            if self.src_path and self.src_text:
                interpreter.push_file_context(self.src_path, self.src_text)
                did_push = True
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnValue as return_value:
            result = return_value.value
        except Exception as e:
            line, col = interpreter._extract_line_col(e)
            interpreter._print_error_with_context(str(e), line or 0, col or 0)
            raise
        
        finally:
            if did_push:
                interpreter.pop_file_context()
        return result

class TaskHandle:
    __slots__ = ('_target_name', '_thread', '_result_container')

    def __init__(self, target_name, thread, result_container):
        self._target_name = target_name
        self._thread = thread
        self._result_container = result_container  # dict with keys: result, error
    
    @property
    def done(self):
        return not self._thread.is_alive()
    
    @property
    def error(self):
        return self._result_container.get('error')
    
    @property
    def result(self):
        return self._result_container.get('result')
    
    def join(self, timeout=None):
        self._thread.join(timeout)
        return self.result

class Namespace:
    def __init__(self, name):
        self.__name = name
        self.__constants = set()
        self.__dict__ = {}  # explicitly initialize dict to store attributes
    
    def _add_constant(self, name):
        self.__constants.add(name)

    def __setattr__(self, name, value):
        if name.startswith('_Namespace__'):
            super().__setattr__(name, value)
            return
        if name in getattr(self, '_Namespace__constants', set()):
            raise RuntimeError(f"Cannot reassign constant attribute '{name}' of namespace '{self.__name}'")
        self.__dict__[name] = value

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        raise AttributeError(f"Namespace '{self.__name}' has no attribute '{name}'")

    def __repr__(self):
        return f"<Namespace {self.__name}>"

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__()

class AMLError(Exception):
    def __init__(self, message, line=0, column=0, file=None):
        self.message = message
        self.line = line
        self.column = column
        self.file = file
        super().__init__(self.message)

class BreakException(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column

class ContinueException(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column

class Interpreter:
    def __init__(self):
        # Thread-local environment to avoid race conditions during spawn
        self._env_local = threading.local()
        self.global_env = Environment()

        # Define built-in functions
        self.global_env.define('len', len)
        self.global_env.define('str', str)
        self.global_env.define('int', int)
        self.global_env.define('float', float)
        self.global_env.define('bool', bool)
        self.global_env.define('type', type)
        self.global_env.define('print', print)
        self.global_env.define('exit', sys.exit)
        self.global_env.define('exit_now', lambda code=0: os._exit(code))
        self.global_env.define('tick', self._builtin_tick)
        self.global_env.define('import', self._builtin_import)
        
        # Reactive built-ins
        self.global_env.define('signal', lambda val: Signal(val, self))
        self.global_env.define('effect', lambda func: Effect(func, self))

        # Magic 'global' namespace
        self.global_env.define('global', GlobalNamespace(self))

        # 'spec' namespace for runtime variables
        self.spec_ns = Namespace('spec')
        self.global_env.define('spec', self.spec_ns)

        # 'runtime' namespace for system information
        self.runtime_ns = Namespace('runtime')
        self.runtime_ns.language_version = "1.1.0"
        self.runtime_ns._add_constant('language_version')
        self.runtime_ns.entry_file = ""
        self.runtime_ns._add_constant('entry_file')
        self.runtime_ns.module_paths = []
        self.runtime_ns._add_constant('module_paths')
        self.global_env.define('runtime', self.runtime_ns, is_const=True)
        
        # Start runtime tick thread
        self.runtime_tick = RuntimeTick(self)

        self.DEBUG = False
        # Initialize current thread environment as global
        self.environment = self.global_env
        self.python_modules = {}
        self.aml_modules = {}
        # Runtime control and configurable import search paths
        self.cancelled = False
        self.aml_search_paths = [os.getcwd(), os.path.join(os.getcwd(), "temaune")]
        self.python_search_paths = []
        # Micro-yield configuration to reduce CPU pressure in tight loops
        # Sleep a tiny slice after N executed statements/evaluations
        self._yield_every_statements = 64
        self._yield_sleep_seconds = 0.0  # set to e.g. 0.0005 for stronger throttling
        self._exec_counter = 0
        self._eval_counter = 0
        # Metadata & entrypoint orchestration
        self.metadata = {}
        self._entrypoint_name = None
        self._entry_invoked = False
        self._symbol_cache = {}
        self._aml_module_cache = {}
        self._caml_bundle = None
        self._file_ctx_stack = []
        self._symbol_cache = {}
        self._aml_module_cache = {}
        # Debugger hook
        self.debug_hook = None
        
        # Expose 'meta' in the environment by default
        try:
            self.global_env.define('meta', self.metadata)
        except Exception:
            pass
        
        # --- Optimization: Dispatch Tables ---
        self._build_dispatch_tables()

    def _build_dispatch_tables(self):
        self.execute_dispatch = {
            ImportPy: self.execute_ImportPy,
            ImportAml: self.execute_ImportAml,
            VarDeclaration: self.execute_VarDeclaration,
            ConstDeclaration: self.execute_ConstDeclaration,
            FunctionDeclaration: self.execute_FunctionDeclaration,
            NamespaceDeclaration: self.execute_NamespaceDeclaration,
            MetadataDeclaration: self.execute_MetadataDeclaration,
            ParallelBlock: self.execute_ParallelBlock,
            IfStatement: self.execute_IfStatement,
            WhileStatement: self.execute_WhileStatement,
            ForStatement: self.execute_ForStatement,
            TryCatchStatement: self.execute_TryCatchStatement,
            ReturnStatement: self.execute_ReturnStatement,
            RaiseStatement: self.execute_RaiseStatement,
            FunctionCall: self.execute_FunctionCall,
            MethodCall: self.execute_MethodCall,
            SpawnCall: self.execute_SpawnCall,
            PythonClassInstance: self.execute_PythonClassInstance,
            BinaryOperation: self.execute_BinaryOperation,
            UnaryOperation: self.execute_UnaryOperation,
            Assignment: self.execute_Assignment,
            BreakStatement: self.execute_BreakStatement,
            ContinueStatement: self.execute_ContinueStatement,
        }
        
        self.evaluate_dispatch = {
            Number: self.evaluate_Number,
            String: self.evaluate_String,
            Boolean: self.evaluate_Boolean,
            Null: self.evaluate_Null,
            Identifier: self.evaluate_Identifier,
            ListLiteral: self.evaluate_ListLiteral,
            DictLiteral: self.evaluate_DictLiteral,
            IndexAccess: self.evaluate_IndexAccess,
            BinaryOperation: self.evaluate_BinaryOperation,
            UnaryOperation: self.evaluate_UnaryOperation,
            FunctionCall: self.evaluate_FunctionCall,
            PythonClassInstance: self.evaluate_PythonClassInstance,
            MethodCall: self.evaluate_MethodCall,
            AttributeAccess: self.evaluate_AttributeAccess,
            SpawnCall: self.evaluate_SpawnCall, # SpawnCall is an expression too
            RangeExpression: self.evaluate_RangeExpression,
            Pointer: self.evaluate_Pointer,
            ListComprehension: self.evaluate_ListComprehension,
            DictComprehension: self.evaluate_DictComprehension,
        }

    def configure_micro_yield(self, every: int | None = None, sleep_seconds: float | None = None):
        """Configure micro-yield behavior.
        - every: apply yield after this many statements/evaluations (power of two recommended)
        - sleep_seconds: duration for each yield (0.0 for scheduler yield only)
        """
        if every is not None and every > 0:
            self._yield_every_statements = int(every)
        if sleep_seconds is not None and sleep_seconds >= 0.0:
            self._yield_sleep_seconds = float(sleep_seconds)

    def disable_micro_yield(self):
        """Disable micro-yielding by setting a very large threshold."""
        self._yield_every_statements = 1 << 30
        self._yield_sleep_seconds = 0.0

    @property
    def environment(self):
        # Each thread keeps its own current environment
        env = getattr(self._env_local, 'environment', None)
        if env is None:
            # Default to global if not initialized in this thread
            self._env_local.environment = self.global_env
            return self.global_env
        return env

    @environment.setter
    def environment(self, env):
        self._env_local.environment = env
    
    def interpret(self, program, source_text=None, file_path=None):
        """
        Interpret a program AST
        """
        if file_path:
            object.__setattr__(self.runtime_ns, 'entry_file', os.path.abspath(file_path))
            # Ensure module_paths is initialized with default search paths
            object.__setattr__(self.runtime_ns, 'module_paths', list(self.aml_search_paths))

        for statement in program.statements:
            # Cooperative cancellation support
            if self.cancelled:
                return
            try:
                self.execute(statement)
            except KeyboardInterrupt:
                # Перехоплюємо Ctrl+C для дружнього завершення
                self.cancel()
                print("\nВиконання AML перервано користувачем (KeyboardInterrupt)")
                return
            except BreakException as e:
                print(f"Runtime Error at line {e.line}, column {e.column}: break outside loop")
                return
            except ContinueException as e:
                print(f"Runtime Error at line {e.line}, column {e.column}: continue outside loop")
                return
            except Exception as e:
                line, col = self._extract_line_col(e)
                if line is None:
                    line, col = statement.line, statement.column
                self._print_error_with_context(str(e), line, col)
                return
        # Auto-invoke entrypoint if provided via meta and not explicitly called
        try:
            if not self.cancelled and self._entrypoint_name and not self._entry_invoked:
                self._invoke_entrypoint()
        except Exception as e:
            print(f"Runtime Error during entrypoint call: {e}")
    
    def set_debug_hook(self, hook):
        """
        Set a debugger hook that will be called before executing each statement/expression.
        Hook signature: hook(interpreter, node, scope_name)
        """
        self.debug_hook = hook

    def execute(self, statement):
        """
        Execute a statement with handler caching for speed
        """
        if self.debug_hook:
            self.debug_hook(self, statement, "statement")

        # Direct dispatch optimization: cache handler on the node
        handler = getattr(statement, '_aml_handler', None)
        if handler is None:
            handler = self.execute_dispatch.get(type(statement))
            if handler:
                statement._aml_handler = handler
            else:
                return self.execute_unknown(statement)
        
        result = handler(statement)

        # Micro-yield after a number of executed statements
        self._exec_counter += 1
        if (self._exec_counter & (self._yield_every_statements - 1)) == 0:
            import time
            if self._yield_sleep_seconds > 0.0:
                time.sleep(self._yield_sleep_seconds)
            else:
                time.sleep(0)
        return result
    
    def execute_unknown(self, statement):
        raise RuntimeError(f"Unknown statement type: {statement.__class__.__name__} at line {statement.line}, column {statement.column}")

    def is_truthy(self, value):
        """
        Determine if a value is truthy in AML
        """
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, (list, dict, tuple)):
            return len(value) > 0
        return True
    
    def _to_num(self, v):
        if isinstance(v, (int, float)):
            return v
        if isinstance(v, str):
            try:
                return float(v) if '.' in v else int(v)
            except ValueError:
                pass
        return None

    def execute_block(self, statements, environment):
        """
        Execute a block of statements in a new environment
        """
        previous_env = self.environment
        try:
            self.environment = environment
            
            for statement in statements:
                if self.cancelled:
                    break
                self.execute(statement)
        finally:
            self.environment = previous_env
    
    def execute_ImportPy(self, statement):
        """
        Import Python modules
        """
        # Ensure configured python_search_paths are in sys.path
        for p in self.python_search_paths:
            if p not in sys.path:
                sys.path.insert(0, p)

        for spec in statement.modules:
            # Normalize spec to (module_name, alias)
            if isinstance(spec, (tuple, list)) and len(spec) >= 1:
                module_name = spec[0]
                alias = spec[1] if len(spec) > 1 else None
            else:
                module_name = spec
                alias = None
            try:
                # Handle module paths with backslashes or forward slashes
                full_module_name = module_name.replace('\\', '.').replace('/', '.')
                module = importlib.import_module(full_module_name)
                
                # Define the module in the environment with base name
                base_name = full_module_name.split('.')[-1]
                # Inject cooperative cancellation checker into base module if available
                if base_name == 'base':
                    try:
                        def _aml_check_cancel():
                            return self.cancelled
                        setattr(module, '_aml_check_cancel', _aml_check_cancel)
                    except Exception:
                        pass
                # Inject runtime proxy into all imported Python modules
                try:
                    import aml_runtime_access as _aml_rt_acc
                    # Attach current interpreter globally for simplified API
                    try:
                        _aml_rt_acc.attach_interpreter(self)
                    except Exception:
                        pass
                    # Provide per-module runtime proxy
                    try:
                        runtime_proxy = _aml_rt_acc.RuntimeProxy(self)
                        setattr(module, '_aml_runtime', runtime_proxy)
                    except Exception:
                        pass
                except Exception:
                    # Якщо модуль доступу до рантайму не знайдено, пропускаємо інжекцію
                    pass
                name_to_define = alias or base_name
                self.environment.define(name_to_define, module)
                self.python_modules[module_name] = module
            except ImportError as e:
                print(f"Error importing Python module '{module_name}': {e}")
    
    def dict_to_ast(self, data):
        if data is None: return None
        if isinstance(data, (int, float, str, bool)): return data
        if isinstance(data, list): return [self.dict_to_ast(item) for item in data]
        
        if not isinstance(data, dict):
            return data
            
        if "_e" in data:
            from .tokens import TokenType
            if data["_e"] == "TokenType":
                return TokenType[data["v"]]
            return data["v"]

        if "_t" not in data:
            return data
            
        data_copy = data.copy()
        cls_name = data_copy.pop("_t")
        
        # Resolve class from aml.parser
        import aml.parser as parser
        cls = getattr(parser, cls_name, None)
        if not cls:
            raise RuntimeError(f"Unknown AST node type in CAML: {cls_name}")
            
        node = cls.__new__(cls)
        for k, v in data_copy.items():
            setattr(node, k, self.dict_to_ast(v))
        
        if not hasattr(node, 'line'): node.line = 0
        if not hasattr(node, 'column'): node.column = 0
        if not hasattr(node, 'token'): node.token = None
        return node

    def load_caml(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            encoded = f.read()
        json_str = base64.b64decode(encoded).decode('utf-8')
        data = json.loads(json_str)
        self._caml_bundle = data['modules']
        return data['entry']

    def _load_ast(self, file_path):
        """
        Loads AST from disk cache if valid, otherwise parses source and caches it.
        """
        # Check CAML bundle first
        if self._caml_bundle and file_path in self._caml_bundle:
            return self.dict_to_ast(self._caml_bundle[file_path])

        from .lexer import Lexer
        from .parser import Parser

        cache_dir = os.path.join(os.getcwd(), ".aml_cache")
        if not os.path.exists(cache_dir):
            try: os.makedirs(cache_dir)
            except Exception: pass

        try:
            mtime = os.path.getmtime(file_path)
            size = os.path.getsize(file_path)
            # Cache key based on file path, mtime and size
            cache_key = hashlib.md5(f"ast_v2:{file_path}:{mtime}:{size}".encode()).hexdigest()
            cache_file = os.path.join(cache_dir, f"{cache_key}.ast")

            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
                except Exception:
                    pass

            # If no cache or error, parse fresh
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Save to cache
            try:
                # Add metadata to the AST object before pickling for the viewer
                ast._cache_metadata = {
                    'file_path': os.path.abspath(file_path),
                    'mtime': mtime,
                    'size': size,
                    'cache_key': cache_key,
                    'cached_at': __import__('time').time()
                }
                with open(cache_file, 'wb') as f:
                    pickle.dump(ast, f)
            except Exception:
                pass
            
            return ast
        except Exception as e:
            # Fallback for errors
            import traceback
            traceback.print_exc()
            print(f"AST Parsing error in {file_path}: {e}")
            if self.DEBUG:
                print(f"[DBG] AST Cache error for {file_path}: {e}")
            return None

    def execute_ImportAml(self, statement):
        """
        Import AML modules
        """
        for module_name in statement.modules:
            try:
                self._load_aml_module(module_name, target_env=self.environment)
            except Exception as e:
                print(f"Import Error in '{module_name}': {e}")

    def _builtin_tick(self, func, rate=20):
        if not (callable(func) or isinstance(func, Function)):
            raise RuntimeError("tick() requires a function as first argument")
        
        def wrapper():
            import time
            while not self.cancelled:
                try:
                    if isinstance(func, Function):
                        func.call(self, [])
                    else:
                        func()
                except Exception as e:
                    print(f"Error in tick function: {e}")
                time.sleep(1.0 / rate)
        
        name = "unknown"
        if isinstance(func, Function):
            name = func.declaration.name
        elif hasattr(func, '__name__'):
            name = func.__name__
            
        t = threading.Thread(target=wrapper, daemon=True, name=f"AMLTickFunc:{name}")
        t.start()

    def _builtin_import(self, module_name):
        return self._load_aml_module(module_name)

    def _load_aml_module(self, module_name, target_env=None):
        """
        Helper to load an AML module into an environment or return as a Namespace.
        """
        # Resolve file path
        normalized_name = module_name.replace('\\', os.path.sep).replace('/', os.path.sep).replace('.', os.path.sep)
        file_path = None
        
        # 1. Check if it's in the CAML bundle
        if self._caml_bundle:
            # Bundle uses absolute paths as keys
            # We need to find which key matches this module name
            for bundle_path in self._caml_bundle:
                if bundle_path.endswith(f"{normalized_name}.aml"):
                    file_path = bundle_path
                    break
        
        # 2. Check filesystem if not found in bundle
        if not file_path:
            for base in self.aml_search_paths:
                candidate = os.path.join(base, f"{normalized_name}.aml")
                if os.path.exists(candidate):
                    file_path = candidate
                    break
                    
        if not file_path:
            raise FileNotFoundError(f"AML module '{normalized_name}.aml' not found")

        file_path = os.path.abspath(file_path)
        
        # For bundle, we don't check mtime as files might not exist
        if self._caml_bundle and file_path in self._caml_bundle:
            mtime = 0 
        else:
            mtime = os.path.getmtime(file_path)
        
        # Check cache
        cache_key = f"mod:{file_path}"
        cached = self._aml_module_cache.get(cache_key)
        if cached and cached['mtime'] == mtime:
            module_env = cached['env']
            return_val = cached.get('return_val')
        else:
            module_ast = self._load_ast(file_path)
            if module_ast is None:
                raise RuntimeError(f"Failed to load AST for {file_path}")
            
            # If file exists on disk, push context with source
            source = ""
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    source = file.read()
            
            module_env = Environment(self.global_env)
            previous_env = self.environment
            return_val = None
            try:
                self.environment = module_env
                if source:
                    self.push_file_context(file_path, source)
                else:
                    # Minimal context for bundled modules without disk source
                    self.push_file_context(file_path, "# bundled module")
                for stmt in module_ast.statements:
                    self.execute(stmt)
            except ReturnValue as rv:
                return_val = rv.value
            finally:
                self.pop_file_context()
                self.environment = previous_env
            
            # Cache ONLY AFTER execution to ensure all definitions are present
            if len(self._aml_module_cache) > 256:
                self._aml_module_cache.clear()
            self._aml_module_cache[cache_key] = {'env': module_env, 'mtime': mtime, 'return_val': return_val}

        if target_env is None:
            # If the module explicitly returned a value, use it.
            # Otherwise return a Namespace containing all defined values.
            if return_val is not None:
                return return_val
            
            # Isolated import: return a Namespace
            ns = Namespace(module_name)
            for name, val in module_env.values.items():
                # print(f"[DEBUG] Defining {name} in namespace {module_name}")
                setattr(ns, name, val)
            # print(f"[DEBUG] Namespace {module_name} contents: {ns.__dict__.keys()}")
            return ns
        else:
            # Traditional import: merge into target_env
            for name, val in module_env.values.items():
                target_env.define(name, val)
            return target_env

    # ---- Runtime control & search path configuration ----
    def cancel(self):
        """Request cooperative cancellation of the current execution."""
        self.cancelled = True

    def reset_cancel(self):
        """Reset cancellation flag to allow subsequent runs."""
        self.cancelled = False

    def add_aml_search_path(self, path):
        if path and path not in self.aml_search_paths:
            self.aml_search_paths.append(path)
            object.__setattr__(self.runtime_ns, 'module_paths', list(self.aml_search_paths))

    def add_python_search_path(self, path):
        if not path:
            return
        if path not in sys.path:
            sys.path.insert(0, path)
        if path not in self.python_search_paths:
            self.python_search_paths.append(path)
    
    def execute_VarDeclaration(self, statement):
        """
        Execute a variable declaration
        """
        value = self.evaluate(statement.value)
        
        # Use resolved index if available for faster definition
        index = getattr(statement, 'resolved_index', -1)
        self.environment.define(statement.name, value, index=index)
        
        if self.DEBUG:
            try:
                # Debug output to trace variable definitions during execution
                print(f"[DBG] define {statement.name} -> {type(value).__name__}")
            except Exception:
                pass
    
    def execute_ConstDeclaration(self, statement):
        """
        Execute a constant declaration
        """
        value = self.evaluate(statement.value)
        
        # Use resolved index if available for faster definition
        index = getattr(statement, 'resolved_index', -1)
        self.environment.define(statement.name, value, index=index, is_const=True)
        
        if self.DEBUG:
            try:
                print(f"[DBG] define const {statement.name} -> {type(value).__name__}")
            except Exception:
                pass

    def execute_FunctionDeclaration(self, statement):
        """
        Execute a function declaration
        """
        if getattr(statement, 'ns_path', None):
            target_name = '.'.join(statement.ns_path)
            obj = self._resolve_dotted_symbol(target_name)
            function = Function(statement, self.environment).bind_to_self(obj)
            ctx = self._current_file_ctx()
            if ctx:
                function.src_path = ctx['path']
                function.src_text = ctx.get('text') if isinstance(ctx, dict) else None
            if isinstance(obj, dict):
                obj[statement.name] = function
            else:
                setattr(obj, statement.name, function)
        else:
            function = Function(statement, self.environment)
            ctx = self._current_file_ctx()
            if ctx:
                function.src_path = ctx['path']
                function.src_text = ctx.get('text') if isinstance(ctx, dict) else None
            self.environment.define(statement.name, function)

    def execute_NamespaceDeclaration(self, statement):
        """
        Execute a namespace declaration: creates a sub-environment and exposes members via object attributes
        """
        ns_obj = Namespace(statement.name)
        # Create a new environment for the namespace body, enclosed in current environment
        ns_env = Environment(self.environment)
        prev_env = self.environment
        try:
            self.environment = ns_env
            for stmt in statement.body:
                self.execute(stmt)
        finally:
            self.environment = prev_env
        # Transfer all names from ns_env to namespace object
        for name, value in ns_env.values.items():
            if isinstance(value, Function):
                value = value.bind_to_self(ns_obj)
            # Use object.__setattr__ to bypass the constant check during initial population
            object.__setattr__(ns_obj, name, value)
            if name in ns_env.constants:
                ns_obj._add_constant(name)
        # Define namespace object in current environment
        self.environment.define(statement.name, ns_obj)

    def execute_MetadataDeclaration(self, statement):
        """Capture metadata and expose it via 'meta' in the environment.
        Recognized fields: version, entry, author, created (+ any custom).
        """
        # Merge parsed elements into the single runtime metadata dict
        for key, val_node in statement.elements:
            try:
                val = self.evaluate(val_node)
            except Exception:
                # Fallback: use raw string literal value when evaluation fails
                val = val_node.value if hasattr(val_node, 'value') else None
            self.metadata[str(key)] = val
        # Ensure 'meta' name points to the interpreter metadata dict
        try:
            self.environment.define('meta', self.metadata)
        except Exception:
            pass
        # handle entrypoint string like "app.main"
        entry = self.metadata.get('entry') or self.metadata.get('entrypoint')
        if isinstance(entry, str) and entry:
            self._entrypoint_name = entry

    def _resolve_dotted_symbol(self, dotted: str):
        key = dotted
        ver = (self.environment._version, self.global_env._version)
        cached = self._symbol_cache.get(key)
        if cached and cached[0] == ver:
            return cached[1]
        parts = dotted.split('.')
        base = self.environment.try_get(parts[0])
        if base is Environment._MISSING:
            base = self.global_env.try_get(parts[0])
            if base is Environment._MISSING:
                raise RuntimeError(f"Undefined symbol '{parts[0]}'")
        obj = base
        for p in parts[1:]:
            if isinstance(obj, dict) and p in obj:
                obj = obj[p]
            elif hasattr(obj, p):
                obj = getattr(obj, p)
            else:
                raise RuntimeError(f"Symbol '{dotted}': missing attribute '{p}'")
        if len(self._symbol_cache) > 2048:
            self._symbol_cache.clear()
        self._symbol_cache[key] = (ver, obj)
        return obj

    def _invoke_entrypoint(self):
        name = self._entrypoint_name
        target = None
        try:
            target = self._resolve_dotted_symbol(name)
        except Exception:
            # If no dots, try simple name
            try:
                target = self.environment.get(name)
            except Exception:
                target = self.global_env.get(name)
        # Call with no args
        if isinstance(target, Function):
            target.call(self, [])
        elif callable(target):
            target()
        else:
            raise RuntimeError(f"Entrypoint '{name}' is not callable")
        self._entry_invoked = True

    def execute_ParallelBlock(self, statement):
        """Launch contained function/method calls in parallel threads (daemon)."""
        threads = []
        def _run_callable(callee, args, kwargs):
            try:
                if isinstance(callee, Function):
                    callee.call(self, args, kwargs=kwargs if kwargs else None)
                elif callable(callee):
                    callee(*args, **kwargs)
            except Exception:
                pass

        for stmt in statement.body:
            if isinstance(stmt, FunctionCall):
                try:
                    callee = self.environment.get(stmt.name)
                except RuntimeError:
                    callee = self.global_env.get(stmt.name)
                args = [self.evaluate(arg) for arg in stmt.args]
                kwargs = {k: self.evaluate(v) for (k, v) in getattr(stmt, 'kwargs', [])}
                t = threading.Thread(target=_run_callable, args=(callee, args, kwargs), name=f"AMLParallel:{stmt.name}", daemon=True)
                t.start()
                threads.append(t)
            elif isinstance(stmt, MethodCall):
                # Resolve object by name or expression
                if stmt.object_name is not None:
                    try:
                        obj = self.environment.get(stmt.object_name)
                    except RuntimeError:
                        obj = self.global_env.get(stmt.object_name)
                elif getattr(stmt, 'object_expr', None) is not None:
                    obj = self.evaluate(stmt.object_expr)
                else:
                    raise RuntimeError("parallel method call has no target object")
                if not hasattr(obj, stmt.method_name):
                    raise RuntimeError(f"'{stmt.object_name}' has no method '{stmt.method_name}'")
                callee = getattr(obj, stmt.method_name)
                args = [self.evaluate(arg) for arg in stmt.args]
                kwargs = {k: self.evaluate(v) for (k, v) in getattr(stmt, 'kwargs', [])}
                t = threading.Thread(target=_run_callable, args=(callee, args, kwargs), name=f"AMLParallel:{stmt.method_name}", daemon=True)
                t.start()
                threads.append(t)
            else:
                # Non-call statements inside parallel are ignored for now
                continue
    
    def execute_IfStatement(self, statement):
        """
        Execute an if statement
        """
        condition = self.evaluate(statement.condition)
        
        if self.is_truthy(condition):
            for stmt in statement.if_body:
                self.execute(stmt)
        elif statement.else_body:
            for stmt in statement.else_body:
                self.execute(stmt)
    
    def execute_WhileStatement(self, statement):
        """
        Execute a while statement with optimized loop
        """
        cond_node = statement.condition
        body = statement.body
        is_truthy = self.is_truthy
        evaluate = self.evaluate
        execute = self.execute
        
        # Micro-yield configuration
        yield_mask = self._yield_every_statements - 1
        
        # Pre-get condition handler
        cond_handler = getattr(cond_node, '_aml_eval_handler', None)
        if not cond_handler:
            evaluate(cond_node) # Trigger caching
            cond_handler = cond_node._aml_eval_handler

        while is_truthy(cond_handler(cond_node)):
            if self.cancelled:
                break
            try:
                for stmt in body:
                    # Inlining small part of execute for speed
                    handler = getattr(stmt, '_aml_handler', None)
                    if handler:
                        handler(stmt)
                    else:
                        execute(stmt)
                        
                # Micro-yield at end of loop iteration
                if (self._exec_counter & yield_mask) == 0:
                    import time
                    if self._yield_sleep_seconds > 0.0:
                        time.sleep(self._yield_sleep_seconds)
                    else:
                        time.sleep(0)
            except ContinueException:
                continue
            except BreakException:
                break

    def execute_ForStatement(self, statement):
        """
        Execute a for statement with optimized loop
        """
        iterable = self.evaluate(statement.iterable)
        if not hasattr(iterable, '__iter__'):
            raise RuntimeError(f"'{iterable}' is not iterable")
        
        body = statement.body
        var_name = statement.var_name
        execute = self.execute
        env = self.environment
        yield_mask = self._yield_every_statements - 1
        
        for item in iterable:
            if self.cancelled:
                break
            
            # Update the iterator variable in current environment
            env.define(var_name, item)
            
            try:
                # Execute the loop body directly in current environment
                for stmt in body:
                    handler = getattr(stmt, '_aml_handler', None)
                    if handler:
                        handler(stmt)
                    else:
                        execute(stmt)
                
                # Micro-yield at end of loop iteration
                if (self._exec_counter & yield_mask) == 0:
                    import time
                    if self._yield_sleep_seconds > 0.0:
                        time.sleep(self._yield_sleep_seconds)
                    else:
                        time.sleep(0)
            except ContinueException:
                continue
            except BreakException:
                break

    def execute_TryCatchStatement(self, statement):
        """
        Execute a try-catch statement. On error, log and run catch body.
        """
        try:
            for stmt in statement.try_body:
                if self.cancelled:
                    break
                self.execute(stmt)
        except (ContinueException, BreakException, ReturnValue):
            # Preserve loop control and return semantics
            raise
        except Exception as e:
            # Informative error message
            error_msg = str(e)
            
            # Execute catch body if it exists
            if statement.catch_body:
                catch_env = Environment(self.environment)
                # If error_var was specified in catch(var), use it.
                # Otherwise default to 'error'
                var_name = getattr(statement, 'error_var', None) or 'error'
                catch_env.define(var_name, error_msg)
                
                self.execute_block(statement.catch_body, catch_env)
            else:
                # If no catch body, at least print it if DEBUG is on
                if self.DEBUG:
                    print(f"Caught error (unhandled): {error_msg}")
    
    def execute_ReturnStatement(self, statement):
        """
        Execute a return statement
        """
        value = None
        if statement.value:
            value = self.evaluate(statement.value)
        
        raise ReturnValue(value)
    
    def execute_RaiseStatement(self, statement):
        """
        Execute a raise statement
        """
        message = self.evaluate(statement.expression)
        file_path = self._file_ctx_stack[-1] if self._file_ctx_stack else None
        raise AMLError(message, line=statement.line, column=statement.column, file=file_path)
    
    def execute_FunctionCall(self, statement):
        """
        Execute a function call
        """
        return self.evaluate(statement)
    
    def execute_MethodCall(self, statement):
        """
        Execute a method call
        """
        return self.evaluate(statement)

    def execute_SpawnCall(self, statement):
        """
        Execute a spawn call expression
        """
        return self.evaluate_SpawnCall(statement)
    
    def evaluate_SpawnCall(self, expr):
        """
        Evaluate a spawn call: launches a function/method in a new thread
        """
        call_node = expr.call_node
        args = []
        kwargs = {}
        callee = None
        name = "spawned"

        if isinstance(call_node, FunctionCall):
            callee = self.environment.get(call_node.name)
            args = [self.evaluate(arg) for arg in call_node.args]
            kwargs = {k: self.evaluate(v) for (k, v) in getattr(call_node, 'kwargs', [])}
            name = call_node.name
            
        elif isinstance(call_node, MethodCall):
            # Resolve object
            if call_node.object_name is not None:
                obj = self.environment.get(call_node.object_name)
            elif getattr(call_node, 'object_expr', None) is not None:
                obj = self.evaluate(call_node.object_expr)
            else:
                raise RuntimeError("Spawn method call has no target object")
            
            if not hasattr(obj, call_node.method_name):
                 raise RuntimeError(f"Object has no method '{call_node.method_name}'")
                 
            callee = getattr(obj, call_node.method_name)
            args = [self.evaluate(arg) for arg in call_node.args]
            kwargs = {k: self.evaluate(v) for (k, v) in getattr(call_node, 'kwargs', [])}
            name = f"{call_node.object_name or '?'}.{call_node.method_name}"
            
        else:
            raise RuntimeError("spawn must be followed by a function or method call")

        result_container = {'result': None, 'error': None}
        
        def _runner():
            try:
                if isinstance(callee, Function):
                    res = callee.call(self, args, kwargs=kwargs)
                    result_container['result'] = res
                elif callable(callee):
                    res = callee(*args, **kwargs)
                    result_container['result'] = res
            except Exception as e:
                result_container['error'] = e

        t = threading.Thread(target=_runner, name=f"Spawn:{name}", daemon=True)
        t.start()
        
        return TaskHandle(name, t, result_container)

    def execute_PythonClassInstance(self, statement):
        """
        Execute a Python class instantiation
        """
        return self.evaluate(statement)
    
    def execute_BinaryOperation(self, statement):
        """
        Execute a binary operation
        """
        return self.evaluate(statement)
    
    def execute_UnaryOperation(self, statement):
        """
        Execute a unary operation
        """
        return self.evaluate(statement)
    
    def execute_Assignment(self, statement):
        """
        Execute an assignment statement
        """
        value = self.evaluate(statement.value)
        # print(f"[DEBUG] Assignment {statement.name} = {value}")
        # Підтримка крапкових присвоєнь: a.b.c = value або index доступів
        target_expr = getattr(statement, 'target_expr', None)
        if target_expr is not None:
            # AttributeAccess: obj.attr = value
            if isinstance(target_expr, AttributeAccess):
                obj = self.evaluate(target_expr.target)
                setattr(obj, target_expr.attr_name, value)
                return
            # IndexAccess: obj[idx] = value
            if isinstance(target_expr, IndexAccess):
                obj = self.evaluate(target_expr.target)
                idx = self.evaluate(target_expr.index)
                try:
                    obj[idx] = value
                except Exception as e:
                    raise RuntimeError(f"Cannot assign by index: {e}")
                return
            # Невідомий тип цілі присвоєння
            raise RuntimeError("Invalid assignment target")
        
        # Optimized assignment using resolved index
        idx = getattr(statement, '_aml_idx', -2)
        if idx == -2:
            idx = getattr(statement, 'resolved_index', -1)
            depth = getattr(statement, 'resolved_depth', -1)
            statement._aml_idx = idx
            statement._aml_depth = depth
            
        if idx != -1:
            # Inline environment.assign_at for speed
            curr = self.environment
            for _ in range(statement._aml_depth):
                curr = curr.enclosing
                if not curr: break
            if curr:
                if idx >= len(curr.slots):
                    curr.slots.extend([None] * (idx - len(curr.slots) + 1))
                
                # Reactive integration: if existing value is a Signal, update it instead of reassigning the name
                existing = curr.slots[idx]
                if isinstance(existing, Signal):
                    existing.set(value)
                    return

                curr.slots[idx] = value
                curr.values[statement.name] = value
                curr._version += 1
                return
        
        # Reactive integration for non-optimized assignment
        try:
            existing = self.environment.get(statement.name)
            if isinstance(existing, Signal):
                existing.set(value)
                return
        except RuntimeError:
            pass

        # Стандартне присвоєння у середовищі
        self.environment.assign(statement.name, value)

    def execute_BreakStatement(self, statement):
        raise BreakException(statement.line, statement.column)

    def execute_ContinueStatement(self, statement):
        raise ContinueException(statement.line, statement.column)
    
    def evaluate(self, expr):
        """
        Evaluate an expression with handler caching for speed
        """
        if self.debug_hook:
            self.debug_hook(self, expr, "expression")

        # Direct dispatch optimization: cache handler on the node
        handler = getattr(expr, '_aml_eval_handler', None)
        if handler is None:
            handler = self.evaluate_dispatch.get(type(expr))
            if handler:
                expr._aml_eval_handler = handler
            else:
                return self.evaluate_unknown(expr)
        
        try:
            result = handler(expr)
                
            # Micro-yield after a number of evaluations
            self._eval_counter += 1
            if (self._eval_counter & (self._yield_every_statements - 1)) == 0:
                import time
                if self._yield_sleep_seconds > 0.0:
                    time.sleep(self._yield_sleep_seconds)
                else:
                    time.sleep(0)
            return result
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise
            raise RuntimeError(f"Error at line {getattr(expr, 'line', 0)}, column {getattr(expr, 'column', 0)}: {str(e)}")
    
    def evaluate_unknown(self, expr):
        raise RuntimeError(f"Unknown expression type: {expr.__class__.__name__} at line {expr.line}, column {expr.column}")
    
    def evaluate_Pointer(self, expr):
        # evaluate the target as a reference
        # if it's an Identifier, we want the object itself without calling it if it's a function
        # evaluate() usually does exactly what we want: returns the value of the identifier.
        return self.evaluate(expr.target)

    def evaluate_Number(self, expr):
        return expr.value
    
    def evaluate_String(self, expr):
        return expr.value

    def evaluate_Boolean(self, expr):
        return expr.value

    def evaluate_Null(self, expr):
        return None

    def evaluate_RangeExpression(self, node):
        start = self.evaluate(node.start)
        end = self.evaluate(node.end)
        
        # Ensure numbers
        start = self._to_num(start)
        end = self._to_num(end)
        
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            raise RuntimeError("Range operator '..' requires numeric operands")
            
        start = int(start)
        end = int(end)
        
        step = 1 if start <= end else -1
        # Include end in range
        return list(range(start, end + step, step))

    def evaluate_Identifier(self, expr):
        # Optimized lookup using resolved index
        idx = getattr(expr, '_aml_idx', -2)
        if idx == -2:
            idx = getattr(expr, 'resolved_index', -1)
            depth = getattr(expr, 'resolved_depth', -1)
            expr._aml_idx = idx
            expr._aml_depth = depth
            
        val = Environment._MISSING
        if idx != -1:
            # Inline environment.get_at for speed
            curr = self.environment
            for _ in range(expr._aml_depth):
                curr = curr.enclosing
                if not curr: break
            if curr and idx < len(curr.slots):
                val = curr.slots[idx]
        
        if val is Environment._MISSING or val is None:
            # Optimized: avoid exception-based control flow for missing names
            val = self.environment.try_get(expr.name)
            if val is Environment._MISSING:
                val = self.global_env.try_get(expr.name)
                if val is Environment._MISSING:
                    raise RuntimeError(f"Undefined variable '{expr.name}'")
        
        # Reactive integration: if it's a Signal, auto-dereference and register dependency
        if isinstance(val, Signal):
            return val.get()
            
        return val
    
    def evaluate_ListLiteral(self, expr):
        elements = []
        for element in expr.elements:
            val = self.evaluate(element)
            # Auto-flatten ranges within list literals
            if isinstance(element, RangeExpression) and isinstance(val, list):
                elements.extend(val)
            else:
                elements.append(val)
        return elements

    def evaluate_ListComprehension(self, expr):
        iterable = self.evaluate(expr.iterable)
        if not hasattr(iterable, '__iter__'):
            raise RuntimeError(f"Object of type '{type(iterable).__name__}' is not iterable")

        results = []
        original_env = self.environment
        
        # We need a new environment for the comprehension to avoid polluting the current scope
        # but it should be able to access outer variables.
        comprehension_env = Environment(original_env)
        
        try:
            self.environment = comprehension_env
            for item in iterable:
                comprehension_env.define(expr.var_name, item)
                
                should_include = True
                if expr.condition:
                    should_include = self.evaluate(expr.condition)
                
                if should_include:
                    val = self.evaluate(expr.expression)
                    results.append(val)
        finally:
            self.environment = original_env
            
        return results

    def evaluate_DictLiteral(self, expr):
        result = {}
        for key_node, value_node in expr.elements:
            key = self.evaluate(key_node)
            value = self.evaluate(value_node)
            result[key] = value
        return result

    def evaluate_DictComprehension(self, expr):
        iterable = self.evaluate(expr.iterable)
        if not hasattr(iterable, '__iter__'):
            raise RuntimeError(f"Object of type '{type(iterable).__name__}' is not iterable")

        results = {}
        original_env = self.environment
        comprehension_env = Environment(original_env)
        
        try:
            self.environment = comprehension_env
            for item in iterable:
                comprehension_env.define(expr.var_name, item)
                
                should_include = True
                if expr.condition:
                    should_include = self.evaluate(expr.condition)
                
                if should_include:
                    key = self.evaluate(expr.key_expression)
                    val = self.evaluate(expr.value_expression)
                    results[key] = val
        finally:
            self.environment = original_env
            
        return results

    def evaluate_IndexAccess(self, expr):
        target = self.evaluate(expr.target)
        index = self.evaluate(expr.index)

        # List indexing
        if isinstance(target, list):
            if isinstance(index, float):
                if index.is_integer():
                    index = int(index)
                else:
                    raise RuntimeError("List index must be an integer")
            if not isinstance(index, int):
                raise RuntimeError("List index must be an integer")
            if index < 0 or index >= len(target):
                raise RuntimeError("List index out of range")
            return target[index]

        # Dict indexing
        if isinstance(target, dict):
            if index not in target:
                raise RuntimeError(f"Key not found: {index}")
            return target[index]

        # Python sequences or mappings (optional)
        try:
            return target[index]
        except Exception:
            pass

        raise RuntimeError(f"Object of type '{type(target).__name__}' is not indexable")
    
    def evaluate_BinaryOperation(self, expr):
        # Short-circuit logical ops; evaluate RHS only when needed
        op = expr.op
        evaluate = self.evaluate
        
        if op == TokenType.AND:
            left = self.is_truthy(evaluate(expr.left))
            if not left:
                return False
            return self.is_truthy(evaluate(expr.right))
        if op == TokenType.OR:
            left = self.is_truthy(evaluate(expr.left))
            if left:
                return True
            return self.is_truthy(evaluate(expr.right))

        left = evaluate(expr.left)
        right = evaluate(expr.right)
        
        # Optimized path for numbers (most common)
        if type(left) in (int, float) and type(right) in (int, float):
            if op == TokenType.PLUS: return left + right
            if op == TokenType.MINUS: return left - right
            if op == TokenType.MULTIPLY: return left * right
            if op == TokenType.DIVIDE: return left / right if right != 0 else 0
            if op == TokenType.LESS_THAN: return left < right
            if op == TokenType.GREATER_THAN: return left > right
            if op == TokenType.EQUALS: return left == right
            if op == TokenType.NOT_EQUALS: return left != right
            if op == TokenType.LESS_THAN_EQUALS: return left <= right
            if op == TokenType.GREATER_THAN_EQUALS: return left >= right
            if op == TokenType.FLOOR_DIVIDE: return left // right if right != 0 else 0
            if op == TokenType.MODULO: return left % right if right != 0 else 0
            if op == TokenType.POWER: return left ** right
        
        if op == TokenType.PLUS:
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            if isinstance(left, list) and isinstance(right, list):
                return left + right
            # Coercion fallback
            ln, rn = self._to_num(left), self._to_num(right)
            if ln is not None and rn is not None:
                return ln + rn
            raise RuntimeError(f"Cannot add types '{type(left).__name__}' and '{type(right).__name__}'")
            
        elif op == TokenType.MINUS:
            ln, rn = self._to_num(left), self._to_num(right)
            if ln is not None and rn is not None:
                return ln - rn
            raise RuntimeError(f"Cannot subtract '{type(right).__name__}' from '{type(left).__name__}'")

        elif op == TokenType.EQUALS:
            return left == right
        elif op == TokenType.NOT_EQUALS:
            return left != right
        elif op == TokenType.LESS_THAN:
            return left < right
        elif op == TokenType.GREATER_THAN:
            return left > right
        elif op == TokenType.LESS_THAN_EQUALS:
            return left <= right
        elif op == TokenType.GREATER_THAN_EQUALS:
            return left >= right
        elif op == TokenType.MULTIPLY:
            if isinstance(left, str) and isinstance(right, int):
                return left * right
            if isinstance(left, int) and isinstance(right, str):
                return right * left
            if isinstance(left, list) and isinstance(right, int):
                return left * right
            if isinstance(left, int) and isinstance(right, list):
                return right * left
            ln, rn = self._to_num(left), self._to_num(right)
            if ln is not None and rn is not None:
                return ln * rn
            raise RuntimeError(f"Cannot multiply types '{type(left).__name__}' and '{type(right).__name__}'")
            
        elif op == TokenType.DIVIDE:
            ln, rn = self._to_num(left), self._to_num(right)
            if ln is not None and rn is not None:
                if rn == 0: raise RuntimeError("Division by zero")
                return ln / rn
            raise RuntimeError(f"Cannot divide types '{type(left).__name__}' and '{type(right).__name__}'")
            
        elif op == TokenType.MODULO:
            ln, rn = self._to_num(left), self._to_num(right)
            if ln is not None and rn is not None:
                if rn == 0: raise RuntimeError("Modulo by zero")
                return ln % rn
            raise RuntimeError(f"Cannot calculate modulo for types '{type(left).__name__}' and '{type(right).__name__}'")

        elif op == TokenType.FLOOR_DIVIDE:
            ln, rn = self._to_num(left), self._to_num(right)
            if ln is not None and rn is not None:
                if rn == 0: raise RuntimeError("Floor division by zero")
                return ln // rn
            raise RuntimeError(f"Cannot calculate floor division for types '{type(left).__name__}' and '{type(right).__name__}'")

        elif op == TokenType.POWER:
            ln, rn = self._to_num(left), self._to_num(right)
            if ln is not None and rn is not None:
                return ln ** rn
            raise RuntimeError(f"Cannot calculate power for types '{type(left).__name__}' and '{type(right).__name__}'")

        # Fallback for other tokens
        raise RuntimeError(f"Unsupported binary operator: {op}")
    def evaluate_UnaryOperation(self, expr):
        right = self.evaluate(expr.expr)
        
        if expr.op == TokenType.MINUS:
            return -right
        elif expr.op == TokenType.PLUS:
            return +right
        elif expr.op == TokenType.NOT:
            return not self.is_truthy(right)
        else:
            raise RuntimeError(f"Unknown unary operator: {expr.op}")
    
    def evaluate_FunctionCall(self, expr):
        # Get the function
        # print(f"[DEBUG] evaluate_FunctionCall: {expr.name}")
        callee = self.environment.get(expr.name)
        
        # Evaluate arguments
        arguments = [self.evaluate(arg) for arg in expr.args]
        kwargs = {k: self.evaluate(v) for (k, v) in getattr(expr, 'kwargs', [])}
        
        # Call the function
        if isinstance(callee, Function):
            return callee.call(self, arguments, kwargs=kwargs if kwargs else None)
        elif callable(callee):
            # Python function
            return callee(*arguments, **kwargs)
        else:
            raise RuntimeError(f"'{expr.name}' is not a function")
    
    def evaluate_PythonClassInstance(self, expr):
        # Get the Python class
        class_name = expr.class_name
        
        # Find the class in imported modules
        for module in self.python_modules.values():
            if hasattr(module, class_name):
                cls = getattr(module, class_name)
                
                # Evaluate arguments
                arguments = [self.evaluate(arg) for arg in expr.args]
                kwargs = {k: self.evaluate(v) for (k, v) in getattr(expr, 'kwargs', [])}
                
                # Create an instance of the class
                try:
                    instance = cls(*arguments, **kwargs)
                    return instance
                except Exception as e:
                    raise RuntimeError(f"Error creating instance of '{class_name}': {e}")
        
        raise RuntimeError(f"Python class '{class_name}' not found")
    
    def evaluate_MethodCall(self, expr):
        # Resolve target object: either by name or by evaluating an expression
        if expr.object_name is not None:
            obj = self.environment.try_get(expr.object_name)
            if obj is Environment._MISSING:
                obj = self.global_env.try_get(expr.object_name)
                if obj is Environment._MISSING:
                    raise RuntimeError(f"Undefined variable '{expr.object_name}'")
        elif getattr(expr, 'object_expr', None) is not None:
            obj = self.evaluate(expr.object_expr)
        else:
            raise RuntimeError("Method call has no target object")
        
        # Check if it's a dict and we're accessing a key
        if isinstance(obj, dict):
            if expr.method_name in obj:
                val = obj[expr.method_name]
                # If it's a MethodCall, we should try to call it if it's callable
                arguments = [self.evaluate(arg) for arg in expr.args]
                kwargs = {k: self.evaluate(v) for (k, v) in getattr(expr, 'kwargs', [])}
                if isinstance(val, Function):
                    return val.call(self, arguments, kwargs=kwargs)
                elif callable(val):
                    return val(*arguments, **kwargs)
                return val

        # Evaluate arguments
        arguments = [self.evaluate(arg) for arg in expr.args]
        kwargs = {k: self.evaluate(v) for (k, v) in getattr(expr, 'kwargs', [])}
        
        # Call the method
        if hasattr(obj, expr.method_name):
            method = getattr(obj, expr.method_name)
            if isinstance(method, Function):
                return method.call(self, arguments, kwargs=kwargs if kwargs else None)
            if callable(method):
                return method(*arguments, **kwargs)
            else:
                return method  # Property access
        else:
            raise RuntimeError(f"'{expr.object_name}' has no method '{expr.method_name}'")

    def evaluate_AttributeAccess(self, expr):
        """
        Evaluate attribute access like `obj.prop` preserving full target evaluation.
        Supports Namespace members and TaskHandle properties.
        """
        target = self.evaluate(expr.target)
        # Check if target is a dict
        if isinstance(target, dict):
            if expr.attr_name in target:
                return target[expr.attr_name]
            # Fallback to generic Python attribute access (like .items(), .keys() etc)
        
        # Namespace exposes members via attributes
        if isinstance(target, Namespace):
            if hasattr(target, expr.attr_name):
                return getattr(target, expr.attr_name)
            raise RuntimeError(f"Undefined attribute '{expr.attr_name}' in namespace")
        # TaskHandle special attributes
        if isinstance(target, TaskHandle):
            if expr.attr_name == 'result':
                return target.result
            if expr.attr_name == 'done':
                return target.done
            if expr.attr_name == 'error':
                return target.error
            # Provide join as attribute (callable) if accessed
            if expr.attr_name == 'join':
                return target.join
        # Generic Python attribute access
        if hasattr(target, expr.attr_name):
            return getattr(target, expr.attr_name)
        raise RuntimeError(f"Object has no attribute '{expr.attr_name}'")

    def evaluate_SpawnCall(self, expr):
        """
        Evaluate a spawn call: executes a function (AML or Python) in a separate thread and returns a TaskHandle
        """
        call_node = expr.call_node
        result_container = {'result': None, 'error': None}
        target_name = None

        def _run_callable(callee, args, kwargs):
            try:
                if isinstance(callee, Function):
                    # Run AML function in the same interpreter context; note: may share environment
                    result_container['result'] = callee.call(self, args, kwargs=kwargs if kwargs else None)
                elif callable(callee):
                    result_container['result'] = callee(*args, **kwargs)
                else:
                    raise RuntimeError("Target is not callable")
            except Exception as e:
                result_container['error'] = e

        # Resolve callee and arguments from the call node
        if isinstance(call_node, FunctionCall):
            # Resolve function from current or global environment
            try:
                callee = self.environment.get(call_node.name)
            except RuntimeError:
                callee = self.global_env.get(call_node.name)
            target_name = call_node.name
            args = [self.evaluate(arg) for arg in call_node.args]
            kwargs = {k: self.evaluate(v) for (k, v) in getattr(call_node, 'kwargs', [])}
        elif isinstance(call_node, MethodCall):
            # Resolve object from current or global environment, or evaluate expression target
            if call_node.object_name is not None:
                try:
                    obj = self.environment.get(call_node.object_name)
                except RuntimeError:
                    obj = self.global_env.get(call_node.object_name)
            elif getattr(call_node, 'object_expr', None) is not None:
                obj = self.evaluate(call_node.object_expr)
                # For naming, attempt to derive a readable target if possible
                target_name = f"<expr>.{call_node.method_name}"
            else:
                raise RuntimeError("spawn method call has no target object")
            if hasattr(obj, call_node.method_name):
                callee = getattr(obj, call_node.method_name)
                if not target_name:
                    target_name = f"{call_node.object_name}.{call_node.method_name}" if call_node.object_name else f"<expr>.{call_node.method_name}"
                if isinstance(callee, Function):
                    # AML function attached to object/namespace
                    args = [self.evaluate(arg) for arg in call_node.args]
                    kwargs = {k: self.evaluate(v) for (k, v) in getattr(call_node, 'kwargs', [])}
                else:
                    args = [self.evaluate(arg) for arg in call_node.args]
                    kwargs = {k: self.evaluate(v) for (k, v) in getattr(call_node, 'kwargs', [])}
            else:
                raise RuntimeError(f"'{call_node.object_name}' has no method '{call_node.method_name}'")
        else:
            raise RuntimeError("spawn expects a function or method call")

        t = threading.Thread(target=_run_callable, args=(callee, args, kwargs), name=f"AMLSpawn:{target_name}", daemon=True)
        t.start()
        return TaskHandle(target_name, t, result_container)
    
    def push_file_context(self, path, source_text):
        self._file_ctx_stack.append({'path': path, 'text': source_text, 'lines': None})

    def pop_file_context(self):
        if self._file_ctx_stack:
            self._file_ctx_stack.pop()

    def _current_file_ctx(self):
        if not self._file_ctx_stack:
            return None
        return self._file_ctx_stack[-1]

    def _extract_line_col(self, err):
        msg = str(err)
        m = re.search(r"line\s+(\d+),\s*column\s+(\d+)", msg)
        if m:
            return int(m.group(1)), int(m.group(2))
        return None, None

    def _print_error_with_context(self, message, line, column):
        ctx = self._current_file_ctx()
        path = ctx.get('path') if ctx else None
        lines = ctx.get('lines') if ctx else None
        if ctx and lines is None:
            text = ctx.get('text') or ""
            lines = text.splitlines()
            ctx['lines'] = lines
        if lines is None:
            lines = []
        print(f"Runtime Error: {message}")
        if path:
            print(f"File: {path}, line {line}, column {column}")
        if lines and 1 <= line <= len(lines):
            start = max(1, line - 1)
            end = min(len(lines), line + 1)
            for i in range(start, end + 1):
                prefix = ">" if i == line else " "
                print(f"{prefix} {i}: {lines[i-1]}")

    def _init_dispatch_table(self):
        """
        Initialize the dispatch table for evaluate() to avoid slow isinstance() chains.
        This mirrors the Visitor pattern but using a dictionary lookup.
        """
        self.evaluate_dispatch = {
            # Literals
            Number: self.evaluate_Number,
            String: self.evaluate_String,
            Boolean: self.evaluate_Boolean,
            Null: self.evaluate_Null,
            ListLiteral: self.evaluate_ListLiteral,
            DictLiteral: self.evaluate_DictLiteral,
            
            # Variables and Access
            Identifier: self.evaluate_Identifier,
            AttributeAccess: self.evaluate_AttributeAccess,
            IndexAccess: self.evaluate_IndexAccess,
            
            # Operations
            BinaryOperation: self.evaluate_BinaryOperation,
            UnaryOperation: self.evaluate_UnaryOperation,
            RangeExpression: self.evaluate_RangeExpression,
            Pointer: self.evaluate_Pointer,
            
            # Calls
            FunctionCall: self.evaluate_FunctionCall,
            MethodCall: self.evaluate_MethodCall,
            
            # Python Interop
            PythonClassInstance: self.evaluate_PythonClassInstance,
        }
