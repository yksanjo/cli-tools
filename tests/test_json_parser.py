"""Tests for json_parser.py"""

import pytest

from json_parser import (
    JSONLexer,
    JSONParser,
    Token,
    TokenType,
    parse_json,
)


class TestLexer:
    def test_empty_input(self):
        lexer = JSONLexer('')
        token = lexer.next_token()
        assert token.type == TokenType.EOF

    def test_whitespace_only(self):
        lexer = JSONLexer('   \n\t  ')
        token = lexer.next_token()
        assert token.type == TokenType.EOF

    def test_simple_tokens(self):
        lexer = JSONLexer('{}[]:,')
        tokens = [lexer.next_token() for _ in range(7)]

        assert tokens[0].type == TokenType.LEFT_BRACE
        assert tokens[1].type == TokenType.RIGHT_BRACE
        assert tokens[2].type == TokenType.LEFT_BRACKET
        assert tokens[3].type == TokenType.RIGHT_BRACKET
        assert tokens[4].type == TokenType.COLON
        assert tokens[5].type == TokenType.COMMA
        assert tokens[6].type == TokenType.EOF

    def test_string_simple(self):
        lexer = JSONLexer('"hello"')
        token = lexer.next_token()
        assert token.type == TokenType.STRING
        assert token.value == 'hello'

    def test_string_with_escapes(self):
        lexer = JSONLexer(r'"hello\nworld"')
        token = lexer.next_token()
        assert token.value == 'hello\nworld'

    def test_string_unicode_escape(self):
        lexer = JSONLexer(r'"hello\u0041"')
        token = lexer.next_token()
        assert token.value == 'helloA'

    def test_number_integer(self):
        lexer = JSONLexer('42')
        token = lexer.next_token()
        assert token.type == TokenType.NUMBER
        assert token.value == 42

    def test_number_negative(self):
        lexer = JSONLexer('-17')
        token = lexer.next_token()
        assert token.value == -17

    def test_number_float(self):
        lexer = JSONLexer('3.14')
        token = lexer.next_token()
        assert token.value == 3.14

    def test_number_exponent(self):
        lexer = JSONLexer('1e10')
        token = lexer.next_token()
        assert token.value == 1e10

    def test_keywords(self):
        tests = [
            ('true', TokenType.TRUE, True),
            ('false', TokenType.FALSE, False),
            ('null', TokenType.NULL, None),
        ]
        for input_str, expected_type, expected_value in tests:
            lexer = JSONLexer(input_str)
            token = lexer.next_token()
            assert token.type == expected_type
            assert token.value == expected_value

    def test_unterminated_string(self):
        lexer = JSONLexer('"hello')
        with pytest.raises(SyntaxError):
            lexer.next_token()

    def test_invalid_escape(self):
        lexer = JSONLexer(r'"hello\x"')
        with pytest.raises(SyntaxError):
            lexer.next_token()

    def test_incomplete_unicode_escape(self):
        lexer = JSONLexer(r'"hello\u12"')
        with pytest.raises(SyntaxError):
            lexer.next_token()

    def test_invalid_number(self):
        lexer = JSONLexer('12.')
        with pytest.raises(SyntaxError):
            lexer.next_token()

    def test_unknown_character(self):
        lexer = JSONLexer('@')
        with pytest.raises(SyntaxError):
            lexer.next_token()


class TestParser:
    def test_parse_null(self):
        result = parse_json('null')
        assert result is None

    def test_parse_true(self):
        result = parse_json('true')
        assert result is True

    def test_parse_false(self):
        result = parse_json('false')
        assert result is False

    def test_parse_number(self):
        assert parse_json('42') == 42
        assert parse_json('-17') == -17
        assert parse_json('3.14') == 3.14
        assert parse_json('1e10') == 1e10

    def test_parse_string(self):
        result = parse_json('"hello world"')
        assert result == 'hello world'

    def test_parse_empty_array(self):
        result = parse_json('[]')
        assert result == []

    def test_parse_array(self):
        result = parse_json('[1, 2, 3]')
        assert result == [1, 2, 3]

    def test_parse_nested_array(self):
        result = parse_json('[[1, 2], [3, 4]]')
        assert result == [[1, 2], [3, 4]]

    def test_parse_empty_object(self):
        result = parse_json('{}')
        assert result == {}

    def test_parse_object(self):
        result = parse_json('{"key": "value"}')
        assert result == {'key': 'value'}

    def test_parse_object_multiple_keys(self):
        result = parse_json('{"a": 1, "b": 2, "c": 3}')
        assert result == {'a': 1, 'b': 2, 'c': 3}

    def test_parse_nested_object(self):
        result = parse_json('{"outer": {"inner": "value"}}')
        assert result == {'outer': {'inner': 'value'}}

    def test_parse_complex(self):
        json_str = '''
        {
            "name": "John",
            "age": 30,
            "is_student": false,
            "grades": [85, 90, 95],
            "address": {
                "city": "New York",
                "zip": "10001"
            },
            "spouse": null
        }
        '''
        result = parse_json(json_str)
        assert result['name'] == 'John'
        assert result['age'] == 30
        assert result['is_student'] is False
        assert result['grades'] == [85, 90, 95]
        assert result['address']['city'] == 'New York'
        assert result['spouse'] is None

    def test_parse_array_of_objects(self):
        result = parse_json('[{"id": 1}, {"id": 2}]')
        assert result == [{'id': 1}, {'id': 2}]

    def test_parse_trailing_content(self):
        with pytest.raises(SyntaxError):
            parse_json('42 extra')

    def test_parse_unexpected_end(self):
        with pytest.raises(SyntaxError):
            parse_json('{"key":')

    def test_parse_missing_colon(self):
        with pytest.raises(SyntaxError):
            parse_json('{"key" "value"}')

    def test_parse_missing_comma(self):
        with pytest.raises(SyntaxError):
            parse_json('[1 2 3]')


class TestRoundTrip:
    """Test that we can parse what we consider valid JSON."""

    def test_simple_values(self):
        values = [
            'null',
            'true',
            'false',
            '0',
            '-1',
            '3.14159',
            '"hello"',
            '""',
            '[]',
            '{}',
        ]
        for value in values:
            parse_json(value)

    def test_complex_structure(self):
        json_str = '''
        {
            "string": "value with \\\"quotes\\\"",
            "number": 123.456,
            "negative": -789,
            "exponent": 1.23e-4,
            "boolean": true,
            "null": null,
            "array": [1, "two", 3.0, false, null, {"nested": "object"}],
            "object": {
                "key1": "value1",
                "key2": ["nested", "array"],
                "key3": {"deeply": {"nested": "value"}}
            }
        }
        '''
        result = parse_json(json_str)
        assert result['string'] == 'value with "quotes"'
        assert result['number'] == 123.456
        assert result['negative'] == -789
        assert result['exponent'] == 1.23e-4
        assert result['boolean'] is True
        assert result['null'] is None
        assert len(result['array']) == 6
        assert result['object']['key3']['deeply']['nested'] == 'value'

    def test_unicode(self):
        result = parse_json('"Hello, 世界! 🌍"')
        assert result == 'Hello, 世界! 🌍'


class TestErrorMessages:
    def test_line_number_in_error(self):
        json_str = '{\n\n\ninvalid'
        with pytest.raises(SyntaxError) as exc_info:
            parse_json(json_str)
        # Error should mention the line number
        assert 'line' in str(exc_info.value).lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
