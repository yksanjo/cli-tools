"""Tests for grep_clone.py"""

import re
import tempfile
from pathlib import Path

import pytest

from grep_clone import (
    MatchResult,
    collect_files,
    compile_pattern,
    find_matches_in_line,
    format_output,
    highlight_matches,
    search_file,
)


class TestPatternCompilation:
    def test_simple_pattern(self):
        pattern = compile_pattern('hello')
        assert pattern.search('hello world')
        assert not pattern.search('goodbye')

    def test_ignore_case(self):
        pattern = compile_pattern('HELLO', ignore_case=True)
        assert pattern.search('hello world')
        assert pattern.search('HELLO world')

    def test_whole_word(self):
        pattern = compile_pattern('test', whole_word=True)
        assert pattern.search('this is a test')
        assert not pattern.search('this is testing')

    def test_fixed_strings(self):
        pattern = compile_pattern('a+b', fixed_strings=True)
        assert pattern.search('a+b equals')
        assert not pattern.search('aaab equals')

    def test_invalid_pattern(self):
        with pytest.raises(SystemExit):
            compile_pattern('[invalid')


class TestFindMatches:
    def test_simple_match(self):
        pattern = compile_pattern('test')
        matches = find_matches_in_line('this is a test', pattern)
        assert matches == [(10, 14)]

    def test_multiple_matches(self):
        pattern = compile_pattern('a')
        matches = find_matches_in_line('banana', pattern)
        assert matches == [(1, 2), (3, 4), (5, 6)]

    def test_no_match(self):
        pattern = compile_pattern('xyz')
        matches = find_matches_in_line('hello world', pattern)
        assert matches is None

    def test_invert_match(self):
        pattern = compile_pattern('test')
        matches = find_matches_in_line('hello world', pattern, invert_match=True)
        assert matches == []

    def test_invert_match_with_match(self):
        pattern = compile_pattern('test')
        matches = find_matches_in_line('this is a test', pattern, invert_match=True)
        assert matches is None


class TestSearchFile:
    def test_basic_search(self, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('line one\nline two\nline three\n')

        pattern = compile_pattern('two')
        results = list(search_file(test_file, pattern))

        assert len(results) == 1
        assert results[0].line_num == 2
        assert 'two' in results[0].line

    def test_multiple_matches(self, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('apple\nbanana\napple pie\n')

        pattern = compile_pattern('apple')
        results = list(search_file(test_file, pattern))

        assert len(results) == 2
        assert results[0].line_num == 1
        assert results[1].line_num == 3

    def test_no_matches(self, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('hello world\ngoodbye\n')

        pattern = compile_pattern('xyz')
        results = list(search_file(test_file, pattern))

        assert len(results) == 0

    def test_max_count(self, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('test\ntest\ntest\ntest\n')

        pattern = compile_pattern('test')
        results = list(search_file(test_file, pattern, max_count=2))

        assert len(results) == 2


class TestHighlightMatches:
    def test_highlight(self):
        line = 'hello world'
        matches = [(6, 11)]
        result = highlight_matches(line, matches, color=True)
        assert '\033[91m' in result
        assert 'world' in result

    def test_no_color(self):
        line = 'hello world'
        matches = [(6, 11)]
        result = highlight_matches(line, matches, color=False)
        assert result == 'hello world'

    def test_empty_matches(self):
        line = 'hello world'
        result = highlight_matches(line, [], color=True)
        assert result == 'hello world'


class TestFormatOutput:
    def test_basic_format(self):
        result = MatchResult('file.txt', 10, 'hello world', [(6, 11)])
        output = format_output(result, show_filename=True, show_line_num=True, color=False)
        assert 'file.txt' in output
        assert '10' in output
        assert 'hello world' in output

    def test_no_filename(self):
        result = MatchResult('file.txt', 10, 'hello world', [(6, 11)])
        output = format_output(result, show_filename=False, show_line_num=True, color=False)
        assert 'file.txt' not in output
        assert '10' in output

    def test_no_line_number(self):
        result = MatchResult('file.txt', 10, 'hello world', [(6, 11)])
        output = format_output(result, show_filename=True, show_line_num=False, color=False)
        assert 'file.txt' in output
        assert ':10:' not in output


class TestCollectFiles:
    def test_single_file(self, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')

        files = list(collect_files([str(test_file)]))
        assert len(files) == 1
        assert files[0] == test_file

    def test_nonexistent_file(self, tmp_path, capsys):
        nonexistent = tmp_path / 'nonexistent.txt'
        files = list(collect_files([str(nonexistent)]))
        assert len(files) == 0

    def test_glob_pattern(self, tmp_path):
        (tmp_path / 'a.py').write_text('')
        (tmp_path / 'b.py').write_text('')
        (tmp_path / 'c.txt').write_text('')

        files = list(collect_files([str(tmp_path / '*.py')]))
        assert len(files) == 2


class TestIntegration:
    def test_search_python_functions(self, tmp_path):
        """Test searching for 'def ' in Python files."""
        py_file = tmp_path / 'test.py'
        py_file.write_text('def hello():\n    pass\n\ndef world():\n    pass\n')

        pattern = compile_pattern(r'def ')
        results = list(search_file(py_file, pattern))

        assert len(results) == 2
        assert all('def ' in r.line for r in results)

    def test_case_insensitive_search(self, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('ERROR\nerror\nError\n')

        pattern = compile_pattern('error', ignore_case=True)
        results = list(search_file(test_file, pattern))

        assert len(results) == 3

    def test_regex_search(self, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('foo123\nbar456\nbaz789\n')

        pattern = compile_pattern(r'\d+')
        results = list(search_file(test_file, pattern))

        assert len(results) == 3
        assert results[0].matches == [(3, 6)]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
