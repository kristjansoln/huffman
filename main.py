# Huffman coding
# Kristjan Šoln

from math import ceil
from os.path import getsize
import numpy as np
from collections import Counter


"""
NodeTree: A class that defines an individual node in the node tree.
Each node has a left and a right child.
"""
class NodeTree(object):

    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def children(self):
        return (self.left, self.right)

    def __str__(self):
        return '%s_%s' % (self.left, self.right)


"""
getCodingTable: A function that takes a node tree and creates
a coding table from it.
"""
def getCodingTable(node, binString=''):
    # If we are at the bottom node, return dictionary item
    # Checks for str as well, to be able to analyze both binary data and strings
    if (type(node) is int) or (type(node) is str) or (type(node) is bytes):
        return {node: binString}
    # If we arent at the bottom node, split nodes to left and right
    (l, r) = node.children()
    d = dict()
    # Add left and right node to d, recursively
    # Left node is the less probable one, so it gets a one
    d.update(getCodingTable(l, binString + '1'))
    # Right node is the more probable one, so it gets a zero
    d.update(getCodingTable(r, binString + '0'))

    return d


"""
getFrequency: Takes a string of characters and returns a list
of tuples containing unique characters and number of their
occurences. The list is sorted by this frequency.
"""
def getFrequency(bytes_data, order=1):
    # Create N-byte pairs
    byte_pairs = [bytes_data[i:i+order]
                  for i in range(0, len(bytes_data) - order + 1, order)]
    # Calculate N-byte pair frequency
    freq = Counter(byte_pairs)

    # Sort based on the second element of each item - the frequency.
    # Lambda function is an inline anonymous function. An alternative would be
    # to define a function which takes an array and returns the second element of it.
    freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return freq


"""
getNodeTree: create a node tree from a sorted list of unique characters and their frequencies.
"""
def getNodeTree(freq_array):
    node_tree = freq_array
    while len(node_tree) > 1:
        # Select current nodes
        (key1, c1) = node_tree[-1]
        (key2, c2) = node_tree[-2]
        # Create a node from current nodes. Key1 has lower probability than key2,
        # therefore key1 is the left one (gets a zero), and key2 is the right one (gets a one).
        node = NodeTree(key1, key2)
        # Replace current two nodes with an object. Add the previous frequencies and append it.
        node_tree = node_tree[:-2]
        node_tree.append((node, c1 + c2))
        # Resort the nodes based on the frequency.
        node_tree = sorted(node_tree, key=lambda x: x[1], reverse=True)

    return node_tree


"""
encode: takes a byte array and encodes it based on the encoding table. Returns an integer, equal to the binary data.
"""
def encode(inp_array, enc_table, order):
    encoded_array = ['1']
    # Always start with a 1, so the casting to binary data doesn't trim leading zeros.
    for i in range(0, len(inp_array)-order+1, order):
        encoded_array.append(enc_table[inp_array[i:i+order]])

    data = ''.join(encoded_array)
    data = int(data, 2)

    return data


"""
decode: takes an integer, equal to the binary data, and decodes it according to the encoding table. Returns byte array.
"""
def decode(binary_data, enc_table):
    out_array = b''
    # Remove the '0b' prefix, along with the added leading '1'. See 'encode()'
    binary_data = bin(binary_data)[3:]

    # Reverse the dictionary to make the search faster
    reverse_table = {}
    for key, value in enc_table.items():
        reverse_table[value] = key

    keys = reverse_table.keys()
    el = ''
    for b in binary_data:
        # If you find a match for el in the encoding table, decode it. Otherwise add the next bit and try again.
        el = el + b
        if el in keys:
            out_array = out_array + reverse_table[el]
            el = ''

    return out_array


"""
readPlainFile: Read binary data from a file
"""
def readPlainFile(file_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()
    return binary_data


"""
writePlainFile: Write binary data to a file
"""
def writePlainFile(file_path, data):
    with open(file_path, 'wb') as file:
        file.write(data)
    return


"""
readEncodedFile: Read binary data from an encoded file.
Also read the encoding table from the header.
"""
def readEncodedFile(file_path):
    with open(file_path, 'rb') as file:

        # Extract header from file
        header = file.read().split(b'header_end:::\n')[0]
        header = header.split(b':::\n')[:-1]

        # Extract padding info from header
        if b"Padding_len" not in header[0]:
            raise Exception("Invalid padding information")
        padding_len = int.from_bytes(header[0].split(b":::")[
                                     1], byteorder='little')
        header = header[1:]

        # Extract encoding table from header
        enc_table = {}
        for line in header:
            key, value = line.rsplit(b':::', 1)
            value = str(value)[2:-1]
            enc_table[key] = value

    # Get binary data from the file
    with open(file_path, 'rb') as file:
        # Skip the header
        binary_data = file.read().split(b'header_end:::\n')[1]

    data = int.from_bytes(binary_data, byteorder='little')

    return (data, enc_table, padding_len)


"""
writeEncodedToFile: write the encoded data to a file.
Adds the encoding table in the header of the file.
"""
def writeEncodedToFile(file_path, data, encoding_table, padding_len):
    # First, write the header in plain text
    with open(file_path, 'wb') as file:

        # Add padding info
        a = b"Padding_len:::" + bytes([padding_len]) + b":::\n"
        file.write(a)

        for key, value in encoding_table.items():
            # Use custom delimiters in order to avoid delimiters in text
            a = key+b':::'+bytes(bytearray(value, 'ascii'))+b':::\n'
            file.write(a)

        file.write(b'header_end:::\n')

    # Now write the binary encoded data
    length = ceil(len(bin(data)[2:])/8)
    binary_data = data.to_bytes(length, byteorder='little', signed=False)
    with open(file_path, 'ab') as file:
        file.write(binary_data)

    return


"""
encodeFile: read a file, encode it and optionally write it into a destination file
"""
def encodeFile(src_file, dest_file=None, order=1):
    print("encodeFile: reading " + src_file)
    plain = readPlainFile(src_file)
    # The input data lenght must be divisible by the specified order.
    # If it is not, it must be padded with extra characters, or the algorithm
    # skips the last character.
    padding_len = len(plain) % order
    if padding_len != 0:
        print("encodeFile: The encoded file has to be padded")
        plain = plain + b' '*padding_len

    print("encodeFile: generating coding table")
    freq_list = getFrequency(plain, order)
    tree = getNodeTree(freq_list)
    coding_table = getCodingTable(tree[0][0])  # Top node of the tree

    print("encodeFile: encoding")
    encoded = encode(plain, coding_table, order)

    # Write to destination file, if given in arguments
    if dest_file is not None:
        print("encodeFile: writing to " + dest_file)
        writeEncodedToFile(dest_file, encoded, coding_table, padding_len)
        comp_ratio = getCompressionRatio(dest_file, src_file)
        efficiency = getEfficiency(plain, coding_table, order)
        print("encodeFile: Compression ratio: " +
              str(comp_ratio*100) + "%")
        print("encodeFile: Efficiency: " + str(efficiency) + "%")

    return (encoded, coding_table)


"""
decodeFile: read an encoded file, decode it and optionally write it into a destination file
"""
def decodeFile(src_file, dest_file=None):
    print("decodeFile: reading " + src_file)
    encoded, enc_table, padding_len = readEncodedFile(src_file)
    print("decodeFile: decoding file")
    decoded = decode(encoded, enc_table)

    # Remove padding
    decoded = decoded[:len(decoded)-padding_len]

    # Write to destination file, if given in arguments
    if dest_file is not None:
        print("decodeFile: writing to " + dest_file)
        writePlainFile(dest_file, decoded)

    return decoded


"""
getEfficiency: Returns compression efficiency
"""
def getEfficiency(plain_data, coding_table, order=1):

    freq_pairs = getFrequency(plain_data, order)
    freq = np.fromiter((f for k, f in freq_pairs), int)
    total = np.sum(freq)

    # Calculate entropy
    entr = -(np.sum(freq*np.log2(freq)))/total + np.log2(total)
    print("Entropija:", entr)

    # Calculate average encoding length
    n_bar = np.sum(np.fromiter((f*len(coding_table[k]) for k, f in freq_pairs), int)) / total
    print("Povprečna dolžina kodne zamenjave:", n_bar)

    # Calculate efficiency
    return entr / n_bar


"""
getCompressionRatio: Returns file size ratio
"""
def getCompressionRatio(comp_file, plain_file):
    comp_size = getsize(comp_file)
    plain_size = getsize(plain_file)
    return comp_size/plain_size


if __name__ == '__main__':
    print("------besedilo.txt--------------------------------")
    print("order = 1")
    encodeFile('test/besedilo.txt', 'test/encoded.huf', order=1)
    decodeFile('test/encoded.huf', 'test/decoded.txt')
    print("order = 2")
    encodeFile('test/besedilo.txt', 'test/encoded.huf', order=2)
    decodeFile('test/encoded.huf', 'test/decoded.txt')
    print("order = 3")
    encodeFile('test/besedilo.txt', 'test/encoded.huf', order=3)
    # decodeFile('test/encoded.huf', 'test/decoded.txt')

    print("------random binary data--------------------------------")
    print("order = 1")
    encodeFile('test/binary_data2', 'test/encoded.huf', order=1)
    # decodeFile('test/encoded.huf', 'test/decoded_binary_data')
    print("order = 2")
    encodeFile('test/binary_data2', 'test/encoded.huf', order=2)
    # decodeFile('test/encoded.huf', 'test/decoded_binary_data')

    print("------slika.bmp--------------------------------")
    print("order = 1")
    encodeFile('test/slika.bmp', 'test/encoded.huf', order=1)
    decodeFile('test/encoded.huf', 'test/decoded.bmp')
    print("order = 2")
    encodeFile('test/slika.bmp', 'test/encoded.huf', order=2)
    # decodeFile('test/encoded.huf', 'test/decoded.bmp')
    print("order = 3")
    encodeFile('test/slika.bmp', 'test/encoded.huf', order=3)
    # decodeFile('test/encoded.huf', 'test/decoded.bmp')

    print("------ Get entropy of a binary file ------------------------")
    for file in ['test/binary_data1', 'test/binary_data2', 'test/binary_data3', 'test/binary_data4']:
        for order in [1, 2, 3]:
            data = readPlainFile(file)
            freq_pairs = getFrequency(data, order)
            freq = np.fromiter((f for k, f in freq_pairs), int)
            total = np.sum(freq)
            # Calculate entropy
            entr = -(np.sum(freq*np.log2(freq)))/total + np.log2(total)
            print("File: %s size[MB]: %02f order: %d entropy: %7f mean: %3f std:%3f" % (file, getsize(file)/1000000, order, entr, np.average(freq), np.std(freq)) )