#!/usr/bin/env python3
"""
JSON Parser - From-Scratch Implementation

A JSON parser built from scratch to understand parsing fundamentals:
- Tokenization (lexical analysis)
- Recursive descent parsing
- Abstract syntax trees
- Error handling and recovery

This parser implements the JSON specification (RFC 8259) without using
Python's json module for the actual parsing.

Usage:
    python json_parser.py validate file.json
    python json_parser.py parse '{"key": "value"}'
    python json_parser.py pretty file.json
"""

import argparse
import re
import sys
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union


class TokenType(Enum):
    """JSON token types."""
    # Structural tokens
    LEFT_BRACE = auto()      # {
    RIGHT_BRACE = auto()     # }
    LEFT_BRACKET = auto()    # [
    RIGHT_BRACKET = auto()   # ]
    COLON = auto()           # :
    COMMA = auto()           # ,
    
    # Value tokens
    STRING = auto()
    NUMBER = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    
    # Special
    EOF = auto()
    INVALID = auto()


@dataclass
class Token:
    """Represents a single token."""
    type: TokenType
    value: Any
    line: int
    column: int
    
    def __repr__(self):
        if self.type == TokenType.STRING:
            return f"Token({self.type.name}, '{self.value[:30]}{'...' if len(str(self.value)) > 30 else ''}')"
        return f"Token({self.type.name}, {self.value})"


class JSONLexer:
    """
    Tokenizer/lexer for JSON.
    
    Converts a JSON string into a stream of tokens.
    """
    
    # Whitespace characters (ignored)
    WHITESPACE = ' \t\n\r'
    
    # Escape character mappings
    ESCAPE_CHARS = {
        '"': '"',
        '\\': '\\',
        '/': '/',
        'b': '\b',
        'f': '\f',
        'n': '\n',
        'r': '\r',
        't': '\t',
    }
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.length = len(text)
    
    def current_char(self) -> Optional[str]:
        """Get current character or None if at end."""
        if self.pos >= self.length:
            return None
        char = self.text[self.pos]
        return char if char is not None else None
    
    def advance(self) -> str:
        """Move to next character and return current."""
        char = self.current_char()
        self.pos += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def peek(self, offset: int = 0) -> Optional[str]:
        """Peek at character without advancing."""
        pos = self.pos + offset
        if pos >= self.length:
            return None
        return self.text[pos]
    
    def skip_whitespace(self):
        """Skip whitespace characters."""
        char = self.current_char()
        while char is not None and char in self.WHITESPACE:
            self.advance()
            char = self.current_char()
    
    def read_string(self) -> Token:
        """
        Read a JSON string literal.
        
        Handles escape sequences and unicode escapes.
        """
        start_line = self.line
        start_col = self.column
        
        # Skip opening quote
        self.advance()
        
        result = []
        while self.current_char() is not None and self.current_char() != '"':
            char = self.current_char()
            
            if char == '\\':
                # Handle escape sequence
                self.advance()
                escape_char = self.current_char()
                
                if escape_char in self.ESCAPE_CHARS:
                    result.append(self.ESCAPE_CHARS[escape_char])
                    self.advance()
                elif escape_char == 'u':
                    # Unicode escape \uXXXX
                    self.advance()
                    hex_digits = ''
                    for _ in range(4):
                        if self.current_char() is None:
                            raise SyntaxError(
                                f"Incomplete unicode escape at line {self.line}, column {self.column}"
                            )
                        hex_digits += self.advance()
                    try:
                        result.append(chr(int(hex_digits, 16)))
                    except ValueError:
                        raise SyntaxError(
                            f"Invalid unicode escape \\u{hex_digits} at line {self.line}, column {self.column}"
                        )
                else:
                    raise SyntaxError(
                        f"Invalid escape sequence \\{escape_char} at line {self.line}, column {self.column}"
                    )
            elif ord(char) < 0x20:
                # Control characters must be escaped
                raise SyntaxError(
                    f"Unescaped control character at line {self.line}, column {self.column}"
                )
            else:
                result.append(char)
                self.advance()
        
        if self.current_char() != '"':
            raise SyntaxError(
                f"Unterminated string starting at line {start_line}, column {start_col}"
            )
        
        # Skip closing quote
        self.advance()
        
        return Token(TokenType.STRING, ''.join(result), start_line, start_col)
    
    def read_number(self) -> Token:
        r"""
        Read a JSON number literal.
        
        JSON numbers follow: -?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?
        """
        start_line = self.line
        start_col = self.column
        
        num_str = []
        
        # Optional minus sign
        if self.current_char() == '-':
            num_str.append(self.advance())
        
        # Integer part
        if self.current_char() == '0':
            num_str.append(self.advance())
        elif self.current_char() and self.current_char().isdigit():
            while self.current_char() and self.current_char().isdigit():
                num_str.append(self.advance())
        else:
            raise SyntaxError(
                f"Invalid number at line {self.line}, column {self.column}"
            )
        
        # Fractional part
        if self.current_char() == '.':
            num_str.append(self.advance())
            if not self.current_char() or not self.current_char().isdigit():
                raise SyntaxError(
                    f"Expected digit after decimal point at line {self.line}, column {self.column}"
                )
            while self.current_char() and self.current_char().isdigit():
                num_str.append(self.advance())
        
        # Exponent part
        char = self.current_char()
        if char is not None and char in 'eE':
            num_str.append(self.advance())
            char = self.current_char()
            if char is not None and char in '+-':
                num_str.append(self.advance())
            if not self.current_char() or not self.current_char().isdigit():
                raise SyntaxError(
                    f"Expected digit in exponent at line {self.line}, column {self.column}"
                )
            while self.current_char() and self.current_char().isdigit():
                num_str.append(self.advance())
        
        # Parse the number
        num_str = ''.join(num_str)
        
        # Use int if no decimal point or exponent, else float
        if '.' in num_str or 'e' in num_str or 'E' in num_str:
            value = float(num_str)
        else:
            value = int(num_str)
        
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def read_identifier(self) -> Token:
        """Read true, false, or null literals."""
        start_line = self.line
        start_col = self.column
        
        ident = []
        while self.current_char() and self.current_char().isalpha():
            ident.append(self.advance())
        
        ident_str = ''.join(ident)
        
        if ident_str == 'true':
            return Token(TokenType.TRUE, True, start_line, start_col)
        elif ident_str == 'false':
            return Token(TokenType.FALSE, False, start_line, start_col)
        elif ident_str == 'null':
            return Token(TokenType.NULL, None, start_line, start_col)
        else:
            raise SyntaxError(
                f"Unknown identifier '{ident_str}' at line {start_line}, column {start_col}"
            )
    
    def next_token(self) -> Token:
        """Get the next token from input."""
        self.skip_whitespace()
        
        start_line = self.line
        start_col = self.column
        char = self.current_char()
        
        if char is None:
            return Token(TokenType.EOF, None, start_line, start_col)
        
        # Single-character tokens
        token_map = {
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            '[': TokenType.LEFT_BRACKET,
            ']': TokenType.RIGHT_BRACKET,
            ':': TokenType.COLON,
            ',': TokenType.COMMA,
        }
        
        if char in token_map:
            self.advance()
            return Token(token_map[char], char, start_line, start_col)
        
        # String literal
        if char == '"':
            return self.read_string()
        
        # Number literal
        if char == '-' or char.isdigit():
            return self.read_number()
        
        # Keywords (true, false, null)
        if char.isalpha():
            return self.read_identifier()
        
        # Unknown character
        raise SyntaxError(
            f"Unexpected character '{char}' at line {self.line}, column {self.column}"
        )
    
    def tokenize(self) -> List[Token]:
        """Tokenize entire input and return all tokens."""
        tokens = []
        while True:
            token = self.next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens


class JSONParser:
    """
    Recursive descent parser for JSON.
    
    Grammar:
        json        -> value
        value       -> object | array | string | number | true | false | null
        object      -> '{' [pair (',' pair)*] '}'
        pair        -> string ':' value
        array       -> '[' [value (',' value)*] ']'
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self) -> Token:
        """Get current token."""
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[self.pos]
    
    def advance(self) -> Token:
        """Move to next token and return current."""
        token = self.current_token()
        self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """Expect a specific token type, raise error if not found."""
        token = self.current_token()
        if token.type != token_type:
            raise SyntaxError(
                f"Expected {token_type.name} but got {token.type.name} "
                f"at line {token.line}, column {token.column}"
            )
        return self.advance()
    
    def parse(self) -> Any:
        """Parse JSON and return Python object."""
        result = self.parse_value()
        
        # Ensure all tokens consumed
        if self.current_token().type != TokenType.EOF:
            token = self.current_token()
            raise SyntaxError(
                f"Unexpected token {token.type.name} at line {token.line}, column {token.column}"
            )
        
        return result
    
    def parse_value(self) -> Any:
        """Parse a JSON value."""
        token = self.current_token()
        
        if token.type == TokenType.LEFT_BRACE:
            return self.parse_object()
        elif token.type == TokenType.LEFT_BRACKET:
            return self.parse_array()
        elif token.type == TokenType.STRING:
            self.advance()
            return token.value
        elif token.type == TokenType.NUMBER:
            self.advance()
            return token.value
        elif token.type == TokenType.TRUE:
            self.advance()
            return True
        elif token.type == TokenType.FALSE:
            self.advance()
            return False
        elif token.type == TokenType.NULL:
            self.advance()
            return None
        else:
            raise SyntaxError(
                f"Unexpected token {token.type.name} at line {token.line}, column {token.column}"
            )
    
    def parse_object(self) -> Dict[str, Any]:
        """Parse a JSON object."""
        self.expect(TokenType.LEFT_BRACE)  # Consume '{'
        
        obj = {}
        
        # Empty object
        if self.current_token().type == TokenType.RIGHT_BRACE:
            self.advance()
            return obj
        
        # Parse first pair
        key, value = self.parse_pair()
        obj[key] = value
        
        # Parse additional pairs
        while self.current_token().type == TokenType.COMMA:
            self.advance()  # Consume ','
            key, value = self.parse_pair()
            obj[key] = value
        
        self.expect(TokenType.RIGHT_BRACE)  # Consume '}'
        
        return obj
    
    def parse_pair(self) -> tuple:
        """Parse a key-value pair."""
        # Key must be a string
        token = self.current_token()
        if token.type != TokenType.STRING:
            raise SyntaxError(
                f"Object key must be string at line {token.line}, column {token.column}"
            )
        
        key = token.value
        self.advance()
        
        self.expect(TokenType.COLON)  # Consume ':'
        
        value = self.parse_value()
        
        return key, value
    
    def parse_array(self) -> List[Any]:
        """Parse a JSON array."""
        self.expect(TokenType.LEFT_BRACKET)  # Consume '['
        
        arr = []
        
        # Empty array
        if self.current_token().type == TokenType.RIGHT_BRACKET:
            self.advance()
            return arr
        
        # Parse first value
        arr.append(self.parse_value())
        
        # Parse additional values
        while self.current_token().type == TokenType.COMMA:
            self.advance()  # Consume ','
            arr.append(self.parse_value())
        
        self.expect(TokenType.RIGHT_BRACKET)  # Consume ']'
        
        return arr


def parse_json(text: str) -> Any:
    """Parse JSON string and return Python object."""
    lexer = JSONLexer(text)
    tokens = lexer.tokenize()
    parser = JSONParser(tokens)
    return parser.parse()


def validate_json_file(filepath: str) -> bool:
    """Validate a JSON file."""
    path = Path(filepath)
    
    if not path.exists():
        print(f"Error: File '{filepath}' not found.")
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = parse_json(content)
        
        print(f"✓ Valid JSON: {filepath}")
        
        # Print summary
        def analyze(obj, depth=0):
            if isinstance(obj, dict):
                print(f"{'  ' * depth}Object with {len(obj)} key(s)")
                for k, v in obj.items():
                    print(f"{'  ' * depth}  \"{k}\":")
                    analyze(v, depth + 2)
            elif isinstance(obj, list):
                print(f"{'  ' * depth}Array with {len(obj)} element(s)")
                if obj:
                    print(f"{'  ' * depth}  [0]:")
                    analyze(obj[0], depth + 2)
            elif isinstance(obj, str):
                preview = obj[:50] + '...' if len(obj) > 50 else obj
                print(f"{'  ' * depth}String: \"{preview}\"")
            elif isinstance(obj, (int, float)):
                print(f"{'  ' * depth}Number: {obj}")
            elif isinstance(obj, bool):
                print(f"{'  ' * depth}Boolean: {obj}")
            elif obj is None:
                print(f"{'  ' * depth}null")
        
        print("\nStructure:")
        analyze(result)
        
        return True
        
    except SyntaxError as e:
        print(f"✗ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def parse_json_string(json_str: str) -> bool:
    """Parse and display a JSON string."""
    try:
        result = parse_json(json_str)
        print("Parsed successfully!")
        print(f"Type: {type(result).__name__}")
        print(f"Value: {result}")
        return True
    except SyntaxError as e:
        print(f"Parse error: {e}")
        return False


def pretty_print_json(filepath: str) -> bool:
    """Pretty-print a JSON file."""
    path = Path(filepath)
    
    if not path.exists():
        print(f"Error: File '{filepath}' not found.")
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = parse_json(content)
        
        def stringify(obj, indent=0, current_indent=0) -> str:
            spaces = '  '
            prefix = spaces * current_indent
            
            if isinstance(obj, dict):
                if not obj:
                    return '{}'
                
                items = []
                for k, v in obj.items():
                    value_str = stringify(v, indent, current_indent + 1)
                    items.append(f'{prefix}{spaces}"{escape_string(k)}": {value_str}')
                
                return '{\n' + ',\n'.join(items) + '\n' + prefix + '}'
            
            elif isinstance(obj, list):
                if not obj:
                    return '[]'
                
                items = []
                for item in obj:
                    items.append(stringify(item, indent, current_indent + 1))
                
                if all(isinstance(x, (str, int, float, bool)) or x is None for x in obj):
                    # Simple array on one line
                    return '[ ' + ', '.join(items) + ' ]'
                
                return '[\n' + ',\n'.join(f'{prefix}{spaces}{item}' for item in items) + '\n' + prefix + ']'
            
            elif isinstance(obj, str):
                return f'"{escape_string(obj)}"'
            
            elif isinstance(obj, bool):
                return 'true' if obj else 'false'
            
            elif obj is None:
                return 'null'
            
            else:
                return str(obj)
        
        print(stringify(result))
        return True
        
    except SyntaxError as e:
        print(f"Parse error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def escape_string(s: str) -> str:
    """Escape special characters in a string for JSON output."""
    escapes = {
        '"': '\\"',
        '\\': '\\\\',
        '\b': '\\b',
        '\f': '\\f',
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
    }
    
    result = []
    for char in s:
        if char in escapes:
            result.append(escapes[char])
        elif ord(char) < 0x20:
            result.append(f'\\u{ord(char):04x}')
        else:
            result.append(char)
    
    return ''.join(result)


def tokenize_json(json_str: str) -> bool:
    """Show the tokens in a JSON string."""
    try:
        lexer = JSONLexer(json_str)
        tokens = lexer.tokenize()
        
        print("Tokens:")
        for token in tokens:
            print(f"  {token}")
        
        return True
    except SyntaxError as e:
        print(f"Tokenization error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="JSON Parser - From-Scratch Implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python json_parser.py validate config.json
  python json_parser.py parse '{"name": "John", "age": 30}'
  python json_parser.py pretty data.json
  python json_parser.py tokenize '{"key": "value"}'
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a JSON file')
    validate_parser.add_argument('file', help='JSON file to validate')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse a JSON string')
    parse_parser.add_argument('json', help='JSON string to parse')
    
    # Pretty print command
    pretty_parser = subparsers.add_parser('pretty', help='Pretty-print a JSON file')
    pretty_parser.add_argument('file', help='JSON file to format')
    
    # Tokenize command
    tokenize_parser = subparsers.add_parser('tokenize', help='Show tokens in JSON')
    tokenize_parser.add_argument('json', help='JSON string to tokenize')
    
    args = parser.parse_args()
    
    success = False
    
    if args.command == 'validate':
        success = validate_json_file(args.file)
    elif args.command == 'parse':
        success = parse_json_string(args.json)
    elif args.command == 'pretty':
        success = pretty_print_json(args.file)
    elif args.command == 'tokenize':
        success = tokenize_json(args.json)
    else:
        parser.print_help()
        return
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
