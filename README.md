# CLI Tools Collection

[![CI](https://github.com/yksanjo/cli-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/yksanjo/cli-tools/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A collection of computationally interesting CLI tools built from scratch in Python. Each tool demonstrates fundamental computer science concepts and algorithms.

**[Features](#tools-included) • [Installation](#installation) • [Usage](#usage) • [Development](#development)**

## Tools Included

### 🗜️ File Compressor

A lossless file compression tool using **Huffman Coding**.

**Concepts:** Greedy algorithms, binary trees, min-heaps, bit manipulation

```bash
python file_compressor.py compress input.txt output.huff
python file_compressor.py decompress output.huff restored.txt
python file_compressor.py analyze input.txt
```

**Features:**
- Huffman tree construction using min-heaps
- Variable-length prefix codes
- Bit-packing for efficient storage
- Frequency analysis and entropy calculation

---

### 🔍 Grep Clone

A pattern-matching file search tool similar to Unix `grep`.

**Concepts:** Regular expressions, file I/O, generators/iterators

```bash
python grep_clone.py "def " *.py
python grep_clone.py -r "TODO" .
python grep_clone.py -i -n "error" log.txt
python grep_clone.py -C 2 "pattern" file.txt
```

**Features:**
- Regex and literal string matching
- Recursive directory search
- Context lines (before/after matches)
- Case-insensitive matching
- Invert match mode
- Colorized output
- Word-boundary matching

---

### 📄 JSON Parser

A complete JSON parser built from scratch (no `json` module usage).

**Concepts:** Tokenization, recursive descent parsing, abstract syntax trees

```bash
python json_parser.py validate config.json
python json_parser.py parse '{"key": "value"}'
python json_parser.py pretty data.json
python json_parser.py tokenize '[1, "hello", null]'
```

**Features:**
- Complete tokenizer/lexer
- Recursive descent parser
- Handles all JSON types: objects, arrays, strings, numbers, booleans, null
- Unicode escape sequence support
- Pretty-printing with proper indentation
- Detailed error messages with line/column info

---

### 📊 CSV Parser

An RFC 4180 compliant CSV parser using state machines.

**Concepts:** State machines, streaming parsers, dialect detection

```bash
python csv_parser.py parse data.csv
python csv_parser.py validate data.csv
python csv_parser.py convert data.csv output.json
python csv_parser.py sniff data.csv
```

**Features:**
- RFC 4180 compliant parsing
- State machine implementation
- Handles quoted fields with commas and newlines
- Escaped quote handling ("")
- Automatic dialect detection
- CSV to JSON conversion

---

### 🎯 Habit Tracker

A gamified habit tracker with streaks, heatmaps, reminders, and achievements.

**Concepts:** Data persistence, date calculations, gamification systems

```bash
python habit_tracker.py add "Exercise" --color green --target 30
python habit_tracker.py done "Exercise"
python habit_tracker.py list
python habit_tracker.py stats
python habit_tracker.py achievements
python habit_tracker.py export
```

**Features:**
- 🔥 Streak counters (current and longest)
- 📊 ASCII heatmap visualizations
- ⏰ Daily reminder system
- 📁 CSV export for data portability
- 🎮 XP and leveling system
- 🏆 8 unlockable achievements
- 🎨 Color-coded habits

## Installation

### From PyPI (coming soon)

```bash
pip install cli-tools
```

### From Source

```bash
# Clone the repository
git clone https://github.com/yksanjo/cli-tools.git
cd cli-tools

# Install in editable mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Usage

After installation, the tools are available as command-line scripts:

```bash
# File compression
huffman-compress compress input.txt output.huff
huffman-compress decompress output.huff restored.txt

# Grep clone
grep-clone "def " *.py
grep-clone -r "TODO" .

# JSON parser
json-parser validate config.json
json-parser parse '{"key": "value"}'
```

Or run directly with Python:

```bash
python file_compressor.py compress input.txt output.huff
python grep_clone.py -n "def " *.py
python json_parser.py validate config.json
```

## Educational Value

These tools are designed to teach fundamental CS concepts:

| Tool | Algorithm/Data Structure | Complexity |
|------|-------------------------|------------|
| File Compressor | Huffman coding, min-heap | O(n log n) |
| Grep Clone | Regex matching, iterators | O(n × m) |
| JSON Parser | Recursive descent, tokenization | O(n) |
| CSV Parser | State machine | O(n) |
| Habit Tracker | Date calculations, persistence | O(n) |

## Development

### Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Or use the Makefile
make install-dev
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Or use Make
make test
make test-cov
```

### Code Quality

```bash
# Run all checks
make check-all

# Individual checks
make lint          # ruff
make format-check  # black
make type-check    # mypy
make format        # auto-format with black
```

### CI/CD

This project uses GitHub Actions for continuous integration. The pipeline runs:
- Linting with `ruff`
- Format checking with `black`
- Type checking with `mypy`
- Tests with `pytest` across Python 3.8-3.12
- Package building

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests and linting (`make check-all`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

These tools were built for educational purposes to demonstrate fundamental computer science concepts. They are not intended to replace production-grade tools but rather to serve as learning resources.

---

⭐ **Star this repo if you found it helpful!**
