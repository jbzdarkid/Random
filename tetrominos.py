tetrominos = {
  ('I', 0):
    (0,
    [[1],
     [1],
     [1],
     [1]]),
  ('I', 1):
    (0,
    [[1, 1, 1, 1]]),
  ('I', 2): ('!', 'Invalid'),
  ('I', 3): ('!', 'Invalid'),
#----------------------------
  ('J', 0):
    (1,
    [[0, 1],
     [0, 1],
     [1, 1]]),
  ('J', 1):
    (0,
    [[1, 0, 0],
     [1, 1, 1]]),
  ('J', 2):
    (0,
    [[1, 1],
     [1, 0],
     [1, 0]]),
  ('J', 3):
    (0,
    [[1, 1, 1],
     [0, 0, 1]]),
#----------------------------
  ('L', 0):
    (0,
    [[1, 0],
     [1, 0],
     [1, 1]]),
  ('L', 1):
    (0,
    [[1, 1, 1],
     [1, 0, 0]]),
  ('L', 2):
    (0,
    [[1, 1],
     [0, 1],
     [0, 1]]),
  ('L', 3):
    (2,
    [[0, 0, 1],
     [1, 1, 1]]),
#----------------------------
  ('O', 0):
    (0,
    [[1, 1],
     [1, 1]]),
  ('O', 1): ('!', 'Invalid'),
  ('O', 2): ('!', 'Invalid'),
  ('O', 3): ('!', 'Invalid'),
#----------------------------
  ('S', 0):
    (1,
    [[0, 1, 1],
     [1, 1, 0]]),
  ('S', 1):
    (0,
    [[1, 0],
     [1, 1],
     [0, 1]]),
  ('S', 2): ('!', 'Invalid'),
  ('S', 3): ('!', 'Invalid'),
#----------------------------
  ('T', 0):
    (0,
    [[1, 1, 1],
     [0, 1, 0]]),
  ('T', 1):
    (1,
    [[0, 1],
     [1, 1],
     [0, 1]]),
  ('T', 2):
    (1,
    [[0, 1, 0],
     [1, 1, 1]]),
  ('T', 3):
    (0,
    [[1, 0],
     [1, 1],
     [1, 0]]),
#----------------------------
  ('Z', 0):
    (0,
    [[1, 1, 0],
     [0, 1, 1]]),
  ('Z', 1):
    (1,
    [[0, 1],
     [1, 1],
     [1, 0]]),
  ('Z', 2): ('!', 'Invalid'),
  ('Z', 3): ('!', 'Invalid'),
}

def doubleIter(xmax, ymax):
  for x in range(xmax):
    for y in range(ymax):
      yield (x, y)

import threading
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
      self.board, self.pieces, self.x, self.y, self.uuid = root
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
    print 'Pieces:', self.pieces
  
  def clone(self):
    return PartialSolution(root=(
      copy.deepcopy(self.board),
      list(self.pieces),
      self.x,
      self.y,
      self.uuid, # Will be changed later IF the new copy survives
      ))
  
  def isInvalid(self, x, y):
    return x < 0 or y < 0 or x >= len(self.board) or y >= len(self.board[0])
  
  def getBoard(self, x, y):
    return self.board[self.x][self.y]
  
  def run(self): # Possibly implement T-tetromino parity
    while True:
      try:
        _cost, self = q.get(True, 1)
        self.cost = _cost
      except Queue.Empty:
        return
      global maxCost
      if self.cost > maxCost and maxCost != -1:
        continue
      if self.pieces == [None] * len(self.pieces):
        global solutions
        if len(solutions) == 0:
          maxCost = self.cost
        if len(solutions) == MAXSOLNS:
          return
        solutions.append(self)
        if len(solutions) == MAXSOLNS: # Allows the -1/0 logic below.
          return
        q.task_done()
        continue
      
      # Locating the first available space
      for self.x, self.y in doubleIter(len(board), len(board[0])):
        if self.getBoard(self.x, self.y) != -1:
          continue
        break
      for rotation in range(0, 4):
        for pieceNum in range(len(self.pieces)):
          if self.pieces[pieceNum] == None:
            continue
          pieceName, initialRotation = self.pieces[pieceNum]
          offset, piece = tetrominos[(pieceName, (initialRotation+rotation) % 4)]
          if piece == 'Invalid': # For pieces like the O which cannot be rotated further
            continue
          # Handle T pairity
          newSolution = self.clone()
          invalidPlacement = False
          for i, j in doubleIter(len(piece), len(piece[0])):
            if piece[i][j] == 1:
              # Bounds check
              if self.isInvalid(self.x+i, self.y+j-offset):
                invalidPlacement = True
                break
              # Collision
              if self.board[self.x+i][self.y+j-offset] != -1:
                invalidPlacement = True
                break
              newSolution.board[self.x+i][self.y+j-offset] = pieceNum
          if invalidPlacement:
            continue
          # Check for 1-gaps on next row (and then coverings on the row below)
          newSolution.uuid = getUUID()
          newSolution.pieces[pieceNum] = None
          q.put((self.cost + rotation, newSolution))
      q.task_done()

challenges = {
  # 'Name': ['Pieces', Height, Width],
  'Connector':  ['T0, T0, L1', 3, 4], # Tied (3)
  'A':          ['I1, L1, J1, Z0', 4, 4], # Better (1)
  'Cube':       ['T0, T0, L1, Z0', 4, 4], # Better? (4)
  'Floor 1':    ['L1, Z0, L1, Z0', 4, 4], # Tied (4)
  'Recorder':   ['T0, T0, J1, S0, Z0', 5, 4], # ? (3)
  'Fan':        ['T0, T0, L1, S0, Z0', 5, 4], # Tied (4)
  'B':          ['I1, T0, T0, L1, Z0', 5, 4], # Tied (5)
  'C':          ['T0, T0, J1, J1, L1, Z0', 6, 4], # Better (2)
  'Platform':   ['I1, S0, T0, T0, L1, Z0', 6, 4], # Tied (5)
  'Test':       ['I0, J0, L0, O0, S0, S0, Z0', 7, 4],
  'Test 2':     ['I0, J0, L0, O0, S0, T0, T0, Z0', 8, 4],
  'Floor 6':    ['O0, S0, S0, S0, S0, L0, L0, L0, L0', 6, 6], # Tied (8)
  'Floor 2':    ['O0, T0, T0, T0, T0, L1, L1, L1, L1', 6, 6], # Better (7)
  'A star':     ['T0, T0, T0, T0, L1, J1, S0, S0, Z0, Z0', 5, 8], # Better (6)
  'B star':     ['I1, I1, O0, T0, T0, T0, T0, L1, L1, J1', 5, 8], # Better (3)
  'C star':     ['L1, J1, S0, Z0, T0, T0, I1, I1, O0, O0', 5, 8], # Better (2)
  'Floor 3':    ['I1, I1, I1, I1, J1, J1, L1, L1, S0, Z0', 5, 8], # Better (3)
  'Floor 4':    ['O0, O0, T0, T0, T0, T0, J1, L1, S0, S0, Z0, Z0', 8, 6], # Better (4)
  'Floor 5':    ['I1, I1, O0, O0, O0, O0, T0, T0, T0, T0, J1, L1, S0, Z0', 7, 8], # 10
}

NUMTHREADS = 16
MAXSOLNS = 1 # Set to -1 for all solutions. Set to 0 to calculate only cost.
import copy
import Queue
import time

lock = threading.Lock()
for title in challenges.keys():
  data = challenges[title]
  board = [[-1 for _ in range(data[2])] for __ in range(data[1])]
  pieces = data[0].split(', ')
  for i in range(len(pieces)):
    pieces[i] = (pieces[i][0], int(pieces[i][1]))
  global maxCost
  maxCost = -1
  global solutions
  solutions = []
  global uuid
  uuid = 0
  startTime = time.time()
  
  q = Queue.PriorityQueue()
  q.put((0, PartialSolution(root=(board, list(pieces), 0, 0, 0))))
  threads = []
  for i in range(NUMTHREADS):
    thread = PartialSolution()
    thread.daemon = True
    threads.append(thread)
    thread.start()
  for thread in threads:
    thread.join()
    print '\a'
  print 'Challenge "{name}" using pieces {pieces}'.format(name=title, pieces=pieces)
  print 'Took {time} seconds using {partials} partials.'.format(time=time.time()-startTime, partials = uuid)
  print '{num} solution{s} at cost {cost}:'.format(num=len(solutions), s=('s' if len(solutions) != 1 else ''), cost=maxCost)
  for solution in solutions:
    for line in solution.board:
      print line
    print
