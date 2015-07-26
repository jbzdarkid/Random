tetrominos = {
  ('I', 0):
  [[1],
   [1],
   [1],
   [1]],
  ('I', 1):
    [[1, 1, 1, 1]],
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
global uuid
uuid = 0
global uuidlock
uuidlock = threading.Lock()
def getUUID():
  global uuid
  uuidlock.acquire()
  uuid += 1
  newId = uuid
  uuidlock.release()
  return newId

class PartialSolution(threading.Thread):
  def __init__(self, root=None):
    if root != None:
      self.board, self.challenge, self.cost, self.uuid = root
      return
    super(PartialSolution, self).__init__()
  
  def debug(self):
    print 'UUID:', self.uuid
    print 'Board:'
    for line in self.board:
      out = '['
      for val in line:
        if val != -1:
          out += ' '
        out += str(val)
        out += ' '
      out += ']'
      print out
    print 'Cost:', self.cost
    print 'Challenge:', self.challenge

  def clone(self):
    return PartialSolution(root=(
      copy.deepcopy(self.board),
      list(self.challenge),
      self.cost,
      getUUID()
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
      global solutions
      if len(self.challenge) == 0:
        lock.acquire()
        if self.cost < maxCost:
          print 'Reduced max cost from', maxCost, 'to', self.cost
          maxCost = self.cost
          solutions = []
        if len(solutions) < MAXSOLNS:
          solutions.append(self)
        lock.release()
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
        for x, y in doubleIter(len(board)-len(piece)+1, len(board[0])-len(piece[0])+1):
          newStep = self.clone()
          invalidPlacement = False
          for i, j in doubleIter(len(piece), len(piece[0])):
            if invalidSquares[x+i][y+j] != -1 and piece[i][j] == 1:
              for k in range(1, i+1):
                if x+i+k >= len(board):
                  continue
                for l in range(1, j+1):
                  if y+j+l >= len(board[0]):
                    continue
                  if piece[k][l] == 1: # A potential future collision
                    invalidSquares[x+i+k][y+j+l] = 0 # The root square where it would occur
              invalidPlacement = True
              break
            if newStep.board[x+i][y+j] == -1 and piece[i][j] == 1: # On the assumption that the piece fits, update the new board.
              newStep.board[x+i][y+j] = len(self.challenge)
          if not invalidPlacement:
            newStep.cost += rotation
            q.put(newStep)
      q.task_done()

challenges = {
  # 'Name': ['Pieces', Height, Width, Best],
  # 'Connector':  ['T0, T0, L1', 3, 4, 3], # Tied
  # 'A':          ['I1, L1, J1, Z0', 4, 4, 1], # Better
  # 'Cube':       ['T0, T0, L1, Z0', 4, 4, 4], # Tied
  # 'Floor 1':    ['L1, Z0, L1, Z0', 4, 4, 4], # Tied
  # 'Fan':        ['T0, T0, L1, S0, Z0', 5, 4, 5], # Tied
  # 'Recorder':   ['T0, T0, J1, S0, Z0', 5, 4, 3], # Better
  # 'B':          ['I1, T0, T0, L1, Z0', 5, 4, 4], # Tied
  # 'C':          ['T0, T0, J1, J1, L1, Z0', 6, 4, 2], # Better
  # 'Platform':   ['I1, S0, T0, T0, L1, Z0', 6, 4, 5], # Tied
  'Floor 2':    ['O0, T0, T0, T0, T0, L1, L1, L1, L1', 6, 6, 10], # Better
  # 'Floor 6':    ['O0, S0, S0, S0, S0, L0, L0, L0, L0', 6, 6, 8], #
  # 'A star':     ['T0, T0, T0, T0, L1, J1, S0, S0, Z0, Z0', 5, 8, 10], #
  # 'B star':     ['I1, I1, O0, T0, T0, T0, T0, L1, L1, J1', 5, 8, 8], #
  # 'C star':     ['L1, J1, S0, Z0, T0, T0, I1, I1, O0, O0', 5, 8, 8], #
  # 'Floor 3':    ['I1, I1, I1, I1, J1, J1, L1, L1, S0, Z0', 5, 8, 4], #
  # 'Floor 4':    ['O0, O0, T0, T0, T0, T0, J1, L1, S0, S0, Z0, Z0', 8, 6, 10], #
  # 'Floor 5':    ['I1, I1, O0, O0, O0, O0, T0, T0, T0, T0, J1, L1, S0, Z0', 7, 8, 10], #
}

NUMTHREADS = 8
MAXSOLNS = 0 # Set to -1 for all solutions. Set to 0 to calculate only maxcost value.
import copy
import Queue
q = Queue.LifoQueue() # A depth-first search performs better than breadth-first when using a max cost, since once we find a solution, we can discard bad ones. Thus, we try to find a solution as early as possible.
lock = threading.Lock()
for title in challenges.keys():
  data = challenges[title]
  board = [[-1 for _ in range(data[2])] for __ in range(data[1])]
  pieces = data[0].split(', ')
  for i in range(len(pieces)):
    pieces[i] = (pieces[i][0], int(pieces[i][1]))
  global maxCost
  maxCost = data[3]
  global solutions
  solutions = []
  
  q.put(PartialSolution(root=(board, list(pieces), 0, 0)))
  for _ in range(NUMTHREADS):
    PartialSolution().start()
  q.join()
  print 'Challenge "{name}" using {pieces}'.format(name=title, pieces=pieces)
  print '{num} solution{s} at cost {cost}:'.format(num=len(solutions), s=('s' if len(solutions) != 1 else ''), cost=maxCost)
  for solution in solutions:
    for line in solution.board:
      print line
    print