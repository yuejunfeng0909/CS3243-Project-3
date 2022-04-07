from random import randrange
import sys

class Piece:

    pieceTypes = ["King", "Queen", "Bishop", "Rook", "Knight", "Pawn"]

    movement = {"King": [(1, 1, 1), (1, 0, 1), (1, -1, 1), (0, -1, 1), (-1, -1, 1), (-1, 0, 1), (-1, 1, 1), (0, 1, 1)],
                "Rook": [(1, 0, 0), (0, -1, 0), (-1, 0, 0), (0, 1, 0)],
                "Bishop": [(1, 1, 0), (1, -1, 0), (-1, -1, 0), (-1, 1, 0)],
                "Queen": [(1, 0, 0), (0, -1, 0), (-1, 0, 0), (0, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0), (-1, 1, 0)],
                "Knight": [(2, 1, 1), (2, -1, 1), (1, 2, 1), (1, -2, 1), (-2, 1, 1), (-2, -1, 1), (-1, 2, 1), (-1, -2, 1)],
                "Pawn": [],
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
    
    def movePiece(self, agent:int, x:int, y:int, target_x:int, target_y:int) -> None:
        pieceType = self.piecesPos[agent].pop((x, y))
        self.piecesPos[agent][(target_x, target_y)]= pieceType
        self.lastMove = ((x, y), (target_x, target_y))

        # remove eaten piece.
        self.piecesPos[1-agent].pop((target_x, target_y), None)

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

    def __pawnVerticalMovesToDirection(self, y_change: int): 
        new_pos = self.moveToDirection(0, y_change)
        if (not self.board.isWithinBoard(new_pos[0], new_pos[1])) or \
                self.board.isBlockedByOwn(new_pos[0], new_pos[1], self.agent) or \
                self.board.isBlockedByOpponent(new_pos[0], new_pos[1], self.agent): 
            return []
        return [new_pos]

    def __pawnDiagnalMovesToDirection(self, x_change: int, y_change: int): 
        new_pos = self.moveToDirection(x_change, y_change)
        if (not self.board.isWithinBoard(new_pos[0], new_pos[1])) or self.board.isBlockedByOwn(new_pos[0], new_pos[1], self.agent): 
            return []
        if self.board.isBlockedByOpponent(new_pos[0], new_pos[1], self.agent):
            return [new_pos]
        return []

    def getAllPossibleNewPos(self): 
        steps = []
        for movement in self.movements: 
            xChange, yChange, maxSteps = movement 
            steps.extend(self.__getAllPossibleMovesToDirection(xChange, yChange, maxSteps)) 
        

        if self.pieceType == "Pawn":
            if self.agent == 0:
                steps.extend(self.__pawnVerticalMovesToDirection(1))
                steps.extend(self.__pawnDiagnalMovesToDirection(1, 1))
                steps.extend(self.__pawnDiagnalMovesToDirection(-1, 1))
            else:
                steps.extend(self.__pawnVerticalMovesToDirection(-1))
                steps.extend(self.__pawnDiagnalMovesToDirection(1, -1))
                steps.extend(self.__pawnDiagnalMovesToDirection(-1, -1))
        
        return steps

class State:

    def __init__(self, rows: int, cols:int, whitePieces:dict, blackPieces:dict, currentAgent:int) -> None:
        self.board = Board(cols, rows, blackPieces, whitePieces)
        self.rows = rows
        self.cols = cols
        self.currentAgent = currentAgent

    def possibleMoves(self):
        # for all pieces of the current agent, list down all the possible movements that can be made by each pieces

        possibleMoves = []
        agentOfNewState = 1-self.currentAgent
        # get king piece position
        opponentPos = self.board.piecesPos[agentOfNewState]
        foundKing = False
        for pos in opponentPos:
            if opponentPos[pos] == "King":
                kingPos = pos
                foundKing = True
                break
        if not foundKing:
            return []

        # pioritize the pieces that are closer to the King piece
        ownPiecePosOrderedByDistance = sorted(self.board.piecesPos[self.currentAgent].keys(), key=lambda x: abs(x[0]-kingPos[0])+abs(x[1]-kingPos[1]))

        for piecePos in ownPiecePosOrderedByDistance:
            movementModel = pieceMovementModel(self.board, piecePos[0], piecePos[1], self.board.piecesPos[self.currentAgent][piecePos], self.currentAgent)
            
            for newPos in movementModel.getAllPossibleNewPos():
                possibleMoves.append((piecePos, newPos))

        return possibleMoves
    
    def possibleMovesToStates(self, moves):
        # for all possible moves, list down all the possible new states
        possibleNewStates = []
        agentOfNewState = 1-self.currentAgent
        for move in moves:
            newState = State(self.rows, self.cols, self.board.piecesPos[0].copy(), self.board.piecesPos[1].copy(), agentOfNewState)
            newState.board.movePiece(self.currentAgent, move[0][0], move[0][1], move[1][0], move[1][1])
            possibleNewStates.append(newState)
        return possibleNewStates


    def isTerminalState(self) -> bool:
        return "King" not in self.board.piecesPos[0].values() or "King" not in self.board.piecesPos[1].values()


def letterToX(character) -> int:
    return ord(character) - ord('a')

def PosToXY(pos) -> tuple:
    return (letterToX(pos[0]), int(pos[1]))

def XYtoPos(xy: tuple) -> tuple:
    xCharVal: int = xy[0]+ord('a')
    return (chr(xCharVal), xy[1])

def ab(depth: int, state: State, alpha: float, beta: float):

    if depth == 0 or state.isTerminalState():
        # return utility
        whitePiecesCount = [0,]*len(Piece.pieceTypes)
        blackPiecesCount = [0,]*len(Piece.pieceTypes)

        for whitePiece in state.board.piecesPos[0]:
            indexOfPieceType = Piece.pieceTypes.index(state.board.piecesPos[0][whitePiece])
            whitePiecesCount[indexOfPieceType] += 1
        for blackPiece in state.board.piecesPos[1]:
            indexOfPieceType = Piece.pieceTypes.index(state.board.piecesPos[1][blackPiece])
            blackPiecesCount[indexOfPieceType] += 1

        # pieceTypes = ["King", "Queen", "Bishop", "Rook", "Knight", "Pawn"]
        pieceWeights = [1000, 5, 4, 4, 3, 2]
        materialScore = sum([pieceWeights[i] * (whitePiecesCount[i] - blackPiecesCount[i]) for i in range(len(Piece.pieceTypes))])

        state.currentAgent = 0
        wMobility = len(state.possibleMoves())
        state.currentAgent = 0
        bMobility = len(state.possibleMoves())
        mobilityScore = 5 * (wMobility-bMobility)

        return ((materialScore + mobilityScore) * (1 if state.currentAgent==0 else -1), state)

    if state.currentAgent == 0:
        value = float("-inf")
        possibleMoves = state.possibleMoves()
        for newMove in possibleMoves:
            newState = state.possibleMovesToStates([newMove])[0]
            abValue, _ = ab(depth - 1, newState, alpha, beta)
            if abValue > value:
                value = abValue
                bestState = newState
            if value >= beta:
                break
            alpha = max(alpha, value)
        return (value, bestState)
    else:
        value = float("inf")
        possibleMoves = state.possibleMoves()
        for newMove in possibleMoves:
            newState = state.possibleMovesToStates([newMove])[0]
            abValue, _ = ab(depth - 1, newState, alpha, beta)
            if abValue < value:
                value = abValue
                bestState = newState
            if value <= alpha:
                break
            alpha = min(alpha, value)
        return (value, bestState)

# def parser(testfile):
#     f = open(testfile, "r")

#     def input():
#         line = f.readline().strip("\n")
#         return line

#     rows = int(input().split(":")[1])
#     cols = int(input().split(":")[1])

#     blackPieces={}
#     # Number of black pieces
#     numOfEachBlackPiece = input().split(":")[1].split(" ")
#     numOfEachBlackPiece = [int(x) for x in numOfEachBlackPiece]
#     input() # ignore line "Position of Enemy Pieces:"
#     for _ in range(sum(numOfEachBlackPiece)):
#         rawInput = input()[1:-1].split(",")
#         piecePosition = PosToXY(rawInput[1])
#         blackPieces[piecePosition] = rawInput[0]

#     whitePieces = {}
#     # Number of white pieces
#     numOfEachWhitePiece = input().split(":")[1].split(" ")
#     numOfEachWhitePiece = [int(x) for x in numOfEachWhitePiece]
#     input() # ignore line "Position of Own Pieces:"
#     for _ in range(sum(numOfEachWhitePiece)):
#         rawInput = input()[1:-1].split(",")
#         piecePosition = PosToXY(rawInput[1])
#         whitePieces[piecePosition] = rawInput[0]

#     f.close()

#     return rows, cols, whitePieces, blackPieces


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
        convertedPos = PosToXY(piecePos)
        if gameboard[piecePos][1] == "White":
            whitePieces[convertedPos] = gameboard[piecePos][0]
        else:
            blackPieces[convertedPos] = gameboard[piecePos][0]
    state = State(5, 5, whitePieces, blackPieces, 0)
    move = ab(2, state, float("-inf"), float("inf"))[1].board.lastMove
    move = (XYtoPos(move[0]), XYtoPos(move[1]))
    return move #Format to be returned (('a', 0), ('b', 3))

# def dummyAgent(gameboard):
#     whitePieces, blackPieces = {}, {}
#     for piecePos in gameboard:
#         convertedPos = PosToXY(piecePos)
#         if gameboard[piecePos][1] == "White":
#             whitePieces[convertedPos] = gameboard[piecePos][0]
#         else:
#             blackPieces[convertedPos] = gameboard[piecePos][0]
#     state = State(5, 5, whitePieces, blackPieces, 1)
#     possibleMove = state.possibleMoves()[0]
#     possibleState = state.possibleMovesToStates([possibleMove])[0]

#     move = possibleState.board.lastMove
#     move = (XYtoPos(move[0]), XYtoPos(move[1]))
    
#     return move #Format to be returned (('a', 0), ('b', 3))

# def randomAgent(gameboard):
#     whitePieces, blackPieces = {}, {}
#     for piecePos in gameboard:
#         convertedPos = PosToXY(piecePos)
#         if gameboard[piecePos][1] == "White":
#             whitePieces[convertedPos] = gameboard[piecePos][0]
#         else:
#             blackPieces[convertedPos] = gameboard[piecePos][0]
#     state = State(5, 5, whitePieces, blackPieces, 1)
    
#     possibleMoves = state.possibleMoves()
#     selectedMove = possibleMoves[randrange(0, len(possibleMoves))]
#     selectedState = state.possibleMovesToStates([selectedMove])[0]
    

#     move = selectedState.board.lastMove
#     move = (XYtoPos(move[0]), XYtoPos(move[1]))
    
#     return move #Format to be returned (('a', 0), ('b', 3))

# def minimaxAgent(gameboard):
#     whitePieces, blackPieces = {}, {}
#     for piecePos in gameboard:
#         convertedPos = PosToXY(piecePos)
#         if gameboard[piecePos][1] == "White":
#             whitePieces[convertedPos] = gameboard[piecePos][0]
#         else:
#             blackPieces[convertedPos] = gameboard[piecePos][0]
#     state = State(5, 5, whitePieces, blackPieces, 1)
#     move = ab(4, state, float("-inf"), float("inf"))[1].board.lastMove
#     move = (XYtoPos(move[0]), XYtoPos(move[1]))
#     return move #Format to be returned (('a', 0), ('b', 3))

# rows, cols, whitePieces, blackPieces = parser(sys.argv[1])
# combinedGameboard = {}
# for whitePiecePos in whitePieces:
#     combinedGameboard[XYtoPos(whitePiecePos)] = (whitePieces[whitePiecePos], "White")
# for blackPiecePos in blackPieces:
#     combinedGameboard[XYtoPos(blackPiecePos)] = (blackPieces[blackPiecePos], "Black")
# initialState = State(rows, cols, whitePieces, blackPieces, 0)

# def game(depth:int, studentAgentTurn:bool, gameboard: dict, gameState: State):
#     if depth == 0:
#         print("Draw")
#         return

#     if studentAgentTurn:
#         move = studentAgent(gameboard)
#     else:
#         move = minimaxAgent(gameboard)
    
#     print("current depth:", depth)
#     print("White pieces:", gameState.board.piecesPos[0])
#     print("Black pieces:", gameState.board.piecesPos[1])
#     print("Student" if studentAgentTurn else "Enemy", "selected move is:", move, "for", gameboard[move[0]][0])
#     print("")

#     gameState.board.movePiece(0 if studentAgentTurn else 1, letterToX(move[0][0]), move[0][1], letterToX(move[1][0]), move[1][1])

#     gameboard[move[1]] = gameboard[move[0]]
#     gameboard.pop(move[0])

#     if gameState.isTerminalState():
#         print("Student agent won" if studentAgentTurn else "Enemy agent won")
#     else:
#         game(depth-1, not studentAgentTurn, gameboard, gameState)

# game(100, True, combinedGameboard, initialState)