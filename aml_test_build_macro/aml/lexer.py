# Lexer for AML language
# Converts source code into tokens

from .tokens import Token, TokenType, KEYWORDS

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
        self.line = 1
        self.column = 1
    
    def error(self):
        raise Exception(f'Invalid character: {self.current_char} at line {self.line}, column {self.column}')
    
    def advance(self):
        """
        Advance the position pointer and set the current character
        """
        self.pos += 1
        self.column += 1
        
        if self.pos >= len(self.text):
            self.current_char = None  # End of input
        else:
            self.current_char = self.text[self.pos]
            
            # Handle newlines for line counting
            if self.current_char == '\n':
                self.line += 1
                self.column = 0
    
    def peek(self):
        """
        Return the next character without advancing the position
        """
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        else:
            return self.text[peek_pos]

    def peek_n(self, n):
        """
        Return the character n positions ahead without advancing
        """
        peek_pos = self.pos + n
        if peek_pos >= len(self.text):
            return None
        else:
            return self.text[peek_pos]
    
    def skip_whitespace(self):
        """
        Skip whitespace characters
        """
        while self.current_char is not None and self.current_char.isspace() and self.current_char != '\n':
            self.advance()
    
    def skip_comment(self):
        """
        Skip comments in the source code
        Comments start with // and end with a newline
        """
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
    
    def number(self):
        """
        Parse a number from the source code
        """
        result = ''
        token_column = self.column
        
        # Handle negative numbers
        if self.current_char == '-':
            result += self.current_char
            self.advance()
        
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
            
        # Look for fractional part
        if self.current_char == '.':
            # Check if it's actually a range operator '..'
            if self.peek() == '.':
                # It is a range '..', so stop parsing the number here.
                # '1..10' -> NUMBER(1), then DOT_DOT
                pass
            else:
                # It is a decimal point
                result += self.current_char
                self.advance()
                
                while self.current_char is not None and self.current_char.isdigit():
                    result += self.current_char
                    self.advance()
        
        # Check if it's a float or an integer
        if '.' in result:
            return Token(TokenType.NUMBER, float(result), self.line, token_column)
        else:
            return Token(TokenType.NUMBER, int(result), self.line, token_column)
    
    def _string_any(self, quote_char: str):
        """
        Parse a string delimited by the given quote character ('"' or "'").
        Supports common escapes and keeps unknown escapes verbatim.
        """
        result = ''
        token_column = self.column
        # Skip opening quote
        self.advance()
        while self.current_char is not None and self.current_char != quote_char:
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 't':
                    result += '\t'
                elif self.current_char == 'r':
                    result += '\r'
                elif self.current_char == '"':
                    result += '"'
                elif self.current_char == "'":
                    result += "'"
                elif self.current_char == '\\':
                    result += '\\'
                # Preserve backslash with common path/word characters
                elif self.current_char == '/' or (self.current_char and (self.current_char.isalnum() or self.current_char in ['_', '.'])):
                    result += '\\' + self.current_char
                else:
                    result += '\\' + (self.current_char if self.current_char is not None else '')
            else:
                result += self.current_char
            self.advance()
        # Closing quote
        if self.current_char == quote_char:
            self.advance()
        else:
            raise Exception(f'Unterminated string at line {self.line}, column {token_column}')
        return Token(TokenType.STRING, result, self.line, token_column)
    
    def identifier(self):
        """
        Parse an identifier or keyword from the source code
        """
        result = ''
        token_column = self.column
        
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        # Check if the identifier is a keyword
        token_type = KEYWORDS.get(result, TokenType.IDENTIFIER)
        return Token(token_type, result, self.line, token_column)
    
    def get_next_token(self):
        """
        Lexical analyzer (also known as scanner or tokenizer)
        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:
            # Skip whitespace
            if self.current_char.isspace() and self.current_char != '\n':
                self.skip_whitespace()
                continue
            
            # Handle newlines
            if self.current_char == '\n':
                token = Token(TokenType.NEWLINE, '\n', self.line, self.column)
                self.advance()
                return token
            
            # Handle comments vs floor division
            if self.current_char == '/' and self.peek() == '/':
                # If next next char is '=', treat as FLOOR_DIVIDE token (for '//=')
                if self.peek_n(2) == '=':
                    self.advance()  # '/'
                    self.advance()  # '/'
                    return Token(TokenType.FLOOR_DIVIDE, '//', self.line, self.column - 2)
                # Otherwise treat as comment until end of line
                self.advance()  # Skip first /
                self.advance()  # Skip second /
                self.skip_comment()
                continue
            
            # Handle identifiers and keywords
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            
            # Handle numbers
            if self.current_char.isdigit() or (self.current_char == '-' and self.peek() and self.peek().isdigit()):
                return self.number()
            
            # Handle strings: double or single quotes
            if self.current_char == '"':
                return self._string_any('"')
            if self.current_char == "'":
                return self._string_any("'")
            
            # Handle operators and delimiters
            # Logical AND '&&'
            if self.current_char == '&':
                if self.peek() == '&':
                    token_column = self.column
                    self.advance()  # first '&'
                    self.advance()  # second '&'
                    return Token(TokenType.AND, '&&', self.line, token_column)
                self.error()

            # Logical OR '||'
            if self.current_char == '|':
                if self.peek() == '|':
                    token_column = self.column
                    self.advance()  # first '|'
                    self.advance()  # second '|'
                    return Token(TokenType.OR, '||', self.line, token_column)
                self.error()
            if self.current_char == '+':
                token = Token(TokenType.PLUS, '+', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '-':
                token = Token(TokenType.MINUS, '-', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '*':
                # POWER '**'
                if self.peek() == '*':
                    token_column = self.column
                    self.advance()  # first '*'
                    self.advance()  # second '*'
                    return Token(TokenType.POWER, '**', self.line, token_column)
                token = Token(TokenType.MULTIPLY, '*', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '/':
                token = Token(TokenType.DIVIDE, '/', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '%':
                token = Token(TokenType.MODULO, '%', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '=':
                token_column = self.column
                self.advance()
                # Check if it's == or =
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUALS, '==', self.line, token_column)
                return Token(TokenType.ASSIGN, '=', self.line, token_column)
            
            if self.current_char == '!':
                token_line = self.line
                token_column = self.column
                self.advance()
                # Check if it's !=
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.NOT_EQUALS, '!=', token_line, token_column)
                return Token(TokenType.NOT, '!', token_line, token_column)
            
            if self.current_char == '<':
                token_column = self.column
                self.advance()
                # Check if it's <= or <
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.LESS_THAN_EQUALS, '<=', self.line, token_column)
                return Token(TokenType.LESS_THAN, '<', self.line, token_column)
            
            if self.current_char == '>':
                token_column = self.column
                self.advance()
                # Check if it's >= or >
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.GREATER_THAN_EQUALS, '>=', self.line, token_column)
                return Token(TokenType.GREATER_THAN, '>', self.line, token_column)
            
            if self.current_char == '(':
                token = Token(TokenType.LPAREN, '(', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == ')':
                token = Token(TokenType.RPAREN, ')', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '{':
                token = Token(TokenType.LBRACE, '{', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '}':
                token = Token(TokenType.RBRACE, '}', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '[':
                token = Token(TokenType.LBRACKET, '[', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == ']':
                token = Token(TokenType.RBRACKET, ']', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == ',':
                token = Token(TokenType.COMMA, ',', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '.':
                token_column = self.column
                self.advance()
                if self.current_char == '.':
                    self.advance()
                    return Token(TokenType.DOT_DOT, '..', self.line, token_column)
                return Token(TokenType.DOT, '.', self.line, token_column)
            
            if self.current_char == ':':
                token = Token(TokenType.COLON, ':', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '@':
                token = Token(TokenType.AT, '@', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '\\':
                token = Token(TokenType.BACKSLASH, '\\', self.line, self.column)
                self.advance()
                return token
            
            self.error()

        # End of file
        return Token(TokenType.EOF, None, self.line, self.column)
    
    def tokenize(self):
        """
        Tokenize the entire input text
        """
        tokens = []
        token = self.get_next_token()

        while token.type != TokenType.EOF:
            tokens.append(token)
            token = self.get_next_token()

        tokens.append(token)  # Add EOF token
        return tokens