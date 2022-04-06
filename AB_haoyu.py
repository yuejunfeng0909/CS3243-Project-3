import sys

### IMPORTANT: Remove any print() functions or rename any print functions/variables/string when submitting on CodePost
### The autograder will not run if it detects any print function.

# Helper functions to aid in your implementation. Can edit/remove
def boardCoordToMatCoord(originalCoordinates): # orginal: "("a", 1)" new: (1, 0) row 1 col 0
    col = ord(originalCoordinates[0]) - 97
    row = originalCoordinates[1]
    return (row, col)

def matCoordToBoardCoord(originalCoordinates): # orginal: (1, 0) new: "("a", 1)"
    colAsChar = chr(originalCoordinates[1] + 97)
    rowAsInt= originalCoordinates[0]
    return (colAsChar, rowAsInt) # return a string

def duplicateDict(dict):
    duplicate = {}
    for key, value in dict.items():
        duplicate[key] = value
    return duplicate
    
def createNewState(currentState, oldPos, newPos):
    oldPieces = currentState.pieces
    oldMap = currentState.map
    oldSide = currentState.side
    allPieces = currentState.allPieces
    newPieces = duplicateDict(oldPieces)
    newMap = duplicateDict(oldMap)
    newSide = (oldSide + 1) % 2
    id = oldMap[oldPos] # obtain current piece id
    newMap.pop(oldPos, None) # remove old Pos
    if newPos in newMap: 
        newPieces.pop(newMap[newPos], None)
    newMap[newPos] = id
    newPieces[id] = newPos
    return State(newPieces, newMap, newSide, allPieces)
    
    

class Piece:
    def __init__(self, pos, type, side, id, rows, cols):
        self.type = type
        self.side = side
        self.id = id
        self.rows = rows
        self.cols = cols
        self.pos = pos
    def getType(self):
        return self.type

class King(Piece):
    def __init__(self, pos, side, id, rows, cols):
        super().__init__(pos, "King", side, id, rows, cols)

    def getRange(self, currentState):
        pieceRange = 0
        self.pos = currentState.pieces[self.id]
        for i in range(-1, 2): # be aware of the boundaries
            for j in range(-1, 2):
                moveInRow = i
                moveInCol = j
                if i == 0 and j == 0:
                    continue
                newRow = self.pos[0] + moveInRow
                newCol = self.pos[1] + moveInCol
                if newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols:
                    if (newRow, newCol) in currentState.map:
                        if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side:
                            pieceRange += 1
                    else:
                        pieceRange += 1
        return pieceRange

    def generateNextStates(self, currentState): 
        states = []
        self.pos = currentState.pieces[self.id]
        for i in range(-1, 2): # be aware of the boundaries
            for j in range(-1, 2):
                moveInRow = i
                moveInCol = j
                if i == 0 and j == 0:
                    continue
                newRow = self.pos[0] + moveInRow
                newCol = self.pos[1] + moveInCol
                if newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols:
                    if (newRow, newCol) in currentState.map:
                        if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side:
                            states.append(createNewState(currentState, self.pos, (newRow, newCol)))
                    else:
                        states.append(createNewState(currentState, self.pos, (newRow, newCol)))
        return states

class Rook(Piece):
    def __init__(self, pos, side, id, rows, cols):
        super().__init__(pos, "Rook", side, id, rows, cols)

    def getRange(self, currentState):
        pieceRange = 0
        self.pos = currentState.pieces[self.id]
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                if i * j > 0:
                    moveInRow = 0
                    moveInCol = j
                else:
                    moveInRow = i
                    moveInCol = 0
                newRow = self.pos[0] + moveInRow
                newCol = self.pos[1] + moveInCol
                isInGrid = newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols
                if isInGrid:
                    isNotBlocked = ((newRow, newCol) not in currentState.map)
                    if isNotBlocked == False:
                        if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side:
                            pieceRange += 1
                while isInGrid and isNotBlocked:
                    pieceRange += 1 
                    newRow = newRow + moveInRow
                    newCol = newCol + moveInCol
                    isInGrid = newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols
                    if isInGrid:
                        isNotBlocked = ((newRow, newCol) in currentState.map)
        return pieceRange   

    def generateNextStates(self, currentState):
        states = []
        self.pos = currentState.pieces[self.id]
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                if i * j > 0:
                    moveInRow = 0
                    moveInCol = j
                else:
                    moveInRow = i
                    moveInCol = 0
                newRow = self.pos[0] + moveInRow
                newCol = self.pos[1] + moveInCol
                isInGrid = newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols
                if isInGrid:
                    isNotBlocked = ((newRow, newCol) not in currentState.map)
                    if isNotBlocked == False:
                        if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side: # important
                            states.append(createNewState(currentState, self.pos, (newRow, newCol)))
                while isInGrid and isNotBlocked:
                    states.append(createNewState(currentState, self.pos, (newRow, newCol))) 
                    newRow = newRow + moveInRow
                    newCol = newCol + moveInCol
                    isInGrid = newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols
                    if isInGrid:
                        isNotBlocked = ((newRow, newCol) not in currentState.map)
                        if isNotBlocked == False:
                            if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side:
                                states.append(createNewState(currentState, self.pos, (newRow, newCol)))
        return states   


class Bishop(Piece):
    def __init__(self, pos, side, id, rows, cols):
        super().__init__(pos, "Bishop", side, id, rows, cols)

    def getRange(self, currentState):
        pieceRange = 0
        self.pos = currentState.pieces[self.id]
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                moveInRow = i
                moveInCol = j
                newRow = self.pos[0] + moveInRow
                newCol = self.pos[1] + moveInCol
                isInGrid = newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols
                if isInGrid:
                    isNotBlocked = ((newRow, newCol) not in currentState.map)
                    if isNotBlocked == False:
                        if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side: # important
                            pieceRange += 1
                while isInGrid and isNotBlocked:
                    pieceRange += 1
                    newRow = newRow + moveInRow
                    newCol = newCol + moveInCol
                    isInGrid = newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols
                    if isInGrid:
                        isNotBlocked = ((newRow, newCol) not in currentState.map)
                        if isNotBlocked == False:
                            if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side: # important
                                pieceRange += 1
        return pieceRange

    def generateNextStates(self, currentState):
        states = []
        self.pos = currentState.pieces[self.id]
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                moveInRow = i
                moveInCol = j
                newRow = self.pos[0] + moveInRow
                newCol = self.pos[1] + moveInCol
                isInGrid = newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols
                if isInGrid:
                    isNotBlocked = ((newRow, newCol) not in currentState.map)
                    if isNotBlocked == False:
                        if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side: # important
                            states.append(createNewState(currentState, self.pos, (newRow, newCol)))
                while isInGrid and isNotBlocked:
                    states.append(createNewState(currentState, self.pos, (newRow, newCol)))
                    newRow = newRow + moveInRow
                    newCol = newCol + moveInCol
                    isInGrid = newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols
                    if isInGrid:
                        isNotBlocked = ((newRow, newCol) not in currentState.map)
                        if isNotBlocked == False:
                            if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side: # important
                                states.append(createNewState(currentState, self.pos, (newRow, newCol)))
        return states
    
class Queen(Piece):
    def __init__(self, pos, side, id, rows, cols):
        super().__init__(pos, "Queen", side, id, rows, cols)

    def getRange(self, currentState):
        pieceRange = 0
        self.pos = currentState.pieces[self.id]
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                moveInRow = i
                moveInCol = j
                newRow = self.pos[0] + moveInRow
                newCol = self.pos[1] + moveInCol
                isInGrid = newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols
                if isInGrid:
                    isNotBlocked = ((newRow, newCol) not in currentState.map)
                    if isNotBlocked == False:
                        if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side: # important
                            pieceRange += 1
                while isInGrid and isNotBlocked:
                    pieceRange += 1
                    newRow = newRow + moveInRow
                    newCol = newCol + moveInCol
                    isInGrid = newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols
                    if isInGrid:
                        isNotBlocked = ((newRow, newCol) not in currentState.map)
                        if isNotBlocked == False:
                            if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side: # important
                                pieceRange += 1
        return pieceRange

    def generateNextStates(self, currentState):
        states = []
        self.pos = currentState.pieces[self.id]
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                moveInRow = i
                moveInCol = j
                newRow = self.pos[0] + moveInRow
                newCol = self.pos[1] + moveInCol
                isInGrid = newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols
                if isInGrid:
                    isNotBlocked = ((newRow, newCol) not in currentState.map)
                    if isNotBlocked == False:
                        if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side: # important
                            states.append(createNewState(currentState, self.pos, (newRow, newCol)))
                while isInGrid and isNotBlocked:
                    states.append(createNewState(currentState, self.pos, (newRow, newCol)))
                    newRow = newRow + moveInRow
                    newCol = newCol + moveInCol
                    isInGrid = newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols
                    if isInGrid:
                        isNotBlocked = ((newRow, newCol) not in currentState.map)
                        if isNotBlocked == False:
                            if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side: # important
                                states.append(createNewState(currentState, self.pos, (newRow, newCol)))
        return states


class Knight(Piece):
    def __init__(self, pos, side, id, rows, cols):
            super().__init__(pos, "Knight", side, id, rows, cols)

    def getRange(self, currentState):
        pieceRange = 0
        self.pos = currentState.pieces[self.id]
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                rowDir = i
                colDir = j
                for k in range(2):
                    extendRow = k
                    extendCol = 1 - k
                    if rowDir > 0:
                        moveInRow = rowDir + extendRow
                    else:
                        moveInRow = rowDir - extendRow
                    if colDir > 0:
                        moveInCol = colDir + extendCol
                    else:
                        moveInCol = colDir - extendCol
                    newRow = self.pos[0] + moveInRow
                    newCol = self.pos[1] + moveInCol
                    if newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols:
                        if (newRow, newCol) in currentState.map:
                            if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side:
                                pieceRange += 1
                        else:
                            pieceRange += 1
        return pieceRange

    def generateNextStates(self, currentState):
        states = []
        self.pos = currentState.pieces[self.id]
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                rowDir = i
                colDir = j
                for k in range(2):
                    extendRow = k
                    extendCol = 1 - k
                    if rowDir > 0:
                        moveInRow = rowDir + extendRow
                    else:
                        moveInRow = rowDir - extendRow
                    if colDir > 0:
                        moveInCol = colDir + extendCol
                    else:
                        moveInCol = colDir - extendCol
                    newRow = self.pos[0] + moveInRow
                    newCol = self.pos[1] + moveInCol
                    if newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols:
                        if (newRow, newCol) in currentState.map:
                            if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side:
                                states.append(createNewState(currentState, self.pos, (newRow, newCol)))
                        else:
                            states.append(createNewState(currentState, self.pos, (newRow, newCol)))
        return states
 

        
class Pawn(Piece):
    def __init__(self, pos, side, id, rows, cols):
        super().__init__(pos, "Pawn", side, id, rows, cols)

    def getRange(self, currentState):
        pieceRange = 0
        self.pos = currentState.pieces[self.id]
        if self.side == 0:
            moveInRow = 1
        else:
            moveInRow = -1
        for i in range(-1, 2):
            moveInCol = i
            newRow = self.pos[0] + moveInRow
            newCol = self.pos[1] + moveInCol
            if moveInCol == 0:
                if newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols:
                    if (newRow, newCol) not in currentState.map:
                        pieceRange += 1
            else:
                if newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols:
                    if (newRow, newCol) in currentState.map:
                        if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side:
                            pieceRange += 1
        return pieceRange
    
    def generateNextStates(self, currentState):
        states = []
        self.pos = currentState.pieces[self.id]
        if self.side == 0:
            moveInRow = 1
        else:
            moveInRow = -1
        for i in range(-1, 2):
            moveInCol = i
            newRow = self.pos[0] + moveInRow
            newCol = self.pos[1] + moveInCol
            if moveInCol == 0:
                if newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols:
                    if (newRow, newCol) not in currentState.map:
                        states.append(createNewState(currentState, self.pos, (newRow, newCol)))
            else:
                if newRow > -1 and newRow < self.rows and newCol > -1 and newCol < self.cols:
                    if (newRow, newCol) in currentState.map:
                        if currentState.allPieces[currentState.map[(newRow, newCol)]].side != self.side:
                            states.append(createNewState(currentState, self.pos, (newRow, newCol)))
        return states

class Game:
    pass

class State:
    def __init__(self, pieces, map, side, allPieces):
        self.pieces = pieces # a dict: {id: (r, c)}
        self.map = map # map is a dictionary {(r, c): id}
        self.side = side
        self.allPieces = allPieces # a dict: {id: Piece}
    
    def evaluate(self):
        wK, wQ, wR, wN, wB, wP, bK, bQ, bR, bN, bB, bP = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        wMobility, bMobility = 0, 0
        kingWt = 1000
        queenWt = 5
        rookWt = 4
        knightWt = 3
        bishopWt = 4
        pawnWt = 2
        mobilityWt = 5
        for id in self.pieces:
            currentPiece = self.allPieces[id]
            if currentPiece.side == 0:
                if currentPiece.type == "King":
                    wK += 1
                elif currentPiece.type == "Queen":
                    wQ += 1
                elif currentPiece.type == "Rook":
                    wR += 1
                elif currentPiece.type == "Knight":
                    wN += 1
                elif currentPiece.type == "Bishop":
                    wB += 1
                else:
                    wP += 1
                wMobility += currentPiece.getRange(self)
            else:
                if currentPiece.type == "King":
                    bK += 1
                elif currentPiece.type == "Queen":
                    bQ += 1
                elif currentPiece.type == "Rook":
                    bR += 1
                elif currentPiece.type == "Knight":
                    bN += 1
                elif currentPiece.type == "Bishop":
                    bB += 1
                else:
                    bP += 1
                bMobility += currentPiece.getRange(self)
        materialScore = kingWt * (wK-bK) + queenWt * (wQ-bQ) + rookWt * (wR-bR) + knightWt * (wN-bN) + bishopWt * (wB-bB) + pawnWt * (wP-bP)
        mobilityScore = mobilityWt * (wMobility - bMobility)
        eval = materialScore + mobilityScore
        return eval

    def generateChildStates(self):
        states = []
        for pieceId in self.pieces:
            if self.allPieces[pieceId].side == self.side:
            # print(self.allPieces[pieceId])
            # print(self.allPieces[pieceId].generateNextStates(self))
                states += self.allPieces[pieceId].generateNextStates(self)
        return states

    def isTerminal(self):
        hasWK = False
        hasBK = False
        for id in self.pieces:
            if self.allPieces[id].type == "King":
                if self.allPieces[id].side == 0:
                    hasWK = True
                else:
                    hasBK = True
        return (hasWK == False or hasBK == False)

#Implement your minimax with alpha-beta pruning algorithm here.
def ab(currentState, depth, alpha, beta):
    if depth == 0 or currentState.isTerminal() == True:
        return (currentState.evaluate(), currentState)

    if currentState.side == 0:
        maxEval = -10E8
        maxState = None
        for newState in currentState.generateChildStates():
            eval = ab(newState, depth - 1, alpha, beta)
            if eval[0] > maxEval:
                maxEval = eval[0]
                maxState = newState
            alpha = max(alpha, eval[0])
            if beta <= alpha:
                break
        return (maxEval, maxState)
    else:
        minEval = 10E8
        minState = None
        for newState in currentState.generateChildStates():
            eval = ab(newState, depth - 1, alpha, beta)
            if eval[0] < minEval:
                minEval = eval[0]
                minState = newState
            beta = min(beta, eval[0])
            if beta <= alpha:
                break
        return (minEval, minState)


def find_between(string, first, last):   
    start = string.index(first) + len(first)
    end = string.index(last, start)
    return string[start:end]

def generateMove(prevState, newState):
    for id in prevState.pieces:
        if id in newState.pieces:
            if prevState.pieces[id] != newState.pieces[id]:
                return (matCoordToBoardCoord(prevState.pieces[id]), matCoordToBoardCoord(newState.pieces[id]))
    return ()


def generateGameboard(fn):
    gameboard = {}
    file = open(fn, 'r')
    line1 = file.readline()
    rows = int(find_between(line1, "Rows:", "\n"))
    line2 = file.readline()
    cols = int(find_between(line2, "Cols:", "\n"))
    line3 = file.readline()
    line4 = file.readline()
    line = file.readline()
    while "Number of Own King" not in line:
        line = line.strip()
        type = line.split(",")[0][1:]
        pos = line.split(",")[1][:-1]
        gameboard[(pos[0], int(pos[1:]))] = (type, 'Black')
        line = file.readline()
    line = file.readline()
    line = file.readline()
    while len(line) != 0:
        line = line.strip()
        type = line.split(",")[0][1:]
        pos = line.split(",")[1][:-1]
        gameboard[(pos[0], int(pos[1:]))] = (type, 'White')
        line = file.readline()
    return gameboard

def generatePiece(pieceInfo, id):
    type = pieceInfo[0]
    if pieceInfo[1] == 'White':
        side = 0
    else:
        side = 1
    if type == "Rook":
        return Rook(None, side, id, 5, 5)
    elif type == "Bishop":
        return Bishop(None, side, id, 5, 5)
    elif type == "Queen":
        return Queen(None, side, id, 5, 5)
    elif type == "Knight":
        return Knight(None, side, id, 5, 5)
    elif type == "Pawn":
        return Pawn(None, side, id, 5, 5)
    else:
        assert type == "King"
        return King(None, side, id, 5, 5)

def initState(gameboard):
    id = 0
    allPieces = {}
    map = {}
    pieces = {}
    side = 0
    for pos in gameboard:
        piece = generatePiece(gameboard[pos], id)
        allPieces[id] = piece
        posInMat = boardCoordToMatCoord(pos)
        map[posInMat] = id
        pieces[id] = posInMat
        id += 1
    return State(pieces, map, side, allPieces)

def test():
    piece1 = Knight(None, 1, 0, 3, 3)
    piece2 = King(None, 1, 0, 3, 3)
    piece3 = Knight(None, 0, 0, 3, 3)
    piece4 = King(None, 0, 3, 3, 3)
    allPieces = {0: piece1, 1: piece2, 2: piece3, 3: piece4}
    map = {(2, 0): 0, (0, 0): 1, (0, 2): 2, (2, 2): 3}
    pieces = {0: (2, 0), 1: (0, 0), 2: (0, 2), 3: (2, 2)}
    side = 0
    initialState = State(pieces, map, side, allPieces)
    # return piece1.generateNextStates(initialState)
    return initialState.evaluate()


# print(test())



### DO NOT EDIT/REMOVE THE FUNCTION HEADER BELOW###
# Chess Pieces: King, Queen, Knight, Bishop, Rook (First letter capitalized)
# Colours: White, Black (First Letter capitalized)
# Positions: Tuple. (column (String format), row (Int)). Example: ('a', 0)

# Parameters:
# gameboard: Dictionary of positions (Key) to the tuple of piece type and its colour (Value). This represents the current pieces left on the board.
# Key: position is a tuple with the x-axis in String format and the y-axis in integer format.
# Value: tuple of piece type and piece colour with both values being in String format. Note that the first letter for both type and colour are capitalized as well.
# gameboard example: {('a', 0) : ('Queen', 'White'), ('d', 10) : ('Knight', 'Black'), ('g', 25) : ('Rook', 'White')}
#
# Return value:
# move: A tuple containing the starting position of the piece being moved to the new position for the piece. x-axis in String format and y-axis in integer format.
# move example: (('a', 0), ('b', 3))
def studentAgent(gameboard):
    # You can code in here but you cannot remove this function, change its parameter or change the return type
    initialState = initState(gameboard)
    # print(initialState.pieces)
    # print(initialState.generateChildStates())
    output = ab(initialState, 2, -10E8, 10E8)
    newState = output[1]
    # print(newState.pieces)
    # print(output[0])
    move = generateMove(initialState, newState)
    return move #Format to be returned (('a', 0), ('b', 3))

def run():
    fn = sys.argv[1]
    return studentAgent(generateGameboard(fn))

# print(run())