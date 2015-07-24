tetrominos = {
    'I1':   [[1, 1, 1, 1]],
    'I2':   [[1],
             [1],
             [1],
             [1]],
#----------------------------
    'J1':   [[0, 1],
             [0, 1],
             [1, 1]],
    'J2':   [[1, 0, 0],
             [1, 1, 1]],
    'J3':   [[1, 1],
             [1, 0],
             [1, 0]],
    'J4':   [[1, 1, 1],
             [0, 0, 1]],
#----------------------------
    'L1':   [[1, 0],
             [1, 0],
             [1, 1]],
    'L2':   [[1, 1, 1],
             [1, 0, 0]],
    'L3':   [[1, 1],
             [0, 1],
             [0, 1]],
    'L4':   [[0, 0, 1],
             [1, 1, 1]],
#----------------------------
    'O':    [[1, 1],
             [1, 1]],
#----------------------------
    'S1':   [[0, 1, 1],
             [1, 1, 0]],
    'S2':   [[1, 0],
             [1, 1],
             [0, 1]],
#----------------------------
    'T1':   [[1, 1, 1],
             [0, 1, 0]],
    'T2':   [[0, 1],
             [1, 1],
             [0, 1]],
    'T3':   [[0, 1, 0],
             [1, 1, 1]],
    'T4':   [[1, 0],
             [1, 1],
             [1, 0]],
#----------------------------
    'Z1':   [[1, 1, 0],
             [0, 1, 1]],
    'Z2':   [[0, 1],
             [1, 1],
             [1, 0]],
}

class PartialSolution():
    def __init__(self, board, solMap, challenge, cost):
        self.board = board
        self.solMap = solMap
        self.challenge = challenge
        self.cost = cost
    def place(self, piece, x, y):
        newStep = PartialSolution(board, solMap, challenge, cost)
        for i in range(len(piece)):
            for j in range(len(piece[i])):
                if board[x][y] and piece[i][j]:
                    return False
                
        return True

board_x = 4
board_y = 3
challenge = ['J2', 'Z1', 'L3']
''' Solution with cost 0:
ZZLL
JZZL
JJJL
'''

import Queue
q = Queue.Queue()
board = [[0 for _ in range(board_x)] for __ in range(board_y)]
print board
q.put(PartialSolution(board, {}, challenge, 0))
while not q.empty():
    step = q.get()
    piece = tetrominos[step.challenge.pop()]
    for x in range(len(board[0])-len(piece[0])):
        for y in range(len(board)-len(piece)):
            if step.place(piece, x, y):
                solMap[len(challenge)] = [x, y]
                q.put(PartialSolution())
