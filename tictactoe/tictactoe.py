"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count = 0
    for i in range(3):
        for j in range(3):
            if not board[i][j] == EMPTY:
                count+=1
        
    if count%2 == 0:
        return X
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possibleMoves = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possibleMoves.add((i,j))
    return possibleMoves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    newBoard = copy.deepcopy(board)
    
    possibleMoves = actions(board)

    if action not in possibleMoves:
        raise Exception
    
    if player(newBoard) == X:
        newBoard[action[0]][action[1]] = X
    elif player(newBoard) == O:
        newBoard[action[0]][action[1]] = O
    
    return newBoard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #top horizontal
    if board[0][0] == board[0][1] == board[0][2]:
        return board[0][0]
    #middle horizontal
    elif board[1][0] == board[1][1] == board[1][2]:
        return board[1][0]
    #bottom horizontal
    elif board[2][0] == board[2][1] == board[2][2]:
        return board[2][0]
    #left vertical
    elif board[0][0] == board[1][0] == board[2][0]:
        return board[0][0]
    #middle vertical
    elif board[0][1] == board[1][1] == board[2][1]:
        return board[0][1]
    #right vertical
    elif board[0][2] == board[1][2] == board[2][2]:
        return board[0][2]
    #left-right diag
    elif board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    #right-left diag
    elif board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    elif len(actions(board)) == 0:
        return True
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if not utility(board) == 0:
        return None

    possibleMoves = actions(board)
    mover = player(board)
    

    if mover == 'X':
        scores = []
        for move in possibleMoves:
            scores.append([move,minValue(result(board,move))])

        maxIndex = -1
        maxScore = -2

        for i in range(len(scores)):
            if scores[i][1]>=maxScore:
                maxScore = scores[i][1]
                maxIndex = i
        
        return scores[maxIndex][0]
    
    else:
        scores = []
        for move in possibleMoves:
            scores.append([move,maxValue(result(board,move))])

        minIndex = -1
        minScore = 2

        for i in range(len(scores)):
            if scores[i][1]<=minScore:
                minScore = scores[i][1]
                minIndex = i
        
        return scores[minIndex][0]
    
def maxValue(board):
    val = -2
    if terminal(board):
        return utility(board)
    for action in actions(board):
        val = max(val,minValue(result(board,action)))
    return val

def minValue(board):
    val = 2
    if terminal(board):
        return utility(board)
    for action in actions(board):
        val = min(val, maxValue(result(board,action)))
    return val