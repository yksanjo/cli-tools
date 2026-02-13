# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-02-13

### Added
- Initial release with three CLI tools:
  - **file_compressor.py**: Huffman coding compression tool
  - **grep_clone.py**: Pattern matching file search
  - **json_parser.py**: From-scratch JSON parser
  - **csv_parser.py**: RFC 4180 compliant CSV parser
- Comprehensive test suite with pytest (87 tests)
- GitHub Actions CI/CD pipeline for Python 3.8-3.12
- pyproject.toml with package metadata and entry points
- Makefile for common development tasks
- MIT License
- Example files for testing

### Features

#### File Compressor
- Huffman tree construction using min-heaps
- Variable-length prefix codes
- Bit-packing for efficient storage
- Frequency analysis and entropy calculation

#### Grep Clone
- Regex and literal string matching
- Recursive directory search
- Context lines (before/after matches)
- Case-insensitive matching
- Invert match mode
- Colorized output
- Word-boundary matching

#### JSON Parser
- Complete tokenizer/lexer
- Recursive descent parser
- Handles all JSON types: objects, arrays, strings, numbers, booleans, null
- Unicode escape sequence support
- Pretty-printing with proper indentation
- Detailed error messages with line/column info

#### CSV Parser
- RFC 4180 compliant parsing
- State machine implementation
- Quoted field handling
- Automatic dialect detection
- CSV to JSON conversion

[0.1.0]: https://github.com/yksanjo/cli-tools/releases/tag/v0.1.0
