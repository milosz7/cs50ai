"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy
import random
import time

X = "X"
O = "O"
EMPTY = None
BOARD_DIM = 3
X_WIN = 1
O_WIN = -1
DRAW = 0


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
    x_amt = 0
    o_amt = 0
    for row in board:
        x_amt += row.count(X)
        o_amt += row.count(O)
    if x_amt == o_amt:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i in range(BOARD_DIM):
        for j in range(BOARD_DIM):
            if board[i][j] is EMPTY:
                actions.add((i, j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    if board[i][j] is not EMPTY:
        raise Exception("This move is illegal!")
    player_symbol = player(board)
    board_copy = deepcopy(board)
    board_copy[i][j] = player_symbol
    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    states = []

    diag1 = set()
    diag2 = set()
    
    for i in range(BOARD_DIM):
        col_unique = set()
        row_unique = set()
        diag1.add(board[i][i])
        diag2.add(board[i][2 - i])
        for j in range(BOARD_DIM):
            row_unique.add(board[i][j])
            col_unique.add(board[j][i])
        states.append(col_unique)
        states.append(row_unique)

    states.append(diag1)
    states.append(diag2)

    for unique in [list(state)[0] for state in states if len(state) == 1]:
        if unique == X:
            return X
        if unique == O:
            return O
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    empty_count = 0
    is_win = winner(board)
    for row in board:
        empty_count += row.count(EMPTY)
    if empty_count == 0 or is_win is not None:
        return True
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    is_win = winner(board)
    if is_win == X:
        return X_WIN
    if is_win == O:
        return O_WIN
    return DRAW


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    acts = list(actions(board))
    current_player = player(board)
    if current_player == X:
        ratings = [-1] * len(acts)
    if current_player == O:
        ratings = [1] * len(acts)
    for i in range(len(acts)):
        if current_player == X:
            ratings[i] = min_value(result(board, acts[i]))
            if ratings[i] > min(ratings):
                return acts[i]
        if current_player == O:
            ratings[i] = max_value(result(board, acts[i]))
            if ratings[i] < max(ratings):
                return acts[i]
    # return last action left if there is nothing to compare
    return acts[0]
    
def max_value(board):
    if terminal(board):
        return utility(board)
    v = -math.inf
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v

def min_value(board):
    if terminal(board):
        return utility(board)
    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v
