DEBUG = False
checks = [0, 0, 0, 0]

tetrominos = {
  ('I', 0):
    (0,
    [[1, 1, 1, 1]]),
  ('I', 1):
    (0,
    [[1],
     [1],
     [1],
     [1]]),
  ('I', 2): ('!', 'Invalid'),
  ('I', 3): ('!', 'Invalid'),
#----------------------------
  ('J', 0):
    (0,
    [[1, 0, 0],
     [1, 1, 1]]),
  ('J', 1):
    (0,
    [[1, 1],
     [1, 0],
     [1, 0]]),
  ('J', 2):
    (0,
    [[1, 1, 1],
     [0, 0, 1]]),
  ('J', 3):
    (1,
    [[0, 1],
     [0, 1],
     [1, 1]]),
#----------------------------
  ('L', 0):
    (0,
    [[1, 1, 1],
     [1, 0, 0]]),
  ('L', 1):
    (0,
    [[1, 1],
     [0, 1],
     [0, 1]]),
  ('L', 2):
    (2,
    [[0, 0, 1],
     [1, 1, 1]]),
  ('L', 3):
    (0,
    [[1, 0],
     [1, 0],
     [1, 1]]),
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

from Queue import Empty, PriorityQueue
from threading import Lock, Thread
from time import time
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
      getUUID(),
      ))

  # Returns True if the point is out of bounds or if the point is filled.
  def isInvalid(self, x, y):
    if x < 0 or y < 0:
      return True
    if x >= self.board_h or y >= self.board_w:
      return True
    return self.getBoard(x, y)

  # Returns 0 if board is empty, 1 otherwise.
  def getBoard(self, x, y):
    mask = 2 << (x*self.board_w + y)
    return self.board & mask == mask

  # Sets a board square to 1.
  def setBoard(self, x, y):
    self.board |= 2 << (x*self.board_w + y)

  # Helper method for printBoard, used in construction of board3
  def setPrintableBoard(self, board, x, y, char):
    if board[x][y] == '/':
      board[x][y] = char
    elif board[x][y] == '-' and char == '|':
      board[x][y] = '+'
    elif board[x][y] == '|' and char == '-':
      board[x][y] = '+'

  def printBoard(self, simple=False):
    global pieces
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

  # Done with helper functions, real code starts here
  def run(self):
    while True:
      global q, pieces
      try:
        _cost, self = q.get(True, 1)
        self.cost = _cost
      except Empty:
        if DEBUG:
          print 'Queue empty'
        return
      if DEBUG:
        self.debug()
      global maxCost
      if self.cost > maxCost and maxCost != -1:
        if DEBUG:
          print 'cost', self.cost,' > maxCost', maxCost
        continue
      # Completed solution, since all pieces are placed
      if len(self.pieces) == len(self.steps):
        if DEBUG:
          print '(complete solution)'
        global solutions
        if len(solutions) == 0:
          maxCost = self.cost
        global MAXSOLNS
        if len(solutions) == MAXSOLNS:
          return
        solutions.append(self)
        if len(solutions) == MAXSOLNS: # Allows the -1/0 maxSolutions logicbelow.
          return
        q.task_done()
        continue

      for self.x, self.y in doubleIter(self.board_h, self.board_w, start=(self.x, self.y)):
        if not self.getBoard(self.x, self.y):
          break
      if DEBUG:
        print 'First free space (x,y):', self.x, self.y
      self.attempted_pieces = []
      for rotation in range(0, 4):
        for pieceNum in range(len(self.pieces)):
          try:
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

            if DEBUG:
              print 'Attempting to place piece', pieceName, 'with rotation', (initialRotation+rotation)%4
              invalid = False

            # Now we start checking for invalid states.
            # First check: Bounds and collision. (68% hitrate)
            # Additionally, we start filling in the new board.
            for i, j in doubleIter(len(piece), len(piece[0])):
              if piece[i][j] == 1:
                # Bounds check and Collision
                if self.isInvalid(self.x+i, self.y+j-offset):
                  if DEBUG:
                    print 'Failed check #1'
                    checks[0] += 1
                  raise StopIteration
                newSolution.setBoard(self.x+i, self.y+j-offset)

            # Second check: 1x1 holes in the next row. (8.2% hitrate)
            # Also checks L placements against the side of the board.
            for i in range(self.x, self.x+len(piece)):
              for j in range(self.board_w):
                if not newSolution.getBoard(i, j): # A potential gap
                  if newSolution.isInvalid(i, j-1) and newSolution.isInvalid(i, j+1) and newSolution.isInvalid(i+1, j):
                    if DEBUG:
                      print 'Failed check #2'
                      checks[1] += 1
                      invalid = True
                    else:
                      raise StopIteration

            # Third check: Uneven parity in the last row(s). (7% hitrate)
            # If the piece touches the edge of the board,
            # then it divides the remaining space into two parts.
            # Each part must be a multiple of 4, or else it can't be filled by tetrominos.
            if len(piece) + self.x == self.board_h: # Piece placed touches the end of the board
              # Looking through columns until we find a filled one
              spaces = 0
              for j in range(self.board_w):
                fullCol = True
                for i in range(self.x, self.board_h):
                  if not newSolution.getBoard(i, j): # Empty cell
                    spaces += 1
                    fullCol = False
                if fullCol:
                  if spaces%4 != 0:
                    if DEBUG:
                      print 'Failed check #3'
                      checks[2] += 1
                      invalid = True
                    else:
                      raise StopIteration

            # Fourth check: T-tetromino parity. (0.55% hitrate)
            # Consider the board to be a checkerboard,
            # then a T piece covers 3 black and 1 white squares, whereas all other pieces
            # cover 2 and 2. Thus, you must have an even number of T pieces AND
            # exactly half must be placed on white and half on black.
            if pieceName == 'T':
              parity = (self.x+self.y) % 2
              if self.parity[parity] == 0:
                if DEBUG:
                  print 'Failed check #4'
                  checks[3] += 1
                  invalid = True
                else:
                  raise StopIteration
              newSolution.parity[parity] -= 1

            if DEBUG and invalid:
              raise StopIteration

            # Passed all checks
            if DEBUG:
              print 'Success, added', newSolution.uuid, 'to queue.'
            newSolution.pieces[pieceNum] = None
            newSolution.steps.append((pieceNum, rotation))

            if rotation == 0:
              cost = 0
            elif rotation == 1:
              cost = 0 # First rotation is free because you can right-click the piece
            elif rotation == 2:
              cost = 1
            elif rotation == 3:
              cost = 2.1 # Rotating 3 times once is more expensive than 2 times twice.
            if self.cost + cost <= maxCost or maxCost == -1:
              q.put((self.cost + cost, newSolution))
          except StopIteration:
            pass
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
  timeData = [[0, 0.0], [0, 0.0]]
  if DEBUG:
    NUMTHREADS = 1

  global uuid, maxCost, solutions, pieces
  uuid = 0
  for title in sorted(challenges.keys()):
    data = challenges[title]
    maxCost = -1
    solutions = []
    pieces = list(data[0])

    TCount = 0
    for i in range(len(pieces)):
      if pieces[i] == 'T':
        TCount += 1
      pieces[i] = (pieces[i], 0)

    print 'Challenge "{name}" using {num} pieces: {pieces}'.format(name=title, num = len(pieces), pieces=', '.join([a+str(b) for a,b in pieces]))
    startTime = time()

    global q
    q = PriorityQueue()
    # cost, PartialSolution(root=(board, board_h, board_w, pieces, steps, parity, x, y, uuid))
    q.put((0, PartialSolution(root=(0L, data[1], data[2], list(pieces), [], [TCount/2, TCount/2], 0, 0, uuid))))
    threads = []
    for i in range(NUMTHREADS):
      thread = PartialSolution()
      threads.append(thread)
      thread.start()
    for thread in threads:
      thread.join()
    runtime = time()-startTime
    print 'Took {time} seconds using {partials} partials.'.format(time=runtime, partials = uuid)
    print 'Found {num} solution{s} with {cost} rotations.'.format(num=len(solutions), s=('s' if len(solutions) != 1 else ''), cost=maxCost)
    print
    if len(solutions) == 0:
      timeData[1][0] += 1
      timeData[1][1] += runtime
      continue
    timeData[0][0] += 1
    timeData[0][1] += runtime
    solutions.sort(key=lambda s: s.steps)
    for solution in solutions:
      solution.printBoard()
  try:
    print 'Average time for success:', timeData[0][1]/timeData[0][0]
  except ZeroDivisionError:
    print 'N/A'
  try:
    print 'Average time for failure:', timeData[1][1]/timeData[1][0]
  except ZeroDivisionError:
    print 'N/A'
  try:
    print 'Average overall:', (timeData[0][1]+timeData[1][1])/(timeData[0][0]+timeData[1][0])
  except ZeroDivisionError:
    print 'N/A'

if __name__ == "__main__":
  challenges = {
    # 'Name': ['Pieces', Height, Width],
    # 'Connector':  ['LTT',            3, 4], # 1
    # 'Hexahedron': ['LTTZ',           4, 4], # 1
    # 'Fan':        ['LSTTZ',          5, 4], # 1
    # 'Recorder':   ['JSTTZ',          5, 4], # 0
    # 'Platform':   ['ILOTTZ',         6, 4], # 3.1
    # 'A':          ['IJLZ',           4, 4], # 0
    # 'B':          ['ILTTZ',          5, 4], # 1
    # 'C':          ['JJLTTZ',         6, 4], # 0
    # 'A star':     ['JLSSTTTTZZ',     5, 8], # 1
    # 'B star':     ['IIJLLOTTTT',     5, 8], # 1
    # 'C star':     ['IIJLOOSTTZ',     5, 8], # 1
    # 'Floor 1':    ['LLZZ',           4, 4], # 1
    # 'Floor 2':    ['LLLLOTTTT',      6, 6], # 2
    # 'Floor 3':    ['IIIIJJLLSZ',     5, 8], # 0
    # 'Floor 4':    ['OOJLSSTTTTZZ',   8, 6], # 1
    # 'Floor 5':    ['IIJLOOOOSTTTTZ', 7, 8], # 0
    # 'Floor 6':    ['OLLLLSSSS',      6, 6], # 3.1

    'Messenger A Connector':   ['ILLOOSTTTT',  10, 4], # 2
    'Messenger A Red Source':  ['IILLOSTTZZ',   8, 5], # 0
    'Messenger A Hexahedron':  ['IJLLOOSTT',    6, 6], # 0
    'Messenger A Fan':         ['JJLLTTZZZ',    6, 6], # 1
    'Messenger A Final':       ['IJJOO',        5, 4], # 0
    'Messenger B Blue Source': ['IJJJLLOOSSTT', 6, 8], # 0
    'Messenger B Red Source':  ['ILTTZ',        5, 4], # 1
    'Messenger B Connector 1': ['IIJSTTTTZZ',  10, 4], # 1
    'Messenger B Connector 2': ['IILSTTZ',      4, 7], # 1
    'Messenger B Final':       ['IJJJOOSTTZZZ', 6, 8], # 0
    'Messenger C Red Source':  ['IJJJLLOOTTZZ', 6, 8], # 0
    'Messenger C Blue Source': ['IJLTTZZ',      4, 7], # 1
    'Messenger C Connector 1': ['JLLTT',        5, 4], # 1
    'Messenger C Connector 2': ['JSTTZ',        5, 4], # 0
    'Messenger C Final':       ['IJJLLOOZZ',    6, 6], # 0

    # 'Demo Green': ['IILSTTZ', 4, 7],
    # 'Demo Blue':  ['LSTTZ',   5, 4],
    # 'Demo Gold':  ['ILOTTZ',  6, 4],

    # 'Road to Gehenna Silver': ['IJJLLTT',    4, 7], # 1
    # 'Road to Gehenna Gold':   ['IILSSSTTTT', 8, 5], # 3.1
  }
  solve(challenges, 16, -1)
  if DEBUG:
    print checks
