#!/usr/bin/env python3
"""
File Compression Tool using Huffman Coding

A CLI tool that implements Huffman coding for lossless text compression.
Great for learning about:
- Greedy algorithms
- Binary trees
- Heap data structures
- Bit manipulation

Usage:
    python file_compressor.py compress input.txt output.huff
    python file_compressor.py decompress output.huff restored.txt
"""

import argparse
import heapq
import pickle
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Optional, Tuple


class HuffmanNode:
    """Node in the Huffman tree."""
    
    def __init__(self, char: Optional[str], freq: int):
        self.char = char
        self.freq = freq
        self.left: Optional['HuffmanNode'] = None
        self.right: Optional['HuffmanNode'] = None
    
    def __lt__(self, other: 'HuffmanNode') -> bool:
        # For heap comparison - lower frequency = higher priority
        return self.freq < other.freq
    
    def is_leaf(self) -> bool:
        return self.char is not None


def build_frequency_table(text: str) -> Dict[str, int]:
    """Count frequency of each character in the text."""
    return Counter(text)


def build_huffman_tree(freq_table: Dict[str, int]) -> Optional[HuffmanNode]:
    """
    Build Huffman tree from frequency table.
    
    Algorithm:
    1. Create a min-heap of nodes (one per character)
    2. While more than one node in heap:
       - Extract two nodes with lowest frequency
       - Create new internal node with sum of frequencies
       - Add back to heap
    3. Return the root node
    """
    if not freq_table:
        return None
    
    # Create min-heap of leaf nodes
    heap = [HuffmanNode(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)
    
    # Special case: only one unique character
    if len(heap) == 1:
        node = heap[0]
        internal = HuffmanNode(None, node.freq)
        internal.left = node
        return internal
    
    # Build tree by combining lowest frequency nodes
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        # Create internal node
        parent = HuffmanNode(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        
        heapq.heappush(heap, parent)
    
    return heap[0]


def build_code_table(root: Optional[HuffmanNode]) -> Dict[str, str]:
    """
    Generate binary codes for each character from the Huffman tree.
    Left edge = 0, Right edge = 1
    """
    codes = {}
    
    def traverse(node: HuffmanNode, code: str):
        if node is None:
            return
        
        if node.is_leaf():
            # Leaf node - assign code (handle special case of single char)
            codes[node.char] = code if code else "0"
            return
        
        traverse(node.left, code + "0")
        traverse(node.right, code + "1")
    
    traverse(root, "")
    return codes


def encode_text(text: str, code_table: Dict[str, str]) -> str:
    """Encode text using Huffman codes."""
    return "".join(code_table[char] for char in text)


def decode_text(encoded: str, root: HuffmanNode) -> str:
    """Decode binary string back to text using Huffman tree."""
    if root is None:
        return ""
    
    result = []
    node = root
    
    for bit in encoded:
        # Traverse tree based on bit
        if bit == "0":
            node = node.left
        else:
            node = node.right
        
        # Reached leaf node
        if node.is_leaf():
            result.append(node.char)
            node = root  # Reset to root for next character
    
    return "".join(result)


def pack_bits(bit_string: str) -> Tuple[bytes, int]:
    """
    Pack a string of '0's and '1's into bytes.
    Returns (bytes, padding_bits) where padding_bits indicates
    how many bits were added to make the length a multiple of 8.
    """
    # Calculate padding needed
    padding = (8 - len(bit_string) % 8) % 8
    bit_string += "0" * padding
    
    # Convert to bytes
    result = bytearray()
    for i in range(0, len(bit_string), 8):
        byte = int(bit_string[i:i+8], 2)
        result.append(byte)
    
    return bytes(result), padding


def unpack_bits(data: bytes, padding: int) -> str:
    """Convert bytes back to bit string, removing padding."""
    bits = "".join(format(byte, '08b') for byte in data)
    if padding > 0:
        bits = bits[:-padding]
    return bits


def compress(input_path: str, output_path: str) -> None:
    """Compress a file using Huffman coding."""
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"Error: File '{input_path}' not found.")
        return
    
    # Read input text
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    if not text:
        print("Error: Input file is empty.")
        return
    
    print(f"Original size: {len(text)} bytes")
    
    # Build Huffman tree and codes
    freq_table = build_frequency_table(text)
    tree_root = build_huffman_tree(freq_table)
    code_table = build_code_table(tree_root)
    
    # Encode text
    encoded = encode_text(text, code_table)
    packed, padding = pack_bits(encoded)
    
    # Save compressed file with metadata
    # Format: [pickled tree] [padding byte] [packed data]
    with open(output_path, 'wb') as f:
        # Pickle the tree structure for decompression
        pickle.dump((tree_root, padding), f)
        f.write(packed)
    
    compressed_size = Path(output_path).stat().st_size
    ratio = (1 - compressed_size / len(text)) * 100
    
    print(f"Compressed size: {compressed_size} bytes")
    print(f"Compression ratio: {ratio:.1f}%")
    print(f"Code table size: {len(code_table)} unique characters")
    
    # Show some sample codes
    print("\nSample codes (most frequent characters):")
    sorted_codes = sorted(code_table.items(), key=lambda x: len(x[1]))
    for char, code in sorted_codes[:5]:
        display = repr(char) if char.isprintable() and not char.isspace() else f"\\x{ord(char):02x}"
        print(f"  {display}: {code}")


def decompress(input_path: str, output_path: str) -> None:
    """Decompress a Huffman-encoded file."""
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"Error: File '{input_path}' not found.")
        return
    
    # Read compressed file
    with open(input_file, 'rb') as f:
        tree_root, padding = pickle.load(f)
        packed = f.read()
    
    # Unpack and decode
    encoded = unpack_bits(packed, padding)
    decoded = decode_text(encoded, tree_root)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decoded)
    
    print(f"Decompressed to: {output_path}")
    print(f"Restored size: {len(decoded)} bytes")


def analyze(input_path: str) -> None:
    """Analyze the frequency distribution of characters in a file."""
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"Error: File '{input_path}' not found.")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    freq_table = build_frequency_table(text)
    total = len(text)
    unique = len(freq_table)
    
    print(f"\nFile Analysis: {input_path}")
    print(f"Total characters: {total}")
    print(f"Unique characters: {unique}")
    print(f"Entropy (bits/char): {calculate_entropy(freq_table, total):.2f}")
    print(f"\nTop 10 most frequent characters:")
    
    for char, freq in freq_table.most_common(10):
        percentage = (freq / total) * 100
        bar = "█" * int(percentage / 2)
        display = repr(char) if char.isprintable() and not char.isspace() else f"\\x{ord(char):02x}"
        print(f"  {display:>4} : {freq:>6} ({percentage:>5.1f}%) {bar}")


def calculate_entropy(freq_table: Dict[str, int], total: int) -> float:
    """Calculate Shannon entropy of the text."""
    import math
    entropy = 0.0
    for freq in freq_table.values():
        p = freq / total
        entropy -= p * math.log2(p)
    return entropy


def main():
    parser = argparse.ArgumentParser(
        description="File Compression Tool using Huffman Coding",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python file_compressor.py compress input.txt output.huff
  python file_compressor.py decompress output.huff restored.txt
  python file_compressor.py analyze input.txt
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Compress command
    compress_parser = subparsers.add_parser('compress', help='Compress a file')
    compress_parser.add_argument('input', help='Input file to compress')
    compress_parser.add_argument('output', help='Output compressed file')
    
    # Decompress command
    decompress_parser = subparsers.add_parser('decompress', help='Decompress a file')
    decompress_parser.add_argument('input', help='Compressed file to decompress')
    decompress_parser.add_argument('output', help='Output restored file')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze file frequency distribution')
    analyze_parser.add_argument('input', help='File to analyze')
    
    args = parser.parse_args()
    
    if args.command == 'compress':
        compress(args.input, args.output)
    elif args.command == 'decompress':
        decompress(args.input, args.output)
    elif args.command == 'analyze':
        analyze(args.input)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
