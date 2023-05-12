# Huffman coding
# Kristjan Šoln



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
def getCodingTable(node, left=True, binString=''):
    # If we are at the bottom node, return dictionary item
    # Checks for str as well, to be able to analyze both binary data and strings
    if (type(node) is int) or (type(node) is str):
        return {node: binString}
    # If we arent at the bottom node, split nodes to left and right
    (l, r) = node.children()
    d = dict()
    # Add left and right node to d, recursively
    # Left node is the less probable one, so it gets a one
    d.update(getCodingTable(l, True, binString + '1'))
    # Right node is the more probable one, so it gets a zero
    d.update(getCodingTable(r, False, binString + '0'))

    return d


"""
getFrequency: Takes a string of characters and returns a list
of tuples containing unique characters and number of their
occurences. The list is sorted by this frequency.
"""
def getFrequency(input_array):
    freq = {}
    for c in input_array:
        if c in freq:
            freq[c] += 1
        else:
            freq[c] = 1

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
def encode(inp_array, enc_table):
    encoded_array = ['1'];
    # Always start with a 1, so the casting to binary data doesn't trim leading zeros.
    for c in inp_array:
        encoded_array.append(enc_table[c])

    data = ''.join(encoded_array)
    data = int(data, 2)

    return data

"""
decode: takes an integer, equal to the binary data, and decodes it according to the encoding table. Returns byte array.
"""
def decode(binary_data, enc_table):
    out_array = []
    # Remove the '0b' prefix, along with the added leading '1'. See 'encode()'
    binary_data = bin(binary_data)[3:]

    el = ''
    for b in binary_data:
        # If you find a match for el in the encoding table, decode it. Otherwise add the next bit and try again.
        el = el + b
        match = next(((symbol, encoding) for symbol, encoding in enc_table.items() if el == encoding), None)
        if match is not None:
            out_array.append(match[0])
            el = ''

    return bytes(out_array)


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
    # Get encoding table from the header
    with open(file_path, 'r') as file:
        enc_table = {}
        for line in file:
            if line == 'header_end\n':
                break
            key, value = line.strip().split(':')
            enc_table[int(key)] = value

    # Get binary data from the file
    with open(file_path, 'rb') as file:
        # Skip the header
        for line in file:
            if line == b'header_end\n':
                break
        binary_data = file.read()

    data = int.from_bytes(binary_data, byteorder='big')

    return (data, enc_table)


"""
writeEncodedToFile: write the encoded data to a file.
Adds the encoding table in the header of the file in plain text.
"""
def writeEncodedToFile(file_path, data, encoding_table):
    # First, write the header in plain text
    with open(file_path, 'w') as file:
        # file.writelines('header_len:'+str(len(encoding_table.items()))+'\n')
        for key, value in encoding_table.items():
            file.write(f"{key}:{value}\n")
        file.writelines('header_end\n')

    # Now write the binary encoded data
    length = len(bin(data)[2:])
    binary_data = data.to_bytes(length, byteorder='big')
    with open(file_path, 'ab') as file:
        file.write(binary_data)

    return


"""
encodeFile: read a file, encode it and optionally write it into a destination file
"""
def encodeFile(src_file, dest_file=None):
    plain = readPlainFile(src_file)
    freq_list = getFrequency(plain)
    tree = getNodeTree(freq_list)
    codingTable = getCodingTable(tree[0][0]) # Top node of the tree
    encoded = encode(plain, codingTable)

    # Write to destination file, if given in arguments
    if dest_file is not None:
        writeEncodedToFile(dest_file, encoded, codingTable)

    return (encoded, codingTable)


"""
decodeFile: read an encoded file, decode it and optionally write it into a destination file
"""
def decodeFile(src_file, dest_file=None):
    encoded, enc_table = readEncodedFile(src_file)
    decoded = decode(encoded, enc_table)

    # Write to destination file, if given in arguments
    if dest_file is not None:
        writePlainFile(dest_file, decoded)

    return decoded


if __name__ == '__main__':
    encodeFile('test/plain-text.txt', 'test/encoded.huf')
    decodeFile('test/encoded.huf', 'test/decoded.txt')