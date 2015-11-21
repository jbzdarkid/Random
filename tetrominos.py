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

def doubleIter(xmax, ymax, start=(0, 0)):
  xmin, ymin = start
  for y in range(ymin, ymax):
    yield (xmin, y)
  for x in range(xmin+1, xmax):
    for y in range(0, ymax):
      yield (x, y)

from threading import Lock, Thread
global uuidlock
uuidlock = Lock()
def getUUID():
  global uuid
  uuidlock.acquire()
  uuid += 1
  newId = uuid
  uuidlock.release()
  return newId

class PartialSolution(Thread):
  def __init__(self, root=None):
    if root != None:
      self.board, self.board_h, self.board_w, self.pieces, self.steps, self.parity, self.x, self.y, self.uuid = root
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
      list(self.parity),
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

  def getBoard(self, x, y):
    mask = 2 << (x*self.board_w + y)
    return self.board & mask == mask

  def setBoard(self, x, y):
    self.board |= 2 << (x*self.board_w + y)

  def setPrintableBoard(self, board, x, y, char):
    if board[x][y] == '/':
      board[x][y] = char
    elif board[x][y] == '-' and char == '|':
      board[x][y] = '+'
    elif board[x][y] == '|' and char == '-':
      board[x][y] = '+'

  def printBoard(self, simple=False):
    # Board2 is reconstructed from the piece placement steps
    board2 = [[-1 for _ in range(self.board_w)] for __ in range(self.board_h)]
    x = y = 0
    for pieceNum, rotation in self.steps:
      pieceName, initialRotation = pieces[pieceNum]
      offset, piece = tetrominos[(pieceName, (initialRotation+rotation) % 4)]
      for x, y in doubleIter(self.board_h, self.board_w, start=(x, y)):
        if board2[x][y] == -1:
          break
      for i, j in doubleIter(len(piece), len(piece[0])):
        if piece[i][j] == 1:
          board2[x+i][y+j-offset] = pieceNum
    if simple:
      chars = '_1234567890ABCDEF'
      for row in board2:
        print ''.join(chars[i+1] for i in row)
      return

    # Board3 is constructed from board 2. It's just prettier :)
    board3 = [['/' for _ in range(self.board_w*10+1)] for __ in range(self.board_h*5+1)]
    # Fixing some corners
    board3[0][self.board_w*10] = '-'
    board3[self.board_h*5][0] = '|'
    board3[self.board_h*5][self.board_w*10] = '+'
    for x, y in doubleIter(len(board2), len(board2[x])):
      if board2[x][y] != -1: # Piece internal
        for i, j in doubleIter(4, 9):
          self.setPrintableBoard(board3, x*5+i+1, y*10+j+1, ' ')
        if x > 0 and board2[x][y] == board2[x-1][y]: # Piece internal row
          for j in range(1, 10):
            self.setPrintableBoard(board3, x*5, y*10+j, ' ')
        if y > 0 and board2[x][y] == board2[x][y-1]: # Piece internal column
          for i in range(1, 5):
            self.setPrintableBoard(board3, x*5+i, y*10, ' ')
        if x > 0 and y > 0 and board2[x][y] == board2[x-1][y] and board2[x][y] == board2[x][y-1]: # O piece internal
          self.setPrintableBoard(board3, x*5, y*10, ' ')
      if x == 0: # Top row
        for j in range(10):
          self.setPrintableBoard(board3, x*5, y*10+j, '-')
      elif board2[x][y] != board2[x-1][y]: # Internal row
        for j in range(11):
          self.setPrintableBoard(board3, x*5, y*10+j, '-')
      if x == self.board_h-1: # Bottom row
        for j in range(10):
          self.setPrintableBoard(board3, (x+1)*5, y*10+j, '-')
      if y == 0: # Left column
        for i in range(5):
          self.setPrintableBoard(board3, x*5+i, y*10, '|')
      elif board2[x][y] != board2[x][y-1]: # Internal column
        for i in range(6):
          self.setPrintableBoard(board3, x*5+i, y*10, '|')
      if y == self.board_w-1: # Right column
        for i in range(5):
          self.setPrintableBoard(board3, x*5+i, (y+1)*10, '|')

    for line in board3:
      print ''.join(line)

  def run(self):
    while True:
      try:
        from Queue import Empty
        global q, pieces
        _cost, self = q.get(True, 1)
        self.cost = _cost
      except Empty:
        return
      global maxCost
      if self.cost > maxCost and maxCost != -1:
        continue
      # Completed solution, since all pieces are placed
      if len(self.pieces) == len(self.steps):
        global solutions
        if len(solutions) == 0:
          maxCost = self.cost
        global MAXSOLNS
        if len(solutions) == MAXSOLNS:
          return
        solutions.append(self)
        if len(solutions) == MAXSOLNS: # Allows the -1/0 logic below.
          return
        q.task_done()
        continue

      # Locating the first available space
      for self.x, self.y in doubleIter(self.board_h, self.board_w, start=(self.x, self.y)):
        if not self.getBoard(self.x, self.y):
          break
      self.attempted_pieces = []
      for rotation in range(0, 4):
        for pieceNum in range(len(self.pieces)):
          if self.pieces[pieceNum] == None:
            continue
          pieceName, initialRotation = self.pieces[pieceNum]
          offset, piece = tetrominos[(pieceName, (initialRotation+rotation) % 4)]
          if piece == 'Invalid': # For pieces like the O which cannot be rotated further
            continue
          # Avoiding duplicates
          if (pieceName, (initialRotation+rotation) % 4) in self.attempted_pieces:
            continue
          self.attempted_pieces.append((pieceName, (initialRotation+rotation) % 4))
          newSolution = self.clone()
          # T pieces have a kind of parity. Consider the board to be a checkerboard,
          # then a T piece covers 3 black and 1 white squares, whereas all other pieces
          # cover 2 and 2. Thus, you must have an even number of T pieces AND
          # exactly half must be placed on white and half on black.
          if pieceName == 'T':
            parity = (self.x+self.y) % 2
            if self.parity[parity] == 0:
              continue # This piece would cause >50% of the pieces to be of this type.
            newSolution.parity[parity] -= 1

          invalidPlacement = False
          for i, j in doubleIter(len(piece), len(piece[0])):
            if piece[i][j] == 1:
              # Bounds check and Collision
              if self.isInvalid(self.x+i, self.y+j-offset):
                invalidPlacement = True
                break
              newSolution.setBoard(self.x+i, self.y+j-offset)
          if invalidPlacement:
            continue
          # Checking for 1x1 holes in the next row is inefficient, as it happens very rarely (1-2%).
          # if self.x < self.board_h:
          #   for j in range(1, self.board_w-1):
          #     if (self.getBoard(self.x+1, j-1), self.getBoard(self.x+1, j), self.getBoard(self.x+1, j+1)) == (True, False, True):
          #       if self.isInvalid(self.x+2, j):
          #           invalidPlacement = True
          #           break
          if len(piece[0]) + self.y == self.board_h: # Piece placed touches the end of the board
            spaces = 0
            i = 0
            while not self.getBoard(i, self.board_h-1) and i < self.board_w:
              spaces += 1
              i += 1
            for j in range(i):
              if not self.getBoard(i, self.board_h-2):
                spaces += 1
            if spaces%4 != 0:
              continue # Impossible to fill remaining gap.
          newSolution.uuid = getUUID()
          newSolution.pieces[pieceNum] = None
          newSolution.steps.append((pieceNum, rotation))
          q.put((self.cost + rotation, newSolution))
      q.task_done()

def randomChallenge(x, y):
  from random import randint
  numPieces = x*y/4
  pieces = 'I0, I0, I1, I1, J0, J1, J2, J3, L0, L1, L2, L3, O0, O0, O0, O0, S0, S0, S1, S1, T0, T1, T2, T3, Z0, Z0, Z1, Z1'.split(', ')
  pieceList = ''
  for i in range(numPieces):
    r = randint(0, len(pieces)-1)
    pieceList += pieces[r] + ', '
  if pieceList.count('T') % 2 != 0:
    return randomChallenge(x, y)
  return [pieceList[:-2], x, y]

# Set MAXSOLNS -1 for all solutions. Set to 0 to calculate only cost.
def solve(challenges, NUMTHREADS, _MAXSOLNS, benchmark=False):
  global MAXSOLNS
  MAXSOLNS = _MAXSOLNS
  from Queue import PriorityQueue
  from time import time
  timeData = [[len(challenges), 0.0], [0, 0.0]]

  global uuid, maxCost, solutions, pieces
  uuid = 0
  for title in sorted(challenges.keys(), key=lambda s: int(s)):
    data = challenges[title]
    maxCost = -1
    solutions = []
    pieces = data[0].split(', ')

    TCount = 0
    for i in range(len(pieces)):
      if pieces[i][0] == 'T':
        TCount += 1
      pieces[i] = (pieces[i][0], int(pieces[i][1]))

    print 'Challenge "{name}" using {num} pieces: {pieces}'.format(name=title, num = len(pieces), pieces=''.join([a+str(b) for a,b in pieces]))
    startTime = time()

    global q
    q = PriorityQueue()
    # cost, PartialSolution(root=(board, board_h, board_w, pieces, steps, parity, x, y, uuid))
    q.put((0, PartialSolution(root=(0L, data[1], data[2], list(pieces), [], [TCount/2, TCount/2], 0, 0, uuid))))
    threads = []
    for i in range(NUMTHREADS):
      thread = PartialSolution()
      thread.daemon = True # Allows for ^C to kill threads
      threads.append(thread)
      thread.start()
    for thread in threads:
      thread.join()
    runtime = time()-startTime
    print 'Took {time} seconds using {partials} partials.'.format(time=runtime, partials = uuid)
    print 'Found {num} solution{s} with {cost} rotations.'.format(num=len(solutions), s=('s' if len(solutions) != 1 else ''), cost=maxCost)
    if len(solutions) == 0:
      timeData[1][0] += 1
      timeData[1][1] += runtime
      continue
    timeData[0][0] -= 1
    timeData[0][1] += runtime
    for solution in solutions:
      solution.printBoard()
  print 'Average time for success:', timeData[0][1]/timeData[0][0]
  print 'Average time for failure:', timeData[1][1]/timeData[1][0]
  print 'Average overall:', (timeData[0][1]+timeData[1][1])/(timeData[0][0]+timeData[1][0])

if __name__ == "__main__":

  challenges = {
    # 'Name': ['Pieces', Height, Width],
    'Connector':  ['T0, T0, L1', 3, 4], # 3
    'A':          ['I1, L1, J1, Z0', 4, 4], # 1
    'Cube':       ['T0, T0, L1, Z0', 4, 4], # 4
    'Floor 1':    ['L1, Z0, L1, Z0', 4, 4], # 4
    'Recorder':   ['T0, T0, J1, S0, Z0', 5, 4], # 3
    'Fan':        ['T0, T0, L1, S0, Z0', 5, 4], # 4
    'B':          ['I1, T0, T0, L1, Z0', 5, 4], # 5
    'C':          ['T0, T0, J1, J1, L1, Z0', 6, 4], # 2
    'Platform':   ['I1, S0, T0, T0, L1, Z0', 6, 4], # 5
    'Floor 6':    ['O0, S0, S0, S0, S0, L0, L0, L0, L0', 6, 6], # 8
    'Floor 2':    ['O0, T0, T0, T0, T0, L1, L1, L1, L1', 6, 6], # 7
    'A star':     ['T0, T0, T0, T0, L1, J1, S0, S0, Z0, Z0', 5, 8], # 6
    'B star':     ['I1, I1, O0, T0, T0, T0, T0, L1, L1, J1', 5, 8], # 3
    'C star':     ['L1, J1, S0, Z0, T0, T0, I1, I1, O0, O0', 5, 8], # 2
    'Floor 3':    ['I1, I1, I1, I1, J1, J1, L1, L1, S0, Z0', 5, 8], # 3
    'Floor 4':    ['O0, O0, T0, T0, T0, T0, J1, L1, S0, S0, Z0, Z0', 8, 6], # 4
    'Floor 5':    ['I1, I1, O0, O0, O0, O0, T0, T0, T0, T0, J1, L1, S0, Z0', 7, 8], # 4
  }
  solve(challenges, 16, 1)