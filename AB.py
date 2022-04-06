import sys

class Piece:

    pieceTypes = ["King", "Queen", "Bishop", "Rook", "Knight", "Pawn"]

    movement = {"King": [(1, 1, 1), (1, 0, 1), (1, -1, 1), (0, -1, 1), (-1, -1, 1), (-1, 0, 1), (-1, 1, 1), (0, 1, 1)],
                "Rook": [(1, 0, 0), (0, -1, 0), (-1, 0, 0), (0, 1, 0)],
                "Bishop": [(1, 1, 0), (1, -1, 0), (-1, -1, 0), (-1, 1, 0)],
                "Queen": [(1, 0, 0), (0, -1, 0), (-1, 0, 0), (0, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0), (-1, 1, 0)],
                "Knight": [(2, 1, 1), (2, -1, 1), (1, 2, 1), (1, -2, 1), (-2, 1, 1), (-2, -1, 1), (-1, 2, 1), (-1, -2, 1)],
                "Pawn": [(1, 0, 1)],
                "Empty": [],
                }

    def __init__(self, pieceType: str, agent: str) -> None:
        self.type = pieceType
        self.agent = agent

    def possibleMovement(pieceType = None):
        return Piece.movement[pieceType]


class Board:


    def __init__(self, cols: int, rows: int, blackPieces: dict, whitePieces: dict) -> None:
        self.piecesPos = [whitePieces, blackPieces]
        self.board_size_x = cols
        self.board_size_y = rows

    def addPiece(self, x:int, y:int, pieceType: str, agent: str) -> None:
        self.piecesPos[0 if agent == "White" else 1][(x, y)] = pieceType
    
    def movePiece(self, agent:str, x:int, y:int, target_x:int, target_y:int) -> None:
        agentIndex = 0 if agent == "White" else 1
        enemyAgentIndex = 1-agentIndex
        pieceType = self.piecesPos[agentIndex].pop((x, y))
        self.piecesPos[agentIndex][(target_x, target_y)]= pieceType
        self.lastMovement = ((x, y), (target_x, target_y))

        # remove eaten piece.
        self.piecesPos[enemyAgentIndex].pop((target_x, target_y), None)

    def isWithinBoard(self, x, y) -> bool:
        if (0 > x or x >= self.board_size_x) or (0 > y or y >= self.board_size_y):
            return False
        return True
    
    def isBlocked(self, x:int, y:int) -> bool:
        if (x, y) in self.piecesPos[0] or (x, y) in self.piecesPos[1]:
            return True
        return False

    def isBlockedByOwn(self, x:int, y:int, currentAgent:str):
        if (x, y) in self.piecesPos[currentAgent]:
            return True
        return False

    def isBlockedByOpponent(self, x:int, y:int, currentAgent:str):
        if (x, y) in self.piecesPos[1-currentAgent]:
            return True
        return False

class pieceMovementModel():

    def __init__(self, board: Board, x: int, y: int, pieceType: str, agent: int):
        self.x = x
        self.y = y
        self.board = board
        self.movements = Piece.movement[pieceType]
        self.pieceType = pieceType
        self.agent = agent

    def moveToDirection(self, x_change: int, y_change: int):
        new_x = self.x + x_change
        new_y = self.y + y_change
        return (new_x, new_y)

    # def __getAllPossibleThreatenToDirection(self, x_change: int, y_change: int, max_steps=0): 
    #     '''Get all the positions that the piece can move to, including position that are being threatened by other pieces''' 
    #     if max_steps == 0: 
    #         max_steps = max(self.board.board_size_x, self.board.board_size_y) 
          
    #     steps = [] 
    #     for i in range(max_steps): 
    #         new_pos = self.moveToDirection((i+1) * x_change, (i+1) * y_change) 
    #         if (not self.board.isWithinBoard(new_pos[0], new_pos[1])) or self.board.isBlocked(new_pos[0], new_pos[1]): 
    #             break 
    #         steps.append(new_pos) 
    #     return steps 
    
    # def getAllPossibleThreaten(self): 
    #     if self.pieceType == "Pawn":
    #         if self.agent == 0:
    #             self.movements = [(1, 0, 1), (1, 1, 1), (1, -1, 1)]
    #         else:
    #             self.movements = [(-1, 0, 1), (-1, 1, 1), (-1, -1, 1)]
        
    #     steps = []
    #     for movement in self.movements: 
    #         xChange, yChange, maxSteps = movement 
    #         steps.extend(self.__getAllPossibleThreatenToDirection(xChange, yChange, maxSteps)) 
    #     return steps

    def __getAllPossibleMovesToDirection(self, x_change: int, y_change: int, max_steps=0): 
        '''Get all the positions that the piece can move to, including position that are being threatened by other pieces''' 
        if max_steps == 0: 
            max_steps = max(self.board.board_size_x, self.board.board_size_y) 
          
        steps = [] 
        for i in range(max_steps): 
            new_pos = self.moveToDirection((i+1) * x_change, (i+1) * y_change) 
            if (not self.board.isWithinBoard(new_pos[0], new_pos[1])) or self.board.isBlockedByOwn(new_pos[0], new_pos[1], self.agent): 
                break 
            steps.append(new_pos) 
            if self.board.isBlockedByOpponent(new_pos[0], new_pos[1], self.agent):
                break
        return steps 

    def getAllPossibleNewPos(self): 
        if self.pieceType == "Pawn":
            if self.agent == 0:
                self.movements = [(1, 0, 1)]
            else:
                self.movements = [(-1, 0, 1)]
        
        steps = []
        for movement in self.movements: 
            xChange, yChange, maxSteps = movement 
            steps.extend(self.__getAllPossibleMovesToDirection(xChange, yChange, maxSteps)) 
        return steps

class State:

    def __init__(self, rows: int, cols:int, whitePieces:dict, blackPieces:dict, currentAgent:str) -> None:
        self.board = Board(cols, rows, blackPieces, whitePieces)
        self.rows = rows
        self.cols = cols
        self.currentAgent = currentAgent

    def possibleNewStates(self):
        # for all pieces of the current agent, list down all the possible movements that can be made by each pieces

        agentIndex = 0 if self.currentAgent == "White" else 1

        # Then add all the possible movements from the current 
        possibleNewStates = []
        agentOfNewState = "Black" if self.currentAgent=="White" else "White"
        for piecePos in self.board.piecesPos[agentIndex]:
            movementModel = pieceMovementModel(self.board, piecePos[0], piecePos[1], self.board.piecesPos[agentIndex][piecePos], agentIndex)
            for newPos in movementModel.getAllPossibleNewPos():
                newState = State(self.rows, self.cols, self.board.piecesPos[0], self.board.piecesPos[1], agentOfNewState)
                newState.board.movePiece(self.currentAgent, piecePos[0], piecePos[1], newPos[0], newPos[1])
                possibleNewStates.append(newState)

        return possibleNewStates

    def isTerminalState(self) -> bool:
        return "King" not in self.board.piecesPos[0].values() or "King" not in self.board.piecesPos[1].values()


def letterToX(character) -> int:
    return ord(character) - ord('a')

def PosToXY(pos) -> tuple:
    return (letterToX(pos[0]), int(pos[1:]))

def XYtoPos(xy: tuple) -> tuple:
    xCharVal: int = xy[0]+ord('a')
    return (chr(xCharVal), xy[1])

def ab(depth: int, state: State, alpha: int, beta: int):

    if depth == 0 or state.isTerminalState():
        # return utility
        # utility = number of white - black
        return len(state.board.piecesPos[0]) - len(state.board.piecesPos[1])

    if state.currentAgent == "White":
        value = float("-inf")
        for newState in state.possibleNewStates():
            value = max(value, ab(depth - 1, "Black", newState, alpha, beta))
            if value >= beta:
                break
            alpha = max(alpha, value)
        return value
    else:
        value = float("inf")
        for newState in state.possibleNewStates():
            value = min(value, ab(depth - 1, "White", newState, alpha, beta))
            if value <= beta:
                break
            alpha = min(alpha, value)
        return value

def parser(testfile):
    f = open(testfile, "r")

    def input():
        line = f.readline().strip("\n")
        return line

    rows = int(input().split(":")[1])
    cols = int(input().split(":")[1])

    blackPieces={}
    # Number of black pieces
    numOfEachBlackPiece = input().split(":")[1].split(" ")
    numOfEachBlackPiece = [int(x) for x in numOfEachBlackPiece]
    input() # ignore line "Position of Enemy Pieces:"
    for _ in range(sum(numOfEachBlackPiece)):
        rawInput = input()[1:-1].split(",")
        piecePosition = PosToXY(rawInput[1])
        blackPieces[piecePosition] = rawInput[0]

    whitePieces = {}
    # Number of white pieces
    numOfEachWhitePiece = input().split(":")[1].split(" ")
    numOfEachWhitePiece = [int(x) for x in numOfEachWhitePiece]
    input() # ignore line "Position of Own Pieces:"
    for _ in range(sum(numOfEachWhitePiece)):
        rawInput = input()[1:-1].split(",")
        piecePosition = PosToXY(rawInput[1])
        whitePieces[piecePosition] = rawInput[0]

    f.close()

    return rows, cols, whitePieces, blackPieces


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
    whitePieces, blackPieces = {}, {}
    for piecePos in gameboard:
        if gameboard[piecePos][1] == "White":
            whitePieces[piecePos] = gameboard[piecePos][0]
        else:
            blackPieces[piecePos] = gameboard[piecePos][0]
    state = State(5, 5, whitePieces, blackPieces, "White")
    move = (None, None)
    maxValue = float("-inf")
    for possibleState in state.possibleNewStates():
        newAlpha = ab(10, possibleState, float("-inf"), float("inf"))
        if newAlpha > maxValue:
            maxValue = newAlpha
            move = possibleState
    return move #Format to be returned (('a', 0), ('b', 3))


rows, cols, whitePieces, blackPieces = parser(sys.argv[1])
combinedGameboard = {}
for whitePiecePos in whitePieces:
    combinedGameboard[whitePiecePos] = (whitePieces[whitePiecePos], "White")
for blackPiecePos in blackPieces:
    combinedGameboard[blackPiecePos] = (blackPieces[blackPiecePos], "Black")
print(studentAgent(combinedGameboard))