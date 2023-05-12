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
    if type(node) is str:
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
def getFrequency(input_string):
    freq = {}
    for c in input_string:
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
encode: takes a character array and encodes it based on the encoding table. Returns a binary list.
"""
def encode(inp_array, enc_table):
    encoded_array = ['1'];
    # Always start with a 1, so the casting to binary data doesn't trim leading zeros.
    for c in inp_array:
        encoded_array.append(enc_table[c])

    merged = ''.join(encoded_array)
    binary_data = int(merged, 2)

    return binary_data

"""
decode: takes a binary array and decodes it according to the encoding table. Returns a string.
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

    return ''.join(out_array)

# TODO: Import plain text file

# TODO: Export encoded file

# TODO: Import encoded file

# TODO: Export plain text file

if __name__ == '__main__':
    string1 = '00001111111111111111111112222222222299999999999999'
    string1_test = '19192021'
    string2 = '1111111111111111111111111222222222222222222223333333333333334444444444555555556666666777777888889999'

    freq_list = getFrequency(string1)

    tree = getNodeTree(freq_list)

    # tree[0][0] is the top node of the tree
    codingTable = getCodingTable(tree[0][0])

    # Print out the coding table
    print(' Char | Huffman code ')
    print('----------------------')
    for (char, frequency) in freq_list:
        print(' %-4r |%12s' % (char, codingTable[char]))

    # Encode and decode the string
    bin_enc = encode(string1, codingTable)
    decoded_string = decode(bin_enc, codingTable)

    print(decoded_string)
    print(string1)