import sys
import itertools

class Piece:

    pieceTypes = ["King", "Queen", "Bishop", "Rook", "Knight", "whitePawn", "blackPawn"]

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

    def isBlockedByOpponent(self, x:int, y:int, currentAgent:str):
        agentIndex = 0 if currentAgent == "White" else 1
        if (x, y) in self.piecesPos[1-agentIndex]:
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

    def __getAllPossibleMovementToDirection(self, x_change: int, y_change: int, max_steps=0): 
        '''Get all the positions that the piece can move to, including position that are being threatened by other pieces''' 
        if max_steps == 0: 
            max_steps = max(self.board.board_size_x, self.board.board_size_y) 
          
        steps = [] 
        for i in range(max_steps): 
            new_pos = self.moveToDirection((i+1) * x_change, (i+1) * y_change) 
            if (not self.board.isWithinBoard(new_pos[0], new_pos[1])) or self.board.isBlocked(new_pos[0], new_pos[1]): 
                break 
            steps.append(new_pos) 
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
            steps.extend(self.__getAllPossibleMovementToDirection(xChange, yChange, maxSteps)) 
        return steps
    
    def getAllPossibleThreaten(self): 
        if self.pieceType == "Pawn":
            if self.agent == 0:
                self.movements = [(1, 0, 1), (1, 1, 1), (1, -1, 1)]
            else:
                self.movements = [(-1, 0, 1), (-1, 1, 1), (-1, -1, 1)]
        
        steps = []
        for movement in self.movements: 
            xChange, yChange, maxSteps = movement 
            steps.extend(self.__getAllPossibleMovementToDirection(xChange, yChange, maxSteps)) 
        return steps

class State:

    def __init__(self, rows: int, cols:int, whitePieces:dict, blackPieces:dict) -> None:
        self.board = Board(cols, rows, blackPieces, whitePieces)
        self.rows = rows
        self.cols = cols
    
    def setAgent(self, agent: str):
        self.currentAgent = agent

    def changeAgent(self):
        self.currentAgent = "Black" if self.currentAgent=="White" else "White"

    def possibleNewStates(self):
        # for all pieces of the current agent, list down all the possible movements that can be made by each pieces

        agentIndex = 0 if self.currentAgent == "White" else 1

        # First calculate the region threatened by the other players, to avoid.
        threatened = {}
        for piecePos in self.board.piecesPos[1-agentIndex]:
            movementModel = pieceMovementModel(self.board, piecePos[0], piecePos[1], self.board.piecesPos[agentIndex][piecePos], 1-agentIndex)
            for threatenedPos in movementModel.getAllPossibleThreaten():
                threatened[threatenedPos] = True

        # Then add all the possible movements from the current 
        possibleMovements = []
        for piecePos in self.board.piecesPos[agentIndex]:
            movementModel = pieceMovementModel(self.board, piecePos[0], piecePos[1], self.board.piecesPos[agentIndex][piecePos], agentIndex)
            for newPos in movementModel.getAllPossibleNewPos():
                if newPos in threatened:
                    continue
                newState = State(self.rows, self.cols, self.board.piecesPos[0], self.board.piecesPos[1])
                newState.board.movePiece(self.currentAgent, piecePos[0], piecePos[1], newPos[0], newPos[1])
                possibleMovements.append(newState)

        return possibleMovements

    def isTerminalState(self) -> bool:
        return "King" not in self.board.piecesPos[0].values() or "King" not in self.board.piecesPos[1].values()


def letterToX(character) -> int:
    return ord(character) - ord('a')

def PosToXY(pos) -> tuple:
    return (letterToX(pos[0]), int(pos[1:]))

def XYtoPos(xy: tuple) -> tuple:
    xCharVal: int = xy[0]+ord('a')
    return (chr(xCharVal), xy[1])

def ab(depth: int, agent: str, state: State, alpha: int, beta: int):
    # each ab state has current agent, moves, a copy of white and black pieces position, current movement
    
    
    if depth == 0 or state.isTerminalState():
        # return utility
        # utility = number of white - black
        return len(state.board.piecesPos[0]) - len(state.board.piecesPos[1])

    if agent == "White":
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

    # Number of black pieces
    numOfEachBlackPiece = input().split(":")[1].split(" ")
    numOfEachBlackPiece = [int(x) for x in numOfEachBlackPiece]
    

    # positions of black pieces
    # for _ in range()


    # Number of white pieces
    numOfEachWhitePiece = input().split(":")[1].split(" ")
    numOfEachWhitePiece = [int(x) for x in numOfEachWhitePiece]
    
    
    # positions of white pieces

    f.close()

    # csp = State(rows, cols, listOfObstacles, numOfEachEnemies)
    return csp
    


### DO NOT EDIT/REMOVE THE FUNCTION HEADER BELOW###
# To return: Goal State which is a dictionary containing a mapping of the position of the grid to the chess piece type.
# Chess Pieces: King, Queen, Knight, Bishop, Rook (First letter capitalized)
# Positions: Tuple. (column (String format), row (Int)). Example: ('a', 0)

# Goal State to return example: {('a', 0) : Queen, ('d', 10) : Knight, ('g', 25) : Rook}
def run_CSP():
    # You can code in here but you cannot remove this function or change the return type
    testfile = sys.argv[1] #Do not remove. This is your input testfile.
    rawResult = search(testfile)

    goalState = {}
    for pos in rawResult:
        goalState[XYtoPos(pos)] = rawResult[pos]
    
    return goalState #Format to be returned

# from time import time 
# startTime = time() 
# print(run_CSP()) 
# print(time() - startTime) 
 
# import profile 
# profile.run("run_CSP()")
# run_CSP()