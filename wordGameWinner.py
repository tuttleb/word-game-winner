import argparse

class LetterNode():
    __slots__ = ('children', 'val', 'isEndValue')
    
    def __init__(self, val, isEndValue, children):
        """Creates a new LetterNode

        val -- The letter in this node
        isEndValue -- Bool determining if a word ends at this node
        children -- A list of child letter nodes
        """

        self.val = val
        self.isEndValue = isEndValue
        self.children = children
    
class Configuration():
    """Represents a 'swipe' on the board. A valid configuration is either an
    english word or the beginning of one.
    """

    __slots__ = ('position', 'blocks', 'word', 'parent')
    
    def __init__(self, position, blocks, word, parent=None):
        """Creates a new configuration

        position -- The index of the current tile, that is the last one in a
            'swipe'
        blocks -- A list of all blocks from the board. Blocks that are already in
            use for this configuration have a value of None
        word -- The word built by this configurations 'swipe'
        parent -- The config that led to this one. This allows for tracing a
            'swipe' back to the start (Default None)
        """

        self.position = position
        self.blocks = blocks
        self.word = word
        self.parent = parent

    def __cmp__(self, other):
        pass

    def isValid(self, wordTree):
        """Determines if this configuration is valid.
        Validity Rules:
        - No block can be used twice
        - A block ending with '-' can only be the first block in a word
        - A block beginning with '-' can only the last block in a word
        - The blocks must make up a word in the word tree, or must be the
            beginning of a word in the word tree

        wordTree -- A tree representing all valid words
        """

        length = len(self.word)
        for i, block in enumerate(self.word):
            if block is None:
                #The same block was used twice
                return False
            if i != 0 and block.endswith("-"):
                #A block ending with a '-' must be the first block in a word
                return False
            elif i != length-1 and block.startswith("-"):
                #A block beginning with '-' must be the last block in a word
                return False
                
        #Turn the blocks into a string
        wholeWord = "".join(self.word).replace("-", "")
        current = wordTree
        for character in wholeWord:
            if character in current:
                current = current[character].children
            else:
                return False
        return True

    def isWord(self, wordTree):
        """Determines if the configuration represents an english word

        wordTree -- A tree representing all valid words
        """

        wholeWord = "".join(self.word).replace("-", "")    
        current = wordTree
        length = len(wholeWord) - 1
        
        for i, character in enumerate(wholeWord):
            if i == length:
                if(character in current):
                    return current[character].isEndValue
                else:
                    return False
            if character in current:
                current = current[character].children
            else:
                return False

    def getDescendents(self, board):
        """Returns a list of configurations that descend from this one.
        Descendents represent continuing the swipe to an adjacent block.

        board -- The board this onfig is on
        """

        neighborPositions = []
        
        #top middle
        if self.position >= board.width:
            neighborPositions += [self.position - board.width]

        #bottom middle
        if self.position < (board.height - 1) * board.width:
            neighborPositions += [self.position + board.width]

        #left
        if self.position % board.width != 0:
            neighborPositions += [self.position - 1]

            #top left
            if self.position >= board.width:
                neighborPositions += [self.position - board.width - 1]

            #bottom left
            if self.position < (board.height - 1) * board.width:
                neighborPositions += [self.position + board.width - 1]


        #right
        if self.position % board.width != board.width - 1:
            neighborPositions += [self.position + 1]

            #top right
            if self.position >= board.width:
                neighborPositions += [self.position - board.width + 1]

            #bottom right
            if self.position < (board.height - 1) * board.width:
                neighborPositions += [self.position + board.width + 1]

        descendents = []

        for position in neighborPositions:
            blocksCopy = self.blocks[:]
            blocksCopy[position] = None

            if self.blocks[position] is not None:
                for grouping in self.blocks[position].split('/'):
                    #Allows for alternate letters separated by the '/' character
                    newConfig = Configuration(position, blocksCopy, self.word + [grouping], parent = self)
                    descendents += [newConfig]

        return descendents

class Board():
    __slots__ = ('blocks', 'width', 'height')
    _MAX_LETTER_WIDTH = 3

    def __init__(self, blocks, width, height):
        """Creates a new board

        blocks -- A list of blocks from the board ordered from left to right, 
            top to bottom. In many cases a block is a single letter, but it can
            also be a combination of symbols representing special rules for the
            block
        width -- The width of the board
        height -- Theh height of the board
        """
        self.blocks = blocks
        self.width = width
        self.height = height

    def __str__(self):
        """
        Returns a string representation of the baord
        """
        result = ""
        for row in range(self.height):
            for col in range(self.width):
                block = self.blocks[row * self.width + col]
                result += format(block, '^' + str(Board._MAX_LETTER_WIDTH))
            result += '\n'
        return result

    def solve(self, wordTree):
        """Returns a list of  words that this board contains

        wordTree -- A tree representing all words
        """

        foundWords = []
        for blockPosition in range(len(self.blocks)):
            adjustedBlocks = self.blocks[:]
            adjustedBlocks[blockPosition] = None #Mark off the current letter as used
            newConfig = Configuration(blockPosition, adjustedBlocks, [self.blocks[blockPosition]])
            possibilities = [newConfig]

            while possibilities:
                currentConfig = possibilities.pop(0)

                if not currentConfig.isValid(wordTree):
                    continue

                possibilities += currentConfig.getDescendents(self)
                if currentConfig.isWord(wordTree) and "".join(currentConfig.word) not in foundWords:
                    foundWords.append("".join(currentConfig.word))

        return foundWords
        
def populateWords(wordFile):
    """Return a word tree using the words from the provided file.

    wordFile -- The file to read
    """

    root = {}
    
    for word in open(wordFile):
        currentPos = root
        length = len(word.strip()) - 1
        for i, character in enumerate(word.strip()):
            if character in currentPos:
                if i == length:
                    currentPos[character].isEndValue = True
                currentPos = currentPos[character].children
            else:
                newNode = LetterNode(character, i == length, {})
                currentPos[character] = newNode
                currentPos = newNode.children
                
    return root
 
def printWordTree(words):
    for key in words.keys():
        print(key + ": ", end="")
        _printWordTreeHelper(words[key].children)
        print()
        print()

def _printWordTreeHelper(root):
    if root:
        for key in root.keys():
            print('{' + key + ": ", end="")
            _printWordTreeHelper(root[key].children)
            print(", ", end="")
        print('}', end="")
    else:
        print("{}", end="")

def isValidDimension(value):
    """Determines if the value provided is a valid board dimension. Throws an
        argparse.ArgumentTypeError if the argument is not an integer and
        greater than zero.

    value -- The value being checked
    """
    try:
        i = int(value)
        if i <= 0:
            raise ValueError()
        return i
    except ValueError:
        raise argparse.ArgumentTypeError("%s is not an integer greater than zero" % value)
        
def main():
    parser = argparse.ArgumentParser(description="Finds words on provided board")

    parser.add_argument('width', type=isValidDimension, help="the width of the board")
    parser.add_argument('height', type=isValidDimension, help="the height of the board")
    parser.add_argument('blocks', help="the blocks on the board from left to right, top to bottom. These should be comma delimited with no spaces")
    #parser.add_argument('form', choices=['list','grids'])
    parser.add_argument('--count', dest='count', type=int, default=100)
    parser.add_argument('--sort', dest='sort', choices=['largest','smallest','none'], default='largest')
    parser.add_argument('--words', dest='words', default='wordsEn.txt', help="name of the file that contains a list of words to look for")
    parser.add_argument('--interactive', dest='interactive', default=False, action='store_true', help="determines if the program should dump out text or step through interactively")

    args = parser.parse_args()
    
    blocks = args.blocks.split(',')

    b = Board(blocks, args.width, args.height)
    words = populateWords(args.words)

    solution = b.solve(words)

    if args.sort == 'largest':
        solution.sort(key=len, reverse=True)
    elif args.sort == 'smallest':
        solution.sort(key=len)

    printed_count = 0
    for word in solution:
        if printed_count >= args.count and args.count >= 0:
            break
        if args.interactive and printed_count != 0 and printed_count % 5 == 0:
            user_input = input("press enter to continue... (q to quit)")
            if user_input == 'q':
                break

        print(word)
        printed_count += 1

if __name__ == "__main__":
    main()
