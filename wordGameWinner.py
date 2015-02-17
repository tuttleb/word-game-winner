class Node():
    __slots__ = ('children', 'val', 'isEndValue')
    
    def __init__(self, val, isEndValue, children):
        self.val = val
        self.isEndValue = isEndValue
        self.children = children
    
class Configuration():
    __slots__ = ('position', 'board', 'word', 'parent')
    
    def __init__(self, position, board, word, parent=None):
        self.position = position
        self.board = board
        self.word = word
        self.parent = parent
        
def populateWords(wordFile = "wordsEn.txt"):
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
                newNode = Node(character, i == length, {})
                currentPos[character] = newNode
                currentPos = newNode.children
                
    return root
    
def getBoard():
    count = 0
    vals = [''] * 16
    
    while count < 16:
        nextBlock = input("Next block (submit nothing to go back): ")
        if nextBlock == "" and count > 0:
            count -= 1
        else:
            vals[count] = nextBlock
            count += 1
    return vals

def printBoard(board):
    for i in range(16):
        if i % 4 == 0:
            print()
        print(board[i], end="\t")
    print()
    
def solve(board, words):
    count = 0
    found = []
    for position in range(16):
        newBoard = board[:]
        newBoard[position] = None
        newConfig = Configuration(position, newBoard, [board[position]])
        if not isValid(newConfig, words):
            continue
        possibilities = [newConfig]
        
        while possibilities:
            count += 1
            next = possibilities.pop(0)
            possibilities  += getDescendents(next, words)
            if isWord(next, words) and "".join(next.word) not in found:
                found.append("".join(next.word))
                #printWord(next)
    found.sort(key=len)
    while(found):
        for i in range(8):
            if found:
                print(found.pop())
                print()
        input("...")
        
def printWord(configuration):
    word = "".join(configuration.word).replace('-','')
    count = len(word)
    print("----------------------------------------------------")
    print(word)
    """
    boardCopy = configuration.board[:]
    current = configuration
    while count > 0:
        boardCopy[current.position] = count
        count -= 1
        current = current.parent
    for i in range(16):
        if i % 4 == 0:
            print()
        print(boardCopy[i], end="\t")
    print("\n----------------------------------------------------")
    """
        
def isValid(configuration, words):
    length = len(configuration.word)
    for i, block in enumerate(configuration.word):
        if block is None:
            return False
        if i != 0 and block.endswith("-"):
            return False
        elif i != length-1 and block.startswith("-"):
            return False
            
    wholeWord = "".join(configuration.word).replace("-", "")
    current = words
    for character in wholeWord:
        if character in current:
            current = current[character].children
        else:
            return False
    return True
    
def isWord(configuration, words):
    wholeWord = "".join(configuration.word).replace("-", "")    
    current = words
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
    
def getDescendents(configuration, words):
    descendents = []

    #top left
    if configuration.position % 4 != 0 and configuration.position > 3:
        _descendentHelper(configuration, words, configuration.position - 5, descendents)
            
    #top
    if configuration.position > 3:
        _descendentHelper(configuration, words, configuration.position - 4, descendents)
        
    #top right
    if (configuration.position+1) % 4 != 0 and configuration.position > 3:
        _descendentHelper(configuration, words, configuration.position - 3, descendents)
        
    #right
    if (configuration.position+1) % 4 != 0:
         _descendentHelper(configuration, words, configuration.position + 1, descendents)
         
    #bottom right
    if (configuration.position+1) % 4 != 0 and configuration.position < 12:
        _descendentHelper(configuration, words, configuration.position + 5, descendents)
        
    #bottom
    if configuration.position < 12:
        _descendentHelper(configuration, words, configuration.position + 4, descendents)
        
    #bottom left
    if configuration.position < 12 and configuration.position % 4 != 0:
        _descendentHelper(configuration, words, configuration.position + 3, descendents)
        
    #left
    if configuration.position % 4 != 0:
        _descendentHelper(configuration, words, configuration.position - 1, descendents)
    return descendents
    
def _descendentHelper(configuration, words, currentPos, descendents):
    boardCopy = configuration.board[:]
    boardCopy[currentPos] = None
    newConfig = Configuration(currentPos, boardCopy, configuration.word + [configuration.board[currentPos]], configuration)
    if isValid(newConfig, words):
        descendents.append(newConfig)
   
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
        
def main():
    words = populateWords()
    #printWordTree(words)
    #board = ['n','u','i','s','m','a','r','e','n','o','w','r','e','m','o','t']
    board = getBoard()
    printBoard(board)
    solve(board, words)
    
if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    