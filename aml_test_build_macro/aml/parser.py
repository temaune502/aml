# Parser for AML language
# Converts tokens into an Abstract Syntax Tree (AST)

from .tokens import TokenType, Token

class AST:
    def __init__(self, token=None):
        self.token = token
        self.line = token.line if token else 0
        self.column = token.column if token else 0

# AST node classes
class Program(AST):
    def __init__(self, statements, token=None):
        super().__init__(token)
        self.statements = statements

class ImportPy(AST):
    def __init__(self, modules, token=None):
        super().__init__(token)
        # modules: list of module specs; each item is either a string module name
        # or a tuple (module_name, alias)
        self.modules = modules

class ImportAml(AST):
    def __init__(self, modules, token=None):
        super().__init__(token)
        self.modules = modules

class VarDeclaration(AST):
    def __init__(self, name, value, token=None):
        super().__init__(token)
        self.name = name
        self.value = value

class ConstDeclaration(AST):
    def __init__(self, name, value, token=None):
        super().__init__(token)
        self.name = name
        self.value = value

class FunctionDeclaration(AST):
    def __init__(self, name, params, body, ns_path=None, token=None):
        super().__init__(token)
        self.name = name
        self.params = params
        self.body = body
        self.ns_path = ns_path or []

class FunctionCall(AST):
    def __init__(self, name, args, kwargs=None, token=None):
        super().__init__(token)
        self.name = name
        self.args = args
        self.kwargs = kwargs or []  # list of (key, valueExpr)

class PythonClassInstance(AST):
    def __init__(self, class_name, args, kwargs=None, token=None):
        super().__init__(token)
        self.class_name = class_name
        self.args = args
        self.kwargs = kwargs or []

class MethodCall(AST):
    def __init__(self, object_name, method_name, args, kwargs=None, object_expr=None, token=None):
        super().__init__(token)
        self.object_name = object_name  # Simple identifier name if available
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs or []
        self.object_expr = object_expr  # Full target expression (e.g., AttributeAccess) when not a simple Identifier

class AttributeAccess(AST):
    def __init__(self, target, attr_name, token=None):
        super().__init__(token)
        self.target = target
        self.attr_name = attr_name

class BinaryOperation(AST):
    def __init__(self, left, op, right, token=None):
        super().__init__(token)
        self.left = left
        self.op = op
        self.right = right

class UnaryOperation(AST):
    def __init__(self, op, expr, token=None):
        super().__init__(token)
        self.op = op
        self.expr = expr

class Pointer(AST):
    def __init__(self, target, token=None):
        super().__init__(token)
        self.target = target

class Number(AST):
    def __init__(self, value, token=None):
        super().__init__(token)
        self.value = value

class String(AST):
    def __init__(self, value, token=None):
        super().__init__(token)
        self.value = value

class Boolean(AST):
    def __init__(self, value, token=None):
        super().__init__(token)
        self.value = value

class RangeExpression(AST):
    def __init__(self, start, end, token=None):
        super().__init__(token)
        self.start = start
        self.end = end

class Null(AST):
    def __init__(self, token=None):
        super().__init__(token)

class Identifier(AST):
    def __init__(self, name, token=None):
        super().__init__(token)
        self.name = name

class ListLiteral(AST):
    def __init__(self, elements, token=None):
        super().__init__(token)
        self.elements = elements

class ListComprehension(AST):
    def __init__(self, expression, var_name, iterable, condition=None, token=None):
        super().__init__(token)
        self.expression = expression
        self.var_name = var_name
        self.iterable = iterable
        self.condition = condition

class DictLiteral(AST):
    def __init__(self, elements, token=None):
        super().__init__(token)
        self.elements = elements  # list of (key, value) tuples

class DictComprehension(AST):
    def __init__(self, key_expression, value_expression, var_name, iterable, condition=None, token=None):
        super().__init__(token)
        self.key_expression = key_expression
        self.value_expression = value_expression
        self.var_name = var_name
        self.iterable = iterable
        self.condition = condition

class IndexAccess(AST):
    def __init__(self, target, index, token=None):
        super().__init__(token)
        self.target = target
        self.index = index

class IfStatement(AST):
    def __init__(self, condition, if_body, else_body=None, token=None):
        super().__init__(token)
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

class WhileStatement(AST):
    def __init__(self, condition, body, token=None):
        super().__init__(token)
        self.condition = condition
        self.body = body

class ForStatement(AST):
    def __init__(self, var_name, iterable, body, token=None):
        super().__init__(token)
        self.var_name = var_name
        self.iterable = iterable
        self.body = body

class ReturnStatement(AST):
    def __init__(self, value, token=None):
        super().__init__(token)
        self.value = value

class RaiseStatement(AST):
    def __init__(self, expression, token=None):
        super().__init__(token)
        self.expression = expression

class Assignment(AST):
    def __init__(self, name, value, target_expr=None, token=None):
        super().__init__(token)
        self.name = name
        self.value = value
        # Якщо присвоєння вигляду a.b.c = expr, зберігаємо повний вираз цілі
        # (AttributeAccess або IndexAccess) у target_expr
        self.target_expr = target_expr

class BreakStatement(AST):
    def __init__(self, token=None):
        super().__init__(token)

class ContinueStatement(AST):
    def __init__(self, token=None):
        super().__init__(token)

class TryCatchStatement(AST):
    def __init__(self, try_body, catch_body, error_var=None, token=None):
        super().__init__(token)
        self.try_body = try_body
        self.catch_body = catch_body
        self.error_var = error_var

class NamespaceDeclaration(AST):
    def __init__(self, name, body, token=None):
        super().__init__(token)
        self.name = name
        self.body = body

class SpawnCall(AST):
    def __init__(self, call_node, token=None):
        super().__init__(token)
        self.call_node = call_node

class MetadataDeclaration(AST):
    def __init__(self, elements, token=None):
        super().__init__(token)
        # list of (key, value) tuples; keys are strings
        self.elements = elements

class ParallelBlock(AST):
    def __init__(self, body, token=None):
        super().__init__(token)
        self.body = body

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    # Optimization: constant folding for binary operations
    def _try_fold_binary(self, left, op_type, right):
        try:
            if isinstance(left, Number) and isinstance(right, Number):
                a, b = left.value, right.value
                if op_type == TokenType.PLUS:
                    return Number(a + b)
                if op_type == TokenType.MINUS:
                    return Number(a - b)
                if op_type == TokenType.MULTIPLY:
                    return Number(a * b)
                if op_type == TokenType.DIVIDE:
                    if b == 0:
                        return None
                    return Number(a / b)
                if op_type == TokenType.FLOOR_DIVIDE:
                    if b == 0:
                        return None
                    return Number(a // b)
                if op_type == TokenType.POWER:
                    return Number(a ** b)
                if op_type == TokenType.MODULO:
                    return Number(a % b)
                if op_type == TokenType.EQUALS:
                    return Boolean(a == b)
                if op_type == TokenType.NOT_EQUALS:
                    return Boolean(a != b)
                if op_type == TokenType.LESS_THAN:
                    return Boolean(a < b)
                if op_type == TokenType.GREATER_THAN:
                    return Boolean(a > b)
                if op_type == TokenType.LESS_THAN_EQUALS:
                    return Boolean(a <= b)
                if op_type == TokenType.GREATER_THAN_EQUALS:
                    return Boolean(a >= b)

            if isinstance(left, String) and isinstance(right, String):
                a, b = left.value, right.value
                if op_type == TokenType.PLUS:
                    return String(a + b)
                if op_type == TokenType.EQUALS:
                    return Boolean(a == b)
                if op_type == TokenType.NOT_EQUALS:
                    return Boolean(a != b)
                if op_type == TokenType.LESS_THAN:
                    return Boolean(a < b)
                if op_type == TokenType.GREATER_THAN:
                    return Boolean(a > b)
                if op_type == TokenType.LESS_THAN_EQUALS:
                    return Boolean(a <= b)
                if op_type == TokenType.GREATER_THAN_EQUALS:
                    return Boolean(a >= b)

            if op_type == TokenType.PLUS:
                if isinstance(left, String) and isinstance(right, Number):
                    return String(left.value + str(right.value))
                if isinstance(left, Number) and isinstance(right, String):
                    return String(str(left.value) + right.value)

            if isinstance(left, Boolean) and isinstance(right, Boolean):
                a, b = left.value, right.value
                if op_type == TokenType.EQUALS:
                    return Boolean(a == b)
                if op_type == TokenType.NOT_EQUALS:
                    return Boolean(a != b)
            return None
        except Exception:
            return None

    def _make_binary(self, left, op_token, right):
        folded = self._try_fold_binary(left, op_token.type, right)
        if folded is not None:
            return folded
        return BinaryOperation(left, op_token.type, right, token=op_token)
    
    def error(self, message="Invalid syntax"):
        token = self.current_token
        raise Exception(f"{message} at line {token.line}, column {token.column}")
    
    def eat(self, token_type):
        """
        Compare the current token type with the passed token type
        and if they match, "eat" the current token and assign the
        next token to the current_token, otherwise raise an exception.
        """
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = None
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")
    
    def peek(self, offset=1):
        """
        Return the token at the current position + offset without advancing
        """
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def program(self):
        """
        program : statement_list
        """
        statements = self.statement_list()
        return Program(statements)
    
    def statement_list(self, end_type=None):
        """
        statement_list : statement*
        """
        statements = []
        
        while self.current_token and self.current_token.type != TokenType.EOF and (end_type is None or self.current_token.type != end_type):
            # Skip newlines between statements
            while self.current_token and self.current_token.type == TokenType.NEWLINE:
                self.eat(TokenType.NEWLINE)
                
            if self.current_token and self.current_token.type != TokenType.EOF and (end_type is None or self.current_token.type != end_type):
                statements.append(self.statement())
                
                # Skip newlines after statements
                while self.current_token and self.current_token.type == TokenType.NEWLINE:
                    self.eat(TokenType.NEWLINE)
        
        return statements
    
    def statement(self):
        """
        statement : import_statement
                  | var_declaration
                  | assignment_statement
                  | function_declaration
                  | namespace_declaration
                  | meta_statement
                  | parallel_statement
                  | if_statement
                  | while_statement
                  | for_statement
                  | return_statement
                  | try_catch_statement
                  | expression_statement
        """
        if self.current_token.type == TokenType.IMPORT_PY:
            return self.import_py_statement()
        elif self.current_token.type == TokenType.IMPORT_AML:
            return self.import_aml_statement()
        elif self.current_token.type == TokenType.VAR:
            return self.var_declaration()
        elif self.current_token.type == TokenType.CONST:
            return self.const_declaration()
        elif self.current_token.type == TokenType.META:
            return self.meta_statement()
        elif self.current_token.type == TokenType.PARALLEL:
            return self.parallel_statement()
        # Підтримка присвоєнь до атрибутів та індексів: a.b.c = expr, a[b] = expr
        elif self.current_token.type == TokenType.IDENTIFIER and self.peek() and self.peek().type in (TokenType.DOT, TokenType.LBRACKET):
            # Парсимо ліву частину як ланцюжок доступів без викликів
            lhs = self.call()
            if self.current_token and self.current_token.type == TokenType.ASSIGN and isinstance(lhs, (AttributeAccess, IndexAccess)):
                assign_token = lhs.token
                self.eat(TokenType.ASSIGN)
                value = self.expression()
                return Assignment(None, value, target_expr=lhs, token=assign_token)
            # Підтримка розширених присвоєнь: a.b.c += expr, a.b[i] *= expr, тощо
            elif (self.current_token and self.peek() and 
                  self.current_token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO, TokenType.FLOOR_DIVIDE, TokenType.POWER, TokenType.AND, TokenType.OR) and 
                  self.peek().type == TokenType.ASSIGN and isinstance(lhs, (AttributeAccess, IndexAccess))):
                op_token = self.current_token
                self.eat(op_token.type)
                self.eat(TokenType.ASSIGN)
                rhs = self.expression()
                value = BinaryOperation(lhs, op_token.type, rhs, token=op_token)
                return Assignment(None, value, target_expr=lhs, token=op_token)
            else:
                # Якщо це не присвоєння, трактуємо як вираз
                return lhs
        elif self.current_token.type == TokenType.IDENTIFIER and self.peek() and (
            self.peek().type == TokenType.ASSIGN or 
            (self.peek().type in (TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO, TokenType.FLOOR_DIVIDE, TokenType.POWER, TokenType.AND, TokenType.OR) and 
             self.peek(2) and self.peek(2).type == TokenType.ASSIGN)
        ):
            return self.assignment_statement()
        elif self.current_token.type == TokenType.FUNC:
            return self.function_declaration()
        elif self.current_token.type == TokenType.NAMESPACE:
            return self.namespace_declaration()
        elif self.current_token.type == TokenType.IF:
            return self.if_statement()
        elif self.current_token.type == TokenType.WHILE:
            return self.while_statement()
        elif self.current_token.type == TokenType.FOR:
            return self.for_statement()
        elif self.current_token.type == TokenType.RETURN:
            return self.return_statement()
        elif self.current_token.type == TokenType.RAISE:
            return self.raise_statement()
        elif self.current_token.type == TokenType.TRY:
            return self.try_catch_statement()
        elif self.current_token.type == TokenType.BREAK:
            break_token = self.current_token
            self.eat(TokenType.BREAK)
            return BreakStatement(token=break_token)
        elif self.current_token.type == TokenType.CONTINUE:
            continue_token = self.current_token
            self.eat(TokenType.CONTINUE)
            return ContinueStatement(token=continue_token)
        else:
            return self.expression_statement()

    def meta_statement(self):
        """
        meta_statement : META LBRACE (meta_pair (COMMA meta_pair)*)? RBRACE
        meta_pair      : (IDENTIFIER | STRING) COLON expression
        """
        meta_tok = self.current_token
        self.eat(TokenType.META)
        self.eat(TokenType.LBRACE)

        elements = []
        # Allow newlines
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)

        def parse_key():
            if self.current_token.type == TokenType.IDENTIFIER:
                key = self.current_token.value
                self.eat(TokenType.IDENTIFIER)
                return key
            elif self.current_token.type == TokenType.STRING:
                key = self.current_token.value
                self.eat(TokenType.STRING)
                return key
            else:
                self.error("Expected identifier or string as metadata key")

        if self.current_token and self.current_token.type != TokenType.RBRACE:
            key = parse_key()
            self.eat(TokenType.COLON)
            val = self.expression()
            elements.append((key, val))
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                # Skip newlines
                while self.current_token and self.current_token.type == TokenType.NEWLINE:
                    self.eat(TokenType.NEWLINE)
                key = parse_key()
                self.eat(TokenType.COLON)
                val = self.expression()
                elements.append((key, val))

        # Allow trailing newlines
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)

        self.eat(TokenType.RBRACE)
        return MetadataDeclaration(elements, token=meta_tok)

    def parallel_statement(self):
        """
        parallel_statement : PARALLEL LBRACE statement_list RBRACE
        """
        par_tok = self.current_token
        self.eat(TokenType.PARALLEL)
        self.eat(TokenType.LBRACE)
        body = self.statement_list(end_type=TokenType.RBRACE)
        self.eat(TokenType.RBRACE)
        return ParallelBlock(body, token=par_tok)

    def assignment_statement(self):
        """
        assignment_statement : IDENTIFIER ASSIGN expression
                             | IDENTIFIER (PLUS|MINUS|MULTIPLY|DIVIDE|MODULO) ASSIGN expression
        """
        name_token = self.current_token
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        # Звичайне присвоєння
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            value = self.expression()
            return Assignment(name, value, token=name_token)
        # Розширене присвоєння: x += expr, x -= expr, x *= expr, x /= expr, x %= expr
        elif self.current_token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO, TokenType.FLOOR_DIVIDE, TokenType.POWER, TokenType.AND, TokenType.OR) and self.peek() and self.peek().type == TokenType.ASSIGN:
            op_token = self.current_token
            self.eat(op_token.type)
            self.eat(TokenType.ASSIGN)
            rhs = self.expression()
            # Створюємо BinaryOperation (x <op> rhs) як значення
            left_ident = Identifier(name, token=name_token)
            value = self._make_binary(left_ident, op_token, rhs)
            return Assignment(name, value, token=name_token)
        else:
            # Неочікуваний патерн після IDENTIFIER
            self.error("Invalid assignment syntax")
    
    def module_name(self):
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        while self.current_token and self.current_token.type in (TokenType.DOT, TokenType.BACKSLASH, TokenType.DIVIDE):
            sep = self.current_token.value
            self.eat(self.current_token.type)
            name += sep + self.current_token.value
            self.eat(TokenType.IDENTIFIER)
        return name

    def import_py_statement(self):
        """
        import_py_statement : IMPORT_PY (LBRACE import_items RBRACE | STRING (AS IDENTIFIER)?)
        import_items       : (module_name (AS IDENTIFIER)? (COMMA module_name (AS IDENTIFIER)? )*)?
        """
        import_token = self.current_token
        self.eat(TokenType.IMPORT_PY)

        modules = []

        if self.current_token.type == TokenType.LBRACE:
            self.eat(TokenType.LBRACE)
            # Skip newlines
            while self.current_token.type == TokenType.NEWLINE:
                self.eat(TokenType.NEWLINE)

            # Parse items with optional commas and alias via 'as'
            if self.current_token.type != TokenType.RBRACE:
                while True:
                    if self.current_token.type not in (TokenType.IDENTIFIER, TokenType.STRING):
                        break
                    
                    if self.current_token.type == TokenType.STRING:
                        module_name = self.current_token.value
                        self.eat(TokenType.STRING)
                    else:
                        module_name = self.module_name()

                    alias = None
                    if self.current_token.type == TokenType.AS:
                        self.eat(TokenType.AS)
                        alias = self.current_token.value
                        self.eat(TokenType.IDENTIFIER)
                    modules.append((module_name, alias) if alias else module_name)
                    # Skip newlines after item
                    while self.current_token.type == TokenType.NEWLINE:
                        self.eat(TokenType.NEWLINE)
                    if self.current_token.type == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                        while self.current_token.type == TokenType.NEWLINE:
                            self.eat(TokenType.NEWLINE)
                        continue
                    else:
                        break

            self.eat(TokenType.RBRACE)
        else:
            # Simple form: import_py "module" [as alias]
            module_name = self.current_token.value
            self.eat(TokenType.STRING)
            alias = None
            if self.current_token.type == TokenType.AS:
                self.eat(TokenType.AS)
                alias = self.current_token.value
                self.eat(TokenType.IDENTIFIER)
            modules.append((module_name, alias) if alias else module_name)

        return ImportPy(modules, token=import_token)
    
    def import_aml_statement(self):
        """
        import_aml_statement : IMPORT_AML LBRACE module_list_commas RBRACE
        """
        import_token = self.current_token
        self.eat(TokenType.IMPORT_AML)
        self.eat(TokenType.LBRACE)
        
        modules = []
        
        # Skip newlines
        while self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)
        
        # Parse module names with optional commas
        if self.current_token.type != TokenType.RBRACE:
            while True:
                if self.current_token.type != TokenType.IDENTIFIER:
                    break
                module_name = self.module_name()
                modules.append(module_name)
                while self.current_token.type == TokenType.NEWLINE:
                    self.eat(TokenType.NEWLINE)
                if self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    while self.current_token.type == TokenType.NEWLINE:
                        self.eat(TokenType.NEWLINE)
                    continue
                else:
                    break
        
        self.eat(TokenType.RBRACE)
        return ImportAml(modules, token=import_token)
    
    def var_declaration(self):
        """
        var_declaration : VAR IDENTIFIER ASSIGN expression
        """
        var_token = self.current_token
        self.eat(TokenType.VAR)
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        value = self.expression()
        return VarDeclaration(var_name, value, token=var_token)

    def const_declaration(self):
        """
        const_declaration : CONST IDENTIFIER ASSIGN expression
        """
        const_token = self.current_token
        self.eat(TokenType.CONST)
        const_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        value = self.expression()
        return ConstDeclaration(const_name, value, token=const_token)

    def function_declaration(self):
        """
        function_declaration : FUNC dotted_ident LPAREN param_list RPAREN LBRACE statement_list RBRACE
        dotted_ident         : IDENTIFIER (DOT IDENTIFIER)*
        """
        func_token = self.current_token
        self.eat(TokenType.FUNC)
        first_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        ns_path = []
        func_name = first_name
        while self.current_token and self.current_token.type == TokenType.DOT:
            self.eat(TokenType.DOT)
            next_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            ns_path.append(func_name)
            func_name = next_name
        self.eat(TokenType.LPAREN)
        params = self.param_list()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        while self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)
        body = self.statement_list(end_type=TokenType.RBRACE)
        self.eat(TokenType.RBRACE)
        return FunctionDeclaration(func_name, params, body, ns_path=ns_path, token=func_token)

    def namespace_declaration(self):
        """
        namespace_declaration : NAMESPACE IDENTIFIER LBRACE statement_list RBRACE
        """
        ns_token = self.current_token
        self.eat(TokenType.NAMESPACE)
        ns_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LBRACE)

        # Skip newlines after opening brace
        while self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)

        body = self.statement_list(end_type=TokenType.RBRACE)
        self.eat(TokenType.RBRACE)
        return NamespaceDeclaration(ns_name, body, token=ns_token)
    
    def param_list(self):
        """
        param_list : (IDENTIFIER (ASSIGN expression)? (COMMA IDENTIFIER (ASSIGN expression)? )*)?
        Returns list of names or (name, defaultExpr)
        """
        params = []
        if self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            if self.current_token and self.current_token.type == TokenType.ASSIGN:
                self.eat(TokenType.ASSIGN)
                default_expr = self.expression()
                params.append((name, default_expr))
            else:
                params.append(name)
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                name = self.current_token.value
                self.eat(TokenType.IDENTIFIER)
                if self.current_token and self.current_token.type == TokenType.ASSIGN:
                    self.eat(TokenType.ASSIGN)
                    default_expr = self.expression()
                    params.append((name, default_expr))
                else:
                    params.append(name)
        return params
    
    def if_statement(self):
        """
        if_statement : IF LPAREN expression RPAREN LBRACE statement_list RBRACE (ELSE LBRACE statement_list RBRACE)?
        """
        if_token = self.current_token
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        condition = self.expression()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        
        # Skip newlines after opening brace
        while self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)
        
        if_body = self.statement_list(end_type=TokenType.RBRACE)
        self.eat(TokenType.RBRACE)
        
        else_body = None
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            self.eat(TokenType.LBRACE)
            
            # Skip newlines after opening brace
            while self.current_token.type == TokenType.NEWLINE:
                self.eat(TokenType.NEWLINE)
            
            else_body = self.statement_list(end_type=TokenType.RBRACE)
            self.eat(TokenType.RBRACE)
        
        return IfStatement(condition, if_body, else_body, token=if_token)
    
    def while_statement(self):
        """
        while_statement : WHILE LPAREN expression RPAREN LBRACE statement_list RBRACE
        """
        while_token = self.current_token
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        condition = self.expression()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        
        # Skip newlines after opening brace
        while self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)
        
        body = self.statement_list(end_type=TokenType.RBRACE)
        self.eat(TokenType.RBRACE)
        return WhileStatement(condition, body, token=while_token)
    
    def for_statement(self):
        """
        for_statement : FOR (LPAREN)? IDENTIFIER IN expression (RPAREN)? LBRACE statement_list RBRACE
        """
        for_token = self.current_token
        self.eat(TokenType.FOR)
        
        has_paren = False
        if self.current_token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            has_paren = True
            
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.IN)
        iterable = self.expression()
        
        if has_paren:
            self.eat(TokenType.RPAREN)
            
        self.eat(TokenType.LBRACE)
        
        # Skip newlines after opening brace
        while self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)
        
        body = self.statement_list(end_type=TokenType.RBRACE)
        self.eat(TokenType.RBRACE)
        return ForStatement(var_name, iterable, body, token=for_token)
    
    def return_statement(self):
        """
        return_statement : RETURN expression?
        """
        token = self.current_token
        self.eat(TokenType.RETURN)
        value = None
        if self.current_token and self.current_token.type not in (TokenType.NEWLINE, TokenType.RBRACE, TokenType.EOF):
            value = self.expression()
        return ReturnStatement(value, token=token)

    def raise_statement(self):
        """
        raise_statement : RAISE expression
        """
        token = self.current_token
        self.eat(TokenType.RAISE)
        expression = self.expression()
        return RaiseStatement(expression, token=token)
    
    def expression_statement(self):
        """
        expression_statement : expression
        """
        return self.expression()
    
    def expression(self):
        """
        expression : range_expr
        """
        return self.range_expr()

    def range_expr(self):
        """
        range_expr : logic_or (DOT_DOT logic_or)?
        """
        node = self.logic_or()
        
        if self.current_token.type == TokenType.DOT_DOT:
            token = self.current_token
            self.eat(TokenType.DOT_DOT)
            end = self.logic_or()
            return RangeExpression(node, end, token=token)
            
        return node

    def logic_or(self):
        """
        logic_or : logic_and (OR logic_and)*
        """
        node = self.logic_and()

        while self.current_token and self.current_token.type == TokenType.OR:
            token = self.current_token
            self.eat(TokenType.OR)
            right = self.logic_and()
            node = BinaryOperation(left=node, op=TokenType.OR, right=right, token=token)

        return node

    def logic_and(self):
        """
        logic_and : equality (AND equality)*
        """
        node = self.equality()

        while self.current_token and self.current_token.type == TokenType.AND:
            token = self.current_token
            self.eat(TokenType.AND)
            right = self.equality()
            node = BinaryOperation(left=node, op=TokenType.AND, right=right, token=token)

        return node
    
    def equality(self):
        """
        equality : comparison ((EQUALS | NOT_EQUALS) comparison)*
        """
        node = self.comparison()
        
        while self.current_token and (self.current_token.type == TokenType.EQUALS or 
                                     self.current_token.type == TokenType.NOT_EQUALS):
            op = self.current_token
            self.eat(self.current_token.type)
            right = self.comparison()
            node = self._make_binary(node, op, right)
        
        return node
    
    def comparison(self):
        """
        comparison : term ((LESS_THAN | GREATER_THAN | LESS_THAN_EQUALS | GREATER_THAN_EQUALS) term)*
        """
        node = self.term()
        
        while self.current_token and (self.current_token.type == TokenType.LESS_THAN or 
                                     self.current_token.type == TokenType.GREATER_THAN or
                                     self.current_token.type == TokenType.LESS_THAN_EQUALS or
                                     self.current_token.type == TokenType.GREATER_THAN_EQUALS):
            op = self.current_token
            self.eat(self.current_token.type)
            right = self.term()
            node = self._make_binary(node, op, right)
            
        return node
    
    def term(self):
        """
        term : factor ((PLUS | MINUS) factor)*
        """
        node = self.factor()
        
        while self.current_token and (self.current_token.type == TokenType.PLUS or 
                                     self.current_token.type == TokenType.MINUS):
            op = self.current_token
            self.eat(self.current_token.type)
            right = self.factor()
            node = self._make_binary(node, op, right)
        
        return node
    
    def factor(self):
        """
        factor : unary ((MULTIPLY | DIVIDE | MODULO | FLOOR_DIVIDE | POWER) unary)*
        """
        node = self.unary()
        
        while self.current_token and (self.current_token.type == TokenType.MULTIPLY or 
                                     self.current_token.type == TokenType.DIVIDE or 
                                     self.current_token.type == TokenType.MODULO or 
                                     self.current_token.type == TokenType.FLOOR_DIVIDE or 
                                     self.current_token.type == TokenType.POWER):
            op = self.current_token
            self.eat(self.current_token.type)
            right = self.unary()
            node = self._make_binary(node, op, right)

        return node
    
    def unary(self):
        """
        unary : (MINUS | PLUS | NOT | AT) unary | (SPAWN call) | call
        """
        if self.current_token.type == TokenType.MINUS or self.current_token.type == TokenType.PLUS or self.current_token.type == TokenType.NOT:
            op = self.current_token
            self.eat(self.current_token.type)
            expr = self.unary()
            return UnaryOperation(op.type, expr)

        if self.current_token.type == TokenType.AT:
            at_token = self.current_token
            self.eat(TokenType.AT)
            # A pointer is typically @Identifier or @AttributeAccess
            target = self.call()
            return Pointer(target, token=at_token)

        if self.current_token.type == TokenType.SPAWN:
            spawn_token = self.current_token
            self.eat(TokenType.SPAWN)
            call_node = self.call()
            return SpawnCall(call_node, token=spawn_token)

        return self.call()
    
    def call(self):
        """
        call : primary (LPAREN argument_list RPAREN | DOT IDENTIFIER (LPAREN argument_list RPAREN)? | LBRACKET expression RBRACKET)*
        """
        node = self.primary()
        
        while True:
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                call_token = self.current_token
                self.eat(TokenType.LPAREN)
                args, kwargs = self.argument_list()
                self.eat(TokenType.RPAREN)
                
                if isinstance(node, Identifier):
                    # Function call
                    node = FunctionCall(node.name, args, kwargs=kwargs, token=call_token)
                elif isinstance(node, MethodCall):
                    # Method call with arguments
                    node.args = args
                    node.kwargs = kwargs
            elif self.current_token and self.current_token.type == TokenType.DOT:
                dot_token = self.current_token
                self.eat(TokenType.DOT)
                method_name = self.current_token.value
                self.eat(TokenType.IDENTIFIER)
                
                if isinstance(node, Identifier) and node.name == "Python":
                    # Python class reference
                    if self.current_token and self.current_token.type == TokenType.LPAREN:
                        self.eat(TokenType.LPAREN)
                        args, kwargs = self.argument_list()
                        self.eat(TokenType.RPAREN)
                        node = PythonClassInstance(method_name, args, kwargs=kwargs, token=dot_token)
                    else:
                        node = PythonClassInstance(method_name, [], kwargs=[], token=dot_token)
                else:
                    # Attribute or method call
                    if self.current_token and self.current_token.type == TokenType.LPAREN:
                        # Method call: preserve full target expression if not a simple identifier
                        self.eat(TokenType.LPAREN)
                        args, kwargs = self.argument_list()
                        self.eat(TokenType.RPAREN)
                        if isinstance(node, Identifier):
                            object_name = node.name
                            object_expr = None
                        else:
                            object_name = None
                            object_expr = node
                        node = MethodCall(object_name, method_name, args, kwargs=kwargs, object_expr=object_expr, token=dot_token)
                    else:
                        # Attribute access: preserve full target expression
                        node = AttributeAccess(node, method_name, token=dot_token)
            elif self.current_token and self.current_token.type == TokenType.LBRACKET:
                bracket_token = self.current_token
                self.eat(TokenType.LBRACKET)
                # Allow newlines inside brackets
                while self.current_token and self.current_token.type == TokenType.NEWLINE:
                    self.eat(TokenType.NEWLINE)
                index_expr = self.expression()
                while self.current_token and self.current_token.type == TokenType.NEWLINE:
                    self.eat(TokenType.NEWLINE)
                self.eat(TokenType.RBRACKET)
                node = IndexAccess(node, index_expr, token=bracket_token)
            else:
                break
        
        return node
    
    def argument_list(self):
        """
        argument_list : (positional_or_kwarg (COMMA positional_or_kwarg)*)?
        positional_or_kwarg : expression | IDENTIFIER ASSIGN expression
        Returns: (args_list, kwargs_pairs)
        """
        args = []
        kwargs = []  # list of (key, valueExpr)

        if self.current_token.type == TokenType.RPAREN:
            return args, kwargs

        # First item
        if self.current_token.type == TokenType.IDENTIFIER and self.peek() and self.peek().type == TokenType.ASSIGN:
            key = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.ASSIGN)
            val_expr = self.expression()
            kwargs.append((key, val_expr))
        else:
            args.append(self.expression())

        # Subsequent items
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            if self.current_token.type == TokenType.IDENTIFIER and self.peek() and self.peek().type == TokenType.ASSIGN:
                key = self.current_token.value
                self.eat(TokenType.IDENTIFIER)
                self.eat(TokenType.ASSIGN)
                val_expr = self.expression()
                kwargs.append((key, val_expr))
            else:
                args.append(self.expression())

        return args, kwargs
    
    def primary(self):
        """
        primary : NUMBER | STRING | TRUE | FALSE | IDENTIFIER | LPAREN expression RPAREN | list_literal | dict_literal
        """
        token = self.current_token
        
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return Number(token.value, token=token)
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return String(token.value, token=token)
        elif token.type == TokenType.TRUE:
            self.eat(TokenType.TRUE)
            return Boolean(True, token=token)
        elif token.type == TokenType.FALSE:
            self.eat(TokenType.FALSE)
            return Boolean(False, token=token)
        elif token.type == TokenType.NULL:
            self.eat(TokenType.NULL)
            return Null(token=token)
        # Allow using reserved keyword 'meta' as a variable name in expressions
        elif token.type == TokenType.META:
            self.eat(TokenType.META)
            return Identifier('meta', token=token)
        elif token.type == TokenType.IDENTIFIER:
            self.eat(TokenType.IDENTIFIER)
            return Identifier(token.value, token=token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            expr = self.expression()
            self.eat(TokenType.RPAREN)
            return expr
        elif token.type == TokenType.LBRACKET:
            return self.list_literal()
        elif token.type == TokenType.LBRACE:
            return self.dict_literal()
        else:
            self.error(f"Unexpected token: {token}")
    
    def list_literal(self):
        """
        list_literal : LBRACKET (expression (COMMA expression)* | expression FOR IDENTIFIER IN expression (IF expression)?)? RBRACKET
        """
        bracket_token = self.current_token
        self.eat(TokenType.LBRACKET)
        
        if self.current_token.type == TokenType.RBRACKET:
            self.eat(TokenType.RBRACKET)
            return ListLiteral([], token=bracket_token)
            
        first_expr = self.expression()
        
        # Check for list comprehension
        if self.current_token.type == TokenType.FOR:
            self.eat(TokenType.FOR)
            var_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.IN)
            iterable = self.expression()
            
            condition = None
            if self.current_token.type == TokenType.IF:
                self.eat(TokenType.IF)
                condition = self.expression()
                
            self.eat(TokenType.RBRACKET)
            return ListComprehension(first_expr, var_name, iterable, condition, token=bracket_token)
            
        # Regular list literal
        elements = [first_expr]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            elements.append(self.expression())
        
        self.eat(TokenType.RBRACKET)
        return ListLiteral(elements, token=bracket_token)

    def dict_literal(self):
        """
        dict_literal : LBRACE (key_value (COMMA key_value)* | key_expr COLON val_expr FOR IDENTIFIER IN expression (IF expression)?)? RBRACE
        key_value   : (STRING | IDENTIFIER) COLON expression
        """
        brace_token = self.current_token
        self.eat(TokenType.LBRACE)
        
        # Skip newlines after opening brace
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)

        if self.current_token and self.current_token.type == TokenType.RBRACE:
            self.eat(TokenType.RBRACE)
            return DictLiteral([], token=brace_token)

        def parse_key_node():
            if self.current_token.type == TokenType.STRING:
                key_token = self.current_token
                self.eat(TokenType.STRING)
                return String(key_token.value, token=key_token)
            elif self.current_token.type == TokenType.IDENTIFIER:
                # In standard dict literal, identifier is a string key
                # In comprehension, it could be an expression.
                key_token = self.current_token
                self.eat(TokenType.IDENTIFIER)
                return String(key_token.value, token=key_token)
            else:
                self.error("Expected STRING or IDENTIFIER as dictionary key")

        # We need to distinguish between {key: val, ...} and {key: val for ...}
        # First, parse the first key. But in comprehension, key can be any expression.
        
        # Save state for possible backtracking or just peek
        first_key = self.expression()
        self.eat(TokenType.COLON)
        first_val = self.expression()
        
        # Check for comprehension
        if self.current_token and self.current_token.type == TokenType.FOR:
            self.eat(TokenType.FOR)
            var_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.IN)
            iterable = self.expression()
            
            condition = None
            if self.current_token and self.current_token.type == TokenType.IF:
                self.eat(TokenType.IF)
                condition = self.expression()
            
            while self.current_token and self.current_token.type == TokenType.NEWLINE:
                self.eat(TokenType.NEWLINE)
            self.eat(TokenType.RBRACE)
            return DictComprehension(first_key, first_val, var_name, iterable, condition, token=brace_token)

        # Regular dict literal
        pairs = [(first_key, first_val)]
        while self.current_token and self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            while self.current_token and self.current_token.type == TokenType.NEWLINE:
                self.eat(TokenType.NEWLINE)
            if self.current_token and self.current_token.type == TokenType.RBRACE:
                break
            k = self.expression()
            self.eat(TokenType.COLON)
            v = self.expression()
            pairs.append((k, v))
            while self.current_token and self.current_token.type == TokenType.NEWLINE:
                self.eat(TokenType.NEWLINE)

        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)
        self.eat(TokenType.RBRACE)
        return DictLiteral(pairs, token=brace_token)

    def try_catch_statement(self):
        """
        try_catch_statement : TRY LBRACE statement_list RBRACE CATCH (LPAREN IDENTIFIER RPAREN)? LBRACE statement_list RBRACE
        """
        try_token = self.current_token
        self.eat(TokenType.TRY)
        self.eat(TokenType.LBRACE)
        while self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)
        try_body = self.statement_list(end_type=TokenType.RBRACE)
        self.eat(TokenType.RBRACE)

        self.eat(TokenType.CATCH)
        
        error_var = None
        if self.current_token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            error_var = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.RPAREN)

        self.eat(TokenType.LBRACE)
        while self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)
        catch_body = self.statement_list(end_type=TokenType.RBRACE)
        self.eat(TokenType.RBRACE)

        return TryCatchStatement(try_body, catch_body, error_var=error_var, token=try_token)
    
    def parse(self):
        """
        Parse the token stream and return an AST
        """
        return self.program()