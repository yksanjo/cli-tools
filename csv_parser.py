#!/usr/bin/env python3
"""
RFC 4180 Compliant CSV Parser

A from-scratch CSV parser that implements the RFC 4180 standard.
Educational demonstration of:
- State machine parsing
- Handling quoted fields
- Escaping rules
- Streaming large files

Usage:
    python csv_parser.py parse data.csv
    python csv_parser.py validate data.csv
    python csv_parser.py convert data.csv output.json
"""

import argparse
import json
import sys
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Iterator, List, Optional, TextIO, Union


class CSVError(Exception):
    """Custom exception for CSV parsing errors."""
    pass


class ParseState(Enum):
    """States for the CSV state machine parser."""
    START = auto()
    IN_FIELD = auto()
    IN_QUOTED_FIELD = auto()
    ESCAPE_IN_QUOTED = auto()
    END_OF_LINE = auto()


@dataclass
class CSVOptions:
    """Options for CSV parsing."""
    delimiter: str = ","
    quotechar: str = '"'
    doublequote: bool = True
    skip_initial_space: bool = False
    lineterminator: str = "\r\n"
    quoting: int = 0  # 0 = minimal, 1 = all, 2 = non-numeric, 3 = none


class CSVParser:
    """
    RFC 4180 compliant CSV parser using state machine.
    
    Handles:
    - Fields containing commas, newlines, quotes
    - Quoted fields with escaped quotes ("")
    - Mixed quoted and unquoted fields
    - Empty fields
    """

    def __init__(self, options: Optional[CSVOptions] = None):
        self.options = options or CSVOptions()

    def parse(self, text: str) -> List[List[str]]:
        """Parse CSV text into list of rows."""
        return list(self.parse_iter(text))

    def parse_iter(self, text: str) -> Iterator[List[str]]:
        """Parse CSV text yielding rows as they're completed."""
        state = ParseState.START
        current_field = []
        current_row = []
        i = 0

        while i < len(text):
            char = text[i]

            if state == ParseState.START:
                if char == self.options.quotechar:
                    state = ParseState.IN_QUOTED_FIELD
                    i += 1
                elif char == self.options.delimiter:
                    # Empty field
                    current_row.append("")
                    i += 1
                elif char in '\r\n':
                    # End of row
                    if current_row or current_field:
                        current_row.append("".join(current_field))
                        yield current_row
                        current_row = []
                        current_field = []
                    # Skip newline after carriage return
                    if char == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                        i += 1
                    i += 1
                    state = ParseState.START
                else:
                    state = ParseState.IN_FIELD

            elif state == ParseState.IN_FIELD:
                if char == self.options.delimiter:
                    current_row.append("".join(current_field))
                    current_field = []
                    state = ParseState.START
                    i += 1
                elif char in '\r\n':
                    current_row.append("".join(current_field))
                    yield current_row
                    current_row = []
                    current_field = []
                    if char == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                        i += 1
                    i += 1
                    state = ParseState.START
                else:
                    current_field.append(char)
                    i += 1

            elif state == ParseState.IN_QUOTED_FIELD:
                if char == self.options.quotechar:
                    # Check if it's an escaped quote ("") or end of field
                    if self.options.doublequote and i + 1 < len(text) and text[i + 1] == self.options.quotechar:
                        current_field.append(self.options.quotechar)
                        i += 2
                    else:
                        state = ParseState.END_OF_LINE
                        i += 1
                else:
                    current_field.append(char)
                    i += 1

            elif state == ParseState.END_OF_LINE:
                if char == self.options.delimiter:
                    current_row.append("".join(current_field))
                    current_field = []
                    state = ParseState.START
                    i += 1
                elif char in '\r\n':
                    current_row.append("".join(current_field))
                    yield current_row
                    current_row = []
                    current_field = []
                    if char == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                        i += 1
                    i += 1
                    state = ParseState.START
                else:
                    raise CSVError(
                        f"Expected delimiter or newline after quoted field, "
                        f"got '{char}' at position {i}"
                    )

        # Handle end of input
        if state == ParseState.IN_QUOTED_FIELD:
            raise CSVError("Unterminated quoted field at end of input")

        if current_field or current_row or state == ParseState.IN_FIELD:
            current_row.append("".join(current_field))
            yield current_row

    def parse_file(self, filepath: Union[str, Path]) -> Iterator[List[str]]:
        """Parse CSV file yielding rows."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(path, 'r', encoding='utf-8', newline='') as f:
            content = f.read()
            yield from self.parse_iter(content)


def sniff_dialect(filepath: str) -> CSVOptions:
    """
    Attempt to detect CSV dialect by analyzing the file.
    
    Returns CSVOptions with detected settings.
    """
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        sample = f.read(8192)  # Read first 8KB

    # Count occurrences of common delimiters
    delimiters = {',': 0, ';': 0, '\t': 0, '|': 0}
    for char in sample:
        if char in delimiters:
            delimiters[char] += 1

    # Most common delimiter wins
    delimiter = max(delimiters, key=delimiters.get)
    if delimiters[delimiter] == 0:
        delimiter = ','  # Default

    return CSVOptions(delimiter=delimiter)


def validate_csv(filepath: str, options: Optional[CSVOptions] = None) -> bool:
    """Validate a CSV file."""
    try:
        parser = CSVParser(options)
        row_count = 0
        col_count = None

        for row in parser.parse_file(filepath):
            row_count += 1
            if col_count is None:
                col_count = len(row)
            elif len(row) != col_count:
                print(f"✗ Row {row_count}: Expected {col_count} columns, got {len(row)}")
                return False

        print(f"✓ Valid CSV: {filepath}")
        print(f"  Rows: {row_count}")
        print(f"  Columns: {col_count}")
        return True

    except CSVError as e:
        print(f"✗ Invalid CSV: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def parse_csv(filepath: str, options: Optional[CSVOptions] = None) -> List[List[str]]:
    """Parse CSV file and return all rows."""
    parser = CSVParser(options)
    return list(parser.parse_file(filepath))


def convert_to_json(
    input_path: str,
    output_path: str,
    has_header: bool = True,
    options: Optional[CSVOptions] = None
) -> bool:
    """Convert CSV to JSON."""
    try:
        rows = parse_csv(input_path, options)

        if not rows:
            print("No data to convert")
            return False

        if has_header:
            headers = rows[0]
            data = [
                {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
                for row in rows[1:]
            ]
        else:
            data = rows

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Converted {len(rows)} rows to {output_path}")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="RFC 4180 Compliant CSV Parser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python csv_parser.py parse data.csv
  python csv_parser.py validate data.csv
  python csv_parser.py convert data.csv output.json
  python csv_parser.py sniff data.csv
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse and display CSV')
    parse_parser.add_argument('file', help='CSV file to parse')
    parse_parser.add_argument('-d', '--delimiter', help='Field delimiter')
    parse_parser.add_argument('-n', '--limit', type=int, help='Limit number of rows')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate CSV file')
    validate_parser.add_argument('file', help='CSV file to validate')
    validate_parser.add_argument('-d', '--delimiter', help='Field delimiter')

    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert CSV to JSON')
    convert_parser.add_argument('input', help='Input CSV file')
    convert_parser.add_argument('output', help='Output JSON file')
    convert_parser.add_argument('-H', '--no-header', action='store_true',
                                help='No header row')
    convert_parser.add_argument('-d', '--delimiter', help='Field delimiter')

    # Sniff command
    sniff_parser = subparsers.add_parser('sniff', help='Detect CSV dialect')
    sniff_parser.add_argument('file', help='CSV file to analyze')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    # Build options
    options = CSVOptions()
    if hasattr(args, 'delimiter') and args.delimiter:
        options.delimiter = args.delimiter

    if args.command == 'parse':
        try:
            rows = parse_csv(args.file, options)
            limit = args.limit or len(rows)
            for i, row in enumerate(rows[:limit], 1):
                print(f"Row {i}: {row}")
            if len(rows) > limit:
                print(f"... ({len(rows) - limit} more rows)")
        except Exception as e:
            print(f"Error: {e}")

    elif args.command == 'validate':
        success = validate_csv(args.file, options)
        sys.exit(0 if success else 1)

    elif args.command == 'convert':
        success = convert_to_json(
            args.input,
            args.output,
            has_header=not args.no_header,
            options=options
        )
        sys.exit(0 if success else 1)

    elif args.command == 'sniff':
        try:
            detected = sniff_dialect(args.file)
            print(f"Detected CSV dialect for {args.file}:")
            print(f"  Delimiter: '{detected.delimiter}'")
            print(f"  Quote char: '{detected.quotechar}'")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
