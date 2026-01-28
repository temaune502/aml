# Tokens for AML language
# Defines token types and keywords

from enum import Enum, auto

class TokenType(Enum):
    # Basic types
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    
    # Keywords
    IN = auto()
    VAR = auto()
    CONST = auto()
    FUNC = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    IMPORT_PY = auto()
    IMPORT_AML = auto()
    TRY = auto()
    CATCH = auto()
    NAMESPACE = auto()
    SPAWN = auto()
    # New constructs
    META = auto()
    PARALLEL = auto()
    AS = auto()
    RAISE = auto()
    
    # Operators
    PLUS = auto()          # +
    MINUS = auto()         # -
    MULTIPLY = auto()      # *
    DIVIDE = auto()        # /
    MODULO = auto()        # %
    POWER = auto()         # **
    FLOOR_DIVIDE = auto()  # //
    NOT = auto()           # !
    AND = auto()           # &&
    OR = auto()            # ||
    ASSIGN = auto()        # =
    EQUALS = auto()        # ==
    NOT_EQUALS = auto()    # !=
    LESS_THAN = auto()     # <
    GREATER_THAN = auto()  # >
    LESS_THAN_EQUALS = auto()     # <=
    GREATER_THAN_EQUALS = auto()  # >=
    COLON = auto()     # :
    AT = auto()        # @
    # Delimiters
    LPAREN = auto()    # (
    RPAREN = auto()    # )
    LBRACE = auto()    # {
    RBRACE = auto()    # }
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    COMMA = auto()     # ,
    DOT = auto()       # .
    DOT_DOT = auto()   # ..
    BACKSLASH = auto() # \
    NEWLINE = auto()   # \n
    
    BREAK = auto()
    CONTINUE = auto()
    # End of file
    EOF = auto()

# Define keywords
KEYWORDS = {
    'var': TokenType.VAR,
    'const': TokenType.CONST,
    'func': TokenType.FUNC,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'return': TokenType.RETURN,
    'import_py': TokenType.IMPORT_PY,
    'import_aml': TokenType.IMPORT_AML,
    'try': TokenType.TRY,
    'catch': TokenType.CATCH,
    'namespace': TokenType.NAMESPACE,
    'spawn': TokenType.SPAWN,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'in': TokenType.IN,
    'True': TokenType.TRUE,
    'False': TokenType.FALSE,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'null': TokenType.NULL,
    # New keywords
    'meta': TokenType.META,
    'parallel': TokenType.PARALLEL,
    'as': TokenType.AS,
    'raise': TokenType.RAISE
}

class Token:
    __slots__ = ('type', 'value', 'line', 'column')
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self):
        return f'Token({self.type}, {repr(self.value)}, line={self.line}, column={self.column})'
    
    def __repr__(self):
        return self.__str__()