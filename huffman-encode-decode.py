import heapq
import os
from collections import defaultdict
from pathlib import Path


class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq
    


# handles file compression
class HuffmanEncoder:
    def __init__(self):
        self.codes = {}
        self.reverse_mapping = {}
    
    # counts frequency of each character in the input data
    def build_frequency_dict(self, data):
        frequency = defaultdict(int)
        for char in data:
            frequency[char] += 1
        return frequency
    
    # min-heap
    def build_heap(self, frequency):
        heap = []
        for char, freq in frequency.items():
            node = HuffmanNode(char=char, freq=freq)
            heapq.heappush(heap, node)
        return heap
    
    # builds the Huffman tree by merging nodes
    def build_huffman_tree(self, heap):
        while len(heap) > 1:
            node1 = heapq.heappop(heap)
            node2 = heapq.heappop(heap)
            
            merged = HuffmanNode(freq=node1.freq + node2.freq, left=node1, right=node2)
            heapq.heappush(heap, merged)
        return heap[0]
    
    
    def build_codes_helper(self, root, current_code):
        if root is None:
            return
        
        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return
        
        self.build_codes_helper(root.left, current_code + "0")
        self.build_codes_helper(root.right, current_code + "1")
    
    # generates binary codes for each character
    def build_codes(self, root):
        self.build_codes_helper(root, "")
    
    # converts the input data into a binary string using Huffman codes
    def get_encoded_text(self, data):
        encoded_text = ""
        for char in data:
            encoded_text += self.codes[char]
        return encoded_text
    

    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        for _ in range(extra_padding):
            encoded_text += "0"
        
        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text
    

    def get_byte_array(self, padded_encoded_text):
        if len(padded_encoded_text) % 8 != 0:
            print("Encoded text not padded properly")
            exit(0)
        
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b
    


    # reads input
    # builds frequency dictionary
    # constructs Huffman tree
    # generates codes
    # encodes data
    # writes compressed file with frequency dictionary and encoded data
    def compress(self, input_path, output_path):
        with open(input_path, 'rb') as file:
            data = file.read()
        
        frequency = self.build_frequency_dict(data)
        heap = self.build_heap(frequency)
        root = self.build_huffman_tree(heap)
        self.build_codes(root)
        encoded_text = self.get_encoded_text(data)
        padded_encoded_text = self.pad_encoded_text(encoded_text)
        byte_array = self.get_byte_array(padded_encoded_text)
        
        with open(output_path, 'wb') as output:

            # write size of frequency dictionary (2 bytes)
            freq_dict_size = len(frequency)
            output.write(freq_dict_size.to_bytes(2, byteorder='big'))
            
            # write frequency dictionary
            for char, freq in frequency.items():
                output.write(bytes([char]))
                output.write(freq.to_bytes(4, byteorder='big'))
            
            # write the compressed data
            output.write(bytes(byte_array))
        
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)
        print(f"Compression complete. Original: {original_size} bytes, Compressed: {compressed_size} bytes")
        return output_path



# handles file decompression
class HuffmanDecoder:
    def __init__(self):
        self.reverse_mapping = {}
    
    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        
        padded_encoded_text = padded_encoded_text[8:]
        encoded_text = padded_encoded_text[:-1*extra_padding]
        return encoded_text
    
    # converts binary string back to original data
    def decode_text(self, encoded_text):
        current_code = ""
        decoded_text = bytearray()
        
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                char = self.reverse_mapping[current_code]
                decoded_text.append(char)
                current_code = ""
        
        return decoded_text
    


    def decompress(self, input_path, output_path):
        with open(input_path, 'rb') as file:


            freq_dict_size = int.from_bytes(file.read(2), byteorder='big')
            
            # read frequency dictionary
            frequency = {}
            for _ in range(freq_dict_size):
                char = file.read(1)[0]
                freq = int.from_bytes(file.read(4), byteorder='big')
                frequency[char] = freq
            
            # rebuilds Huffman tree
            encoder = HuffmanEncoder()
            heap = encoder.build_heap(frequency)
            root = encoder.build_huffman_tree(heap)
            encoder.build_codes(root)
            self.reverse_mapping = encoder.reverse_mapping
            
            # read remaining data
            bit_string = ""
            byte = file.read(1)
            while byte:
                byte = byte[0]
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)
            
            encoded_text = self.remove_padding(bit_string)
            decompressed_data = self.decode_text(encoded_text)
        
        with open(output_path, 'wb') as output:
            output.write(decompressed_data)
        
        original_size = os.path.getsize(input_path)
        decompressed_size = os.path.getsize(output_path)
        print(f"Decompression complete. Compressed: {original_size} bytes, Decompressed: {decompressed_size} bytes")
        return output_path



def main():
    print("Using zipit, do you want to compress or decompress a file?")
    print("1. Compress File")
    print("2. Decompress File")
    choice = input("Enter (1 or 2): ").strip()
    
    try:
        if choice == "1":
            input_file = input("Enter file to compress: ").strip('"\' ')
            input_path = Path(input_file)
            
            if not input_path.exists():
                print(f"File not found at: {input_path.absolute()}")
                print(f"Current working directory: {os.getcwd()}")
                return
            
            output_file = input("Enter output file name: ").strip('"\' ')
            encoder = HuffmanEncoder()
            encoder.compress(input_path, output_file)
        
        elif choice == "2":
            input_file = input("Enter file to decompress: ").strip('"\' ')
            input_path = Path(input_file)
            
            if not input_path.exists():
                print(f"File not found at: {input_path.absolute()}")
                print(f"Current working directory: {os.getcwd()}")
                return
            
            output_file = input("Enter output file name: ").strip('"\' ')
            decoder = HuffmanDecoder()
            decoder.decompress(input_path, output_file)
        
        else:
            print("Invalid choice! Please enter 1 or 2.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check your input files and try again.")

if __name__ == "__main__":
    main()


    