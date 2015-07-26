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
      self.board, self.board_h, self.board_w, self.pieces, self.steps, self.parity, self.parityLimit, self.x, self.y, self.uuid = root
      return
    super(PartialSolution, self).__init__()
  
  def debug(self):
    print 'UUID:', self.uuid
    print 'Board:'
    self.printBoard()
    print 'Cost:', self.cost
    print 'Pieces:', self.pieces
    print 'Steps:', self.steps
  
  def clone(self):
    return PartialSolution(root=(
      self.board,
      self.board_h,
      self.board_w,
      list(self.pieces),
      list(self.steps),
      self.parity,
      self.parityLimit,
      self.x,
      self.y,
      self.uuid, # Will be changed later IF the new copy survives
      ))
  
  def isInvalid(self, x, y):
    if x < 0 or y < 0:
      return True
    if x >= self.board_h or y >= self.board_w:
      return True
    return self.getBoard(x, y)
  
  def getParity(self, x, y):
    evenOdd = (x+y) % 2
    return 2 * (evenOdd) - 1
  
  def getBoard(self, x, y):
    mask = 2 << (x*self.board_w + y)
    return self.board & mask == mask
  
  def setBoard(self, x, y):
    self.board |= 2 << (x*self.board_w + y)
  
  def printBoard(self):
    board2 = [[None for _ in range(self.board_w)] for __ in range(self.board_h)]
    x = y = 0
    for pieceNum, rotation in self.steps:
      pieceName, initialRotation = pieces[pieceNum]
      offset, piece = tetrominos[(pieceName, (initialRotation+rotation) % 4)]
      for x, y in doubleIter(self.board_h, self.board_w):
        if board2[x][y] == None:
          break
      for i, j in doubleIter(len(piece), len(piece[0])):
        if piece[i][j] == 1:
          board2[x+i][y+j-offset] = pieceNum
    for line in board2:
      row = ' '
      for cell in line:
        row += '0123456789ABCDEF'[cell]
      print row
  
  def run(self):
    while True:
      try:
        _cost, self = q.get(True, 1)
        self.cost = _cost
      except Queue.Empty:
        return
      global maxCost
      if self.cost > maxCost and maxCost != -1:
        continue
      if len(self.pieces) == len(self.steps):
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
      for self.x, self.y in doubleIter(self.board_h, self.board_w):
        if self.getBoard(self.x, self.y):
          continue
        break
      self.attempted_pieces = []
      for rotation in range(0, 4):
        for pieceNum in range(len(self.pieces)):
          if self.pieces[pieceNum] == None:
            continue
          pieceName, initialRotation = self.pieces[pieceNum]
          offset, piece = tetrominos[(pieceName, (initialRotation+rotation) % 4)]
          if (pieceName, (initialRotation+rotation) % 4) in self.attempted_pieces:
            continue
          self.attempted_pieces.append((pieceName, (initialRotation+rotation) % 4))
          if piece == 'Invalid': # For pieces like the O which cannot be rotated further
            continue
          # T pieces have a kind of parity. Consider the board to be a checkerboard,
          # then a T piece covers 3 black and 1 white square, whereas all other pieces
          # cover 2 and 2. Thus, you must have an even number of T pieces AND
          # exactly half must be placed on white and on black.
          if pieceName == 'T':
            parity = self.getParity(self.x, self.y)
            if abs(self.parity) == self.parityLimit and parity * self.parity > 0:
              continue
            self.parity += parity
          newSolution = self.clone()
          invalidPlacement = False
          for i, j in doubleIter(len(piece), len(piece[0])):
            if piece[i][j] == 1:
              # Bounds check and Collision
              if self.isInvalid(self.x+i, self.y+j-offset):
                invalidPlacement = True
                break
              newSolution.setBoard(self.x+i, self.y+j-offset)
          # Checking for 1x1 holes in the next row is inefficient, as it happens very rarely.
          # if self.x < self.board_h:
          #   for j in range(1, self.board_w-1):
          #     if (self.getBoard(self.x+1, j-1), self.getBoard(self.x+1, j), self.getBoard(self.x+1, j+1)) == (True, False, True):
          #       if self.isInvalid(self.x+2, j):
          #           invalidPlacement = True
          #           global count
          #           count += 1
          #           break
          if invalidPlacement:
            continue
          newSolution.uuid = getUUID()
          newSolution.pieces[pieceNum] = None
          newSolution.steps.append((pieceNum, rotation))
          q.put((self.cost + rotation, newSolution))
      q.task_done()

challenges = {
  # 'Name': ['Pieces', Height, Width],
  # 'Connector':  ['T0, T0, L1', 3, 4], # Tied (3)
  # 'A':          ['I1, L1, J1, Z0', 4, 4], # Better (1)
  # 'Cube':       ['T0, T0, L1, Z0', 4, 4], # Tied (4)
  # 'Floor 1':    ['L1, Z0, L1, Z0', 4, 4], # Tied (4)
  # 'Recorder':   ['T0, T0, J1, S0, Z0', 5, 4], # Better (3)
  # 'Fan':        ['T0, T0, L1, S0, Z0', 5, 4], # Tied (4)
  # 'B':          ['I1, T0, T0, L1, Z0', 5, 4], # Tied (5)
  # 'C':          ['T0, T0, J1, J1, L1, Z0', 6, 4], # Better (2)
  # 'Platform':   ['I1, S0, T0, T0, L1, Z0', 6, 4], # Tied (5)
  # 'Test':       ['I0, J0, L0, O0, S0, S0, Z0', 7, 4], # (2)
  # 'Test 2':     ['I0, J0, L0, O0, S0, T0, T0, Z0', 8, 4], # (4)
  # 'Floor 6':    ['O0, S0, S0, S0, S0, L0, L0, L0, L0', 6, 6], # Tied (8)
  # 'Floor 2':    ['O0, T0, T0, T0, T0, L1, L1, L1, L1', 6, 6], # Better (7)
  # 'A star':     ['T0, T0, T0, T0, L1, J1, S0, S0, Z0, Z0', 5, 8], # Better (6)
  # 'B star':     ['I1, I1, O0, T0, T0, T0, T0, L1, L1, J1', 5, 8], # Better (3)
  # 'C star':     ['L1, J1, S0, Z0, T0, T0, I1, I1, O0, O0', 5, 8], # Better (2)
  # 'Floor 3':    ['I1, I1, I1, I1, J1, J1, L1, L1, S0, Z0', 5, 8], # Better (3)
  # 'Floor 4':    ['O0, O0, T0, T0, T0, T0, J1, L1, S0, S0, Z0, Z0', 8, 6], # Better (4)
  'Floor 5':    ['I1, I1, O0, O0, O0, O0, T0, T0, T0, T0, J1, L1, S0, Z0', 7, 8], # Better (4)
}

NUMTHREADS = 8
MAXSOLNS = 1 # Set to -1 for all solutions. Set to 0 to calculate only cost.
import copy
import Queue
import time
import array
global count
count = 0

lock = threading.Lock()
for title in challenges.keys():
  data = challenges[title]
  TCount = 0
  pieces = data[0].split(', ')
  for i in range(len(pieces)):
    if pieces[i][0] == 'T':
      TCount += 1
    pieces[i] = (pieces[i][0], int(pieces[i][1]))
  global maxCost
  maxCost = -1
  global solutions
  solutions = []
  global uuid
  uuid = 0
  startTime = time.time()
  
  q = Queue.PriorityQueue()
  # cost, PartialSolution(root=(board, board_h, board_w, pieces, steps, parity, parityLimit, x, y, uuid))
  q.put((0, PartialSolution(root=(0L, data[1], data[2], list(pieces), [], 0, TCount/2, 0, 0, 0))))
  threads = []
  for i in range(NUMTHREADS):
    thread = PartialSolution()
    thread.daemon = True
    threads.append(thread)
    thread.start()
  for thread in threads:
    thread.join()
    print '\a',
  print
  print 'Challenge "{name}" using pieces {pieces}'.format(name=title, pieces=pieces)
  print 'Took {time} seconds using {partials} partials.'.format(time=time.time()-startTime, partials = uuid)
  print '{num} solution{s} at cost {cost}:'.format(num=len(solutions), s=('s' if len(solutions) != 1 else ''), cost=maxCost)
  for solution in solutions:
    solution.printBoard()
    print
print count
