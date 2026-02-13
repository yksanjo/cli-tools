"""Tests for file_compressor.py"""

import os
import tempfile
from pathlib import Path

import pytest

from file_compressor import (
    HuffmanNode,
    build_code_table,
    build_frequency_table,
    build_huffman_tree,
    decode_text,
    encode_text,
    pack_bits,
    unpack_bits,
)


class TestHuffmanNode:
    def test_node_creation(self):
        node = HuffmanNode('a', 5)
        assert node.char == 'a'
        assert node.freq == 5
        assert node.left is None
        assert node.right is None

    def test_is_leaf(self):
        leaf = HuffmanNode('a', 5)
        assert leaf.is_leaf() is True

        internal = HuffmanNode(None, 10)
        assert internal.is_leaf() is False

    def test_node_comparison(self):
        node1 = HuffmanNode('a', 5)
        node2 = HuffmanNode('b', 10)
        node3 = HuffmanNode('c', 5)

        assert node1 < node2
        assert not (node2 < node1)
        assert not (node1 < node3)  # Equal frequency


class TestFrequencyTable:
    def test_empty_string(self):
        assert build_frequency_table('') == {}

    def test_single_char(self):
        assert build_frequency_table('aaa') == {'a': 3}

    def test_multiple_chars(self):
        text = 'hello world'
        freq = build_frequency_table(text)
        assert freq['l'] == 3
        assert freq['o'] == 2
        assert freq['h'] == 1


class TestHuffmanTree:
    def test_empty_frequency_table(self):
        assert build_huffman_tree({}) is None

    def test_single_char(self):
        tree = build_huffman_tree({'a': 5})
        assert tree is not None
        assert tree.left.char == 'a'

    def test_two_chars(self):
        tree = build_huffman_tree({'a': 1, 'b': 2})
        assert tree is not None
        assert tree.freq == 3

    def test_multiple_chars(self):
        freq = {'a': 5, 'b': 9, 'c': 12, 'd': 13, 'e': 16, 'f': 45}
        tree = build_huffman_tree(freq)
        assert tree is not None
        assert tree.freq == sum(freq.values())


class TestCodeTable:
    def test_single_char(self):
        tree = build_huffman_tree({'a': 5})
        codes = build_code_table(tree)
        assert codes == {'a': '0'}

    def test_two_chars(self):
        tree = build_huffman_tree({'a': 1, 'b': 2})
        codes = build_code_table(tree)
        assert len(codes) == 2
        assert all(len(code) > 0 for code in codes.values())

    def test_prefix_property(self):
        """No code should be a prefix of another code."""
        freq = {'a': 5, 'b': 9, 'c': 12}
        tree = build_huffman_tree(freq)
        codes = build_code_table(tree)

        code_list = list(codes.values())
        for i, code1 in enumerate(code_list):
            for code2 in code_list[i + 1:]:
                assert not code1.startswith(code2)
                assert not code2.startswith(code1)


class TestEncodingDecoding:
    def test_round_trip_simple(self):
        text = 'hello'
        freq = build_frequency_table(text)
        tree = build_huffman_tree(freq)
        codes = build_code_table(tree)

        encoded = encode_text(text, codes)
        decoded = decode_text(encoded, tree)

        assert decoded == text

    def test_round_trip_complex(self):
        text = 'The quick brown fox jumps over the lazy dog!'
        freq = build_frequency_table(text)
        tree = build_huffman_tree(freq)
        codes = build_code_table(tree)

        encoded = encode_text(text, codes)
        decoded = decode_text(encoded, tree)

        assert decoded == text

    def test_round_trip_unicode(self):
        text = 'Hello, 世界! 🌍'
        freq = build_frequency_table(text)
        tree = build_huffman_tree(freq)
        codes = build_code_table(tree)

        encoded = encode_text(text, codes)
        decoded = decode_text(encoded, tree)

        assert decoded == text

    def test_empty_string(self):
        text = ''
        freq = build_frequency_table(text)
        tree = build_huffman_tree(freq)

        assert tree is None
        assert decode_text('', None) == ''


class TestBitPacking:
    def test_exact_bytes(self):
        bits = '10101010'  # 8 bits = 1 byte exactly
        packed, padding = pack_bits(bits)
        assert packed == b'\xaa'
        assert padding == 0
        assert unpack_bits(packed, padding) == bits

    def test_partial_byte(self):
        bits = '101'  # 3 bits, needs 5 padding
        packed, padding = pack_bits(bits)
        assert len(packed) == 1
        assert padding == 5
        assert unpack_bits(packed, padding) == bits

    def test_multiple_bytes(self):
        bits = '1010101011110000'  # 16 bits = 2 bytes
        packed, padding = pack_bits(bits)
        assert len(packed) == 2
        assert padding == 0
        assert unpack_bits(packed, padding) == bits

    def test_empty_bits(self):
        bits = ''
        packed, padding = pack_bits(bits)
        assert packed == b''
        assert padding == 0


class TestIntegration:
    def test_full_compression_round_trip(self):
        """Test compress and decompress using actual files."""
        import tempfile
        from file_compressor import compress, decompress

        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / 'input.txt'
            compressed_file = Path(tmpdir) / 'compressed.huff'
            output_file = Path(tmpdir) / 'output.txt'

            # Create test file
            original_text = 'Hello, World! This is a test of Huffman compression.'
            input_file.write_text(original_text, encoding='utf-8')

            # Compress
            compress(str(input_file), str(compressed_file))
            assert compressed_file.exists()

            # Decompress
            decompress(str(compressed_file), str(output_file))
            assert output_file.exists()

            # Verify
            restored_text = output_file.read_text(encoding='utf-8')
            assert restored_text == original_text

    def test_large_file(self):
        """Test with larger text to see actual compression."""
        import tempfile
        from file_compressor import compress

        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / 'large.txt'
            compressed_file = Path(tmpdir) / 'compressed.huff'

            # Create repetitive text (should compress well)
            original_text = 'AAAAABBBCCCDDDDEEEEE' * 1000
            input_file.write_text(original_text, encoding='utf-8')
            original_size = input_file.stat().st_size

            compress(str(input_file), str(compressed_file))
            compressed_size = compressed_file.stat().st_size

            # Should achieve some compression
            assert compressed_size < original_size


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
