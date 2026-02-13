# CLI Tools Collection

A collection of computationally interesting CLI tools built from scratch in Python. Each tool demonstrates fundamental computer science concepts and algorithms.

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

## Requirements

- Python 3.7+
- No external dependencies (stdlib only)

## Installation

```bash
# Clone the repository
git clone https://github.com/yksanjo/cli-tools.git
cd cli-tools

# Make executable (optional)
chmod +x *.py
```

## Educational Value

These tools are designed to teach fundamental CS concepts:

| Tool | Algorithm/Data Structure | Complexity |
|------|-------------------------|------------|
| File Compressor | Huffman coding, min-heap | O(n log n) |
| Grep Clone | Regex matching, iterators | O(n × m) |
| JSON Parser | Recursive descent, tokenization | O(n) |

## License

MIT License - Feel free to use, modify, and learn from!
