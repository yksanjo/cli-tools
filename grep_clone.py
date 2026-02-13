#!/usr/bin/env python3
"""
Grep Clone - Pattern Matching File Search Tool

A simplified grep implementation that demonstrates:
- Regular expression pattern matching
- File I/O and directory traversal
- Text processing algorithms
- Line-based searching with context

Usage:
    python grep_clone.py pattern file.txt
    python grep_clone.py -r pattern /path/to/dir
    python grep_clone.py -i -n pattern *.py
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Iterator, List, NamedTuple, Optional, Pattern, Tuple


class MatchResult(NamedTuple):
    """Represents a single match in a file."""
    filename: str
    line_num: int
    line: str
    matches: List[Tuple[int, int]]  # Start/end positions of matches


def compile_pattern(
    pattern: str,
    ignore_case: bool = False,
    whole_word: bool = False,
    fixed_strings: bool = False
) -> Pattern:
    """
    Compile the search pattern into a regex pattern.
    
    Args:
        pattern: The search pattern
        ignore_case: Case-insensitive matching
        whole_word: Match whole words only
        fixed_strings: Treat pattern as literal string (no regex)
    """
    if fixed_strings:
        # Escape regex special characters for literal matching
        pattern = re.escape(pattern)
    
    if whole_word:
        # Add word boundaries
        pattern = r'\b' + pattern + r'\b'
    
    flags = re.IGNORECASE if ignore_case else 0
    
    try:
        return re.compile(pattern, flags)
    except re.error as e:
        print(f"Invalid pattern: {e}", file=sys.stderr)
        sys.exit(1)


def find_matches_in_line(
    line: str,
    pattern: Pattern,
    invert_match: bool = False
) -> Optional[List[Tuple[int, int]]]:
    """
    Find all matches of pattern in a line.
    
    Returns:
        List of (start, end) tuples if matches found, None otherwise.
        If invert_match is True, returns empty list for non-matching lines.
    """
    matches = [(m.start(), m.end()) for m in pattern.finditer(line)]
    
    if invert_match:
        # Return empty list (indicating "match") if no real matches
        return [] if not matches else None
    
    return matches if matches else None


def search_file(
    filepath: Path,
    pattern: Pattern,
    invert_match: bool = False,
    max_count: Optional[int] = None
) -> Iterator[MatchResult]:
    """
    Search a single file for pattern matches.
    
    Yields MatchResult objects for each matching line.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            count = 0
            for line_num, line in enumerate(f, 1):
                if max_count is not None and count >= max_count:
                    break
                
                # Remove trailing newline for cleaner output
                display_line = line.rstrip('\n\r')
                
                matches = find_matches_in_line(display_line, pattern, invert_match)
                
                if matches is not None:
                    count += 1
                    yield MatchResult(
                        filename=str(filepath),
                        line_num=line_num,
                        line=display_line,
                        matches=matches
                    )
    except (IOError, OSError) as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)


def get_context_lines(
    filepath: Path,
    match_line: int,
    before: int,
    after: int
) -> Tuple[List[str], List[str]]:
    """
    Get context lines before and after a match.
    
    Returns:
        Tuple of (before_lines, after_lines)
    """
    before_lines = []
    after_lines = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Get before context
        start = max(0, match_line - before - 1)
        for i in range(start, match_line - 1):
            before_lines.append((i + 1, lines[i].rstrip('\n\r')))
        
        # Get after context
        end = min(len(lines), match_line + after)
        for i in range(match_line, end):
            after_lines.append((i + 1, lines[i].rstrip('\n\r')))
            
    except (IOError, OSError):
        pass
    
    return before_lines, after_lines


def highlight_matches(line: str, matches: List[Tuple[int, int]], color: bool = True) -> str:
    """
    Highlight matched portions of a line.
    
    Uses ANSI color codes if color=True.
    """
    if not color or not matches:
        return line
    
    # ANSI color codes
    RED = '\033[91m'
    RESET = '\033[0m'
    
    # Build highlighted string from right to left to preserve indices
    result = line
    for start, end in reversed(matches):
        result = result[:start] + RED + result[start:end] + RESET + result[end:]
    
    return result


def format_output(
    result: MatchResult,
    show_filename: bool,
    show_line_num: bool,
    color: bool,
    before_context: List[Tuple[int, str]] = None,
    after_context: List[Tuple[int, str]] = None
) -> str:
    """Format a match result for output."""
    lines = []
    
    # Before context
    if before_context:
        for ctx_line_num, ctx_line in before_context:
            prefix = f"{ctx_line_num}-" if show_line_num else ""
            lines.append(f"{' ' * len(result.filename)}{'--' if show_filename else ''}{prefix}{ctx_line}")
    
    # Main match line
    prefix_parts = []
    if show_filename:
        prefix_parts.append(result.filename)
    if show_line_num:
        prefix_parts.append(str(result.line_num))
    
    prefix = ':'.join(prefix_parts) + ':' if prefix_parts else ''
    highlighted = highlight_matches(result.line, result.matches, color)
    lines.append(f"{prefix}{highlighted}")
    
    # After context
    if after_context:
        for ctx_line_num, ctx_line in after_context:
            prefix = f"{ctx_line_num}-" if show_line_num else ""
            lines.append(f"{' ' * len(result.filename)}{'--' if show_filename else ''}{prefix}{ctx_line}")
    
    return '\n'.join(lines)


def collect_files(paths: List[str], recursive: bool = False) -> Iterator[Path]:
    """
    Collect all files from given paths.
    
    Expands directories if recursive=True.
    """
    for path_str in paths:
        path = Path(path_str)
        
        if path.is_file():
            yield path
        elif path.is_dir():
            if recursive:
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        yield file_path
            else:
                print(f"{path}: Is a directory (use -r for recursive)", file=sys.stderr)
        else:
            # Try glob expansion for patterns like *.py
            import glob
            matches = glob.glob(path_str)
            if matches:
                for match in matches:
                    match_path = Path(match)
                    if match_path.is_file():
                        yield match_path
            else:
                print(f"{path}: No such file or directory", file=sys.stderr)


def search(
    paths: List[str],
    pattern: Pattern,
    recursive: bool = False,
    show_filename: bool = None,
    show_line_num: bool = True,
    invert_match: bool = False,
    max_count: Optional[int] = None,
    before_context: int = 0,
    after_context: int = 0,
    only_filenames: bool = False,
    count_only: bool = False,
    color: bool = True
) -> int:
    """
    Main search function.
    
    Returns:
        Number of matches found (exit code: 0 if matches, 1 if no matches)
    """
    files = list(collect_files(paths, recursive))
    
    # Auto-enable filename display if multiple files
    if show_filename is None:
        show_filename = len(files) > 1
    
    total_matches = 0
    file_counts = {}
    
    for filepath in files:
        file_matches = list(search_file(filepath, pattern, invert_match, max_count))
        
        if file_matches:
            total_matches += len(file_matches)
            file_counts[filepath] = len(file_matches)
            
            if only_filenames:
                print(filepath)
            elif count_only:
                pass  # Count collected above
            else:
                for result in file_matches:
                    # Get context if requested
                    before_ctx = None
                    after_ctx = None
                    
                    if before_context > 0 or after_context > 0:
                        before_ctx, after_ctx = get_context_lines(
                            filepath, result.line_num, before_context, after_context
                        )
                    
                    output = format_output(
                        result, show_filename, show_line_num, color,
                        before_ctx, after_ctx
                    )
                    print(output)
    
    if count_only:
        if len(files) == 1:
            print(total_matches)
        else:
            for filepath in files:
                count = file_counts.get(filepath, 0)
                print(f"{filepath}:{count}")
    
    return 0 if total_matches > 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="Grep Clone - Pattern Matching File Search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python grep_clone.py "def " *.py           # Search Python files
  python grep_clone.py -r "TODO" .           # Recursive search for TODO
  python grep_clone.py -i -n "error" log.txt # Case-insensitive with line numbers
  python grep_clone.py -c "pattern" file.txt # Count matches only
  python grep_clone.py -l "import" *.py      # List files with matches
  python grep_clone.py -v "test" file.py     # Invert match (lines without pattern)
        """
    )
    
    parser.add_argument('pattern', help='Search pattern (regex by default)')
    parser.add_argument('files', nargs='+', help='Files or directories to search')
    
    # Matching options
    parser.add_argument('-i', '--ignore-case', action='store_true',
                        help='Case-insensitive matching')
    parser.add_argument('-v', '--invert-match', action='store_true',
                        help='Select non-matching lines')
    parser.add_argument('-w', '--word-regexp', action='store_true',
                        help='Match whole words only')
    parser.add_argument('-F', '--fixed-strings', action='store_true',
                        help='Treat pattern as literal string')
    
    # Output options
    parser.add_argument('-n', '--line-number', action='store_true', default=True,
                        help='Show line numbers (default: on)')
    parser.add_argument('-N', '--no-line-number', action='store_true',
                        help='Hide line numbers')
    parser.add_argument('-H', '--with-filename', action='store_true', default=None,
                        help='Show filenames')
    parser.add_argument('--no-filename', action='store_true',
                        help='Hide filenames')
    parser.add_argument('--color', '--colour', choices=['always', 'never', 'auto'],
                        default='auto', help='Colorize output')
    
    # Context options
    parser.add_argument('-B', '--before-context', type=int, metavar='NUM', default=0,
                        help='Show NUM lines before each match')
    parser.add_argument('-A', '--after-context', type=int, metavar='NUM', default=0,
                        help='Show NUM lines after each match')
    parser.add_argument('-C', '--context', type=int, metavar='NUM', default=0,
                        help='Show NUM lines before and after each match')
    
    # Control options
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Recursively search directories')
    parser.add_argument('-l', '--files-with-matches', action='store_true',
                        help='List only filenames with matches')
    parser.add_argument('-c', '--count', action='store_true',
                        help='Count matches per file')
    parser.add_argument('-m', '--max-count', type=int, metavar='NUM',
                        help='Stop after NUM matches per file')
    
    args = parser.parse_args()
    
    # Handle --context shorthand
    if args.context > 0:
        args.before_context = args.context
        args.after_context = args.context
    
    # Handle no-line-number and no-filename
    show_line_num = not args.no_line_number
    show_filename = False if args.no_filename else (args.with_filename or None)
    
    # Handle color
    use_color = args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty())
    
    # Compile pattern
    pattern = compile_pattern(
        args.pattern,
        ignore_case=args.ignore_case,
        whole_word=args.word_regexp,
        fixed_strings=args.fixed_strings
    )
    
    # Run search
    exit_code = search(
        paths=args.files,
        pattern=pattern,
        recursive=args.recursive,
        show_filename=show_filename,
        show_line_num=show_line_num,
        invert_match=args.invert_match,
        max_count=args.max_count,
        before_context=args.before_context,
        after_context=args.after_context,
        only_filenames=args.files_with_matches,
        count_only=args.count,
        color=use_color
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
