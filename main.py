# Huffman coding
# Kristjan Šoln


# string = 'BCAADDDCCACACAC'
string = '00001111111111111111111112222222222299999999999999'


# Creating tree nodes
class NodeTree(object):

    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def children(self):
        return (self.left, self.right)

    def nodes(self):
        return (self.left, self.right)

    def __str__(self):
        return '%s_%s' % (self.left, self.right)


"""
huffman_code_tree: A function that takes a node tree and creates
a coding table from it.
"""
def huffman_code_tree(node, left=True, binString=''):
    # If we are at the bottom node, return dictionary item
    if type(node) is str:
        return {node: binString}
    # If we arent at the bottom node, split nodes to left and right
    (l, r) = node.children()
    d = dict()
    # Add left and right node to d, recursively
    # Left node is the less probable one, so it gets a one
    d.update(huffman_code_tree(l, True, binString + '1'))
    # Right node is the more probable one, so it gets a zero
    d.update(huffman_code_tree(r, False, binString + '0'))

    return d


# Calculating frequency
freq = {}
for c in string:
    if c in freq:
        freq[c] += 1
    else:
        freq[c] = 1

# Sort based on the second element of each item - the frequency.
# Lambda function is an inline anonymous function. An alternative would be
# to define a function which takes an array and returns the second element of it.
freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)

nodes = freq

# TODO: Create a function from this
# Create a node tree
while len(nodes) > 1:
    # Select current nodes
    (key1, c1) = nodes[-1]
    (key2, c2) = nodes[-2]
    # Create a node from current nodes. Key1 has lower probability than key2,
    # therefore key1 is the left one (gets a zero), and key2 is the right one (gets a one).
    node = NodeTree(key1, key2)
    # Replace current two nodes with an object. Add the previous frequencies and append it.
    nodes = nodes[:-2]
    nodes.append((node, c1 + c2))
    # Resort the nodes based on the frequency.
    nodes = sorted(nodes, key=lambda x: x[1], reverse=True)

# nodes[0][0] is the top node
huffmanCode = huffman_code_tree(nodes[0][0])

print(' Char | Huffman code ')
print('----------------------')
for (char, frequency) in freq:
    print(' %-4r |%12s' % (char, huffmanCode[char]))
