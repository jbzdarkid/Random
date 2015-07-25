tetrominos = {
  ('I', 0):
    [[1, 1, 1, 1]],
  ('I', 1):
    [[1],
     [1],
     [1],
     [1]],
#----------------------------
  ('J', 0):
    [[0, 1],
     [0, 1],
     [1, 1]],
  ('J', 1):
    [[1, 0, 0],
     [1, 1, 1]],
  ('J', 2):
    [[1, 1],
     [1, 0],
     [1, 0]],
  ('J', 3):
    [[1, 1, 1],
     [0, 0, 1]],
#----------------------------
  ('L', 0):
    [[1, 0],
     [1, 0],
     [1, 1]],
  ('L', 1):
    [[1, 1, 1],
     [1, 0, 0]],
  ('L', 2):
    [[1, 1],
     [0, 1],
     [0, 1]],
  ('L', 3):
    [[0, 0, 1],
     [1, 1, 1]],
#----------------------------
  ('O', 0):
    [[1, 1],
     [1, 1]],
#----------------------------
  ('S', 0):
    [[0, 1, 1],
     [1, 1, 0]],
  ('S', 1):
    [[1, 0],
     [1, 1],
     [0, 1]],
#----------------------------
  ('T', 0):
    [[1, 1, 1],
     [0, 1, 0]],
  ('T', 1):
    [[0, 1],
     [1, 1],
     [0, 1]],
  ('T', 2):
    [[0, 1, 0],
     [1, 1, 1]],
  ('T', 3):
    [[1, 0],
     [1, 1],
     [1, 0]],
#----------------------------
  ('Z', 0):
    [[1, 1, 0],
     [0, 1, 1]],
  ('Z', 1):
    [[0, 1],
     [1, 1],
     [1, 0]],
}

def doubleIter(xmax, ymax):
  for x in range(xmax):
    for y in range(ymax):
      yield (x, y)

import threading
class PartialSolution(threading.Thread):
  def __init__(self, root=None):
    if root != None:
      self.board, self.solMap, self.challenge, self.cost = root
      return
    super(PartialSolution, self).__init__()
  
  def debug(self):
    print
    print 'Board:', self.board
    for line in self.board:
      print line
    print 'Cost:', self.cost
    print 'Solution:', self.solMap
    print 'Challenge:', self.challenge

  def clone(self):
    return PartialSolution(root=(
      copy.deepcopy(self.board),
      copy.copy(self.solMap), # 1-depth dict
      copy.copy(self.challenge), # 1d array
      self.cost
      ))

  def run(self): # Possibly implement T-tetromino parity
    while True:
      try:
        self = q.get(True, 1)
      except Queue.Empty:
        return
      global maxCost
      if self.cost > maxCost:
        q.task_done()
        continue
      if len(self.challenge) == 0:
        global solutions
        lock.acquire()
        if self.cost < maxCost:
          maxCost = self.cost
          solutions = []
        lock.release()
        solutions.append(self)
        q.task_done()
        continue
      
      pieceName, initialRotation = self.challenge.pop()
      if pieceName in 'O':
        rotations = 1
      elif pieceName in 'ISZ':
        rotations = 2
      elif pieceName in 'JLT':
        rotations = 4
      
      for rotation in range(rotations):
        piece = tetrominos[(pieceName, (initialRotation+rotation) % rotations)]
        invalidSquares = copy.deepcopy(self.board)
        for x, y in doubleIter(board_x-len(piece)+1, board_y-len(piece[0])+1):
          newStep = self.clone()
          invalidPlacement = False
          for i, j in doubleIter(len(piece), len(piece[0])):
            if invalidSquares[x+i][y+j] + piece[i][j] == 2: # The square is invalid and there is a part of the tetromino there
              for k in range(i+1):
                if x+i+k > board_x-1:
                  continue
                for l in range(j+1):
                  if y+j+l > board_y-1:
                    continue
                  if piece[k][l] == 1: # A potential future collision
                    invalidSquares[x+i+k][y+j+l] = 1 # The root square where it would occur
              invalidPlacement = True
              break
            if newStep.board[x+i][y+j] == 0: # On the assumption that the piece fits, update the new board.
              newStep.board[x+i][y+j] = piece[i][j]
          if not invalidPlacement:
            newStep.solMap[len(self.challenge)] = [x, y, rotation]
            newStep.cost += rotation
            q.put(newStep)
      q.task_done()


board_x = 3
board_y = 4
challenge = [('J', 1), ('Z', 0), ('L', 2)]
'''Only solution with cost 0:
ZZLL
JZZL
JJJL
'''

global maxCost
maxCost = len(challenge)*3 # At worst, all pieces have 4 rotations and are rotated 3 times.
global solutions
solutions = []
import copy
import Queue
q = Queue.Queue()
lock = threading.Lock()
board = [[0 for _ in range(board_y)] for __ in range(board_x)]

q.put(PartialSolution(root=(board, {}, list(challenge), 0)))
threads = []
for _ in range(8):
  threads.append(PartialSolution())
  threads[-1].start()
q.join()
print 'Challenge:', challenge
print 'Solutions at cost', maxCost
for solution in solutions:
  print solution.solMap