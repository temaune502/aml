_current_interpreter = None

def attach_interpreter(interpreter):
    global _current_interpreter
    _current_interpreter = interpreter

def get_interpreter():
    return _current_interpreter

class RuntimeProxy:
    def __init__(self, interpreter):
        self._interpreter = interpreter
    
    def get_var(self, name):
        return self._interpreter.environment.get(name)
    
    def set_var(self, name, value):
        self._interpreter.environment.define(name, value)
    
    def call(self, func_name, *args):
        # Resolve dotted name if necessary
        parts = func_name.split('.')
        curr = self._interpreter.environment
        val = None
        
        # Simple implementation for now
        if len(parts) == 1:
            val = curr.get(func_name)
        else:
            # Handle namespaces
            val = curr.get(parts[0])
            for part in parts[1:]:
                if hasattr(val, part):
                    val = getattr(val, part)
                elif isinstance(val, dict) and part in val:
                    val = val[part]
                else:
                    val = None
                    break
        
        if val and hasattr(val, 'call'):
            return val.call(self._interpreter, list(args))
        elif callable(val):
            return val(*args)
        return None
