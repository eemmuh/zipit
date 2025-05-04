# zipit


This program implements Huffman coding, which is a lossless data compression algorithm.


It consists of two main classes: `HuffmanEncoder` for file compression and `HuffmanDecoder` for decompression.

Features
------
* Compresses files using Huffman coding algorithm 
* Decompresses files back to original form
* Supports all file types (pdf, txt, jpeg, etc.)
* Shows compression statistics
* Simple command-line interface


How It Works
---------
## Compression
1. Builds character frequency dictionary
2. Creates Huffman tree from frequencies
3. Assigns optimal binary codes to each character
4. Converts input file to compressed binary stream
5. Saves compressed data with frequency table header
