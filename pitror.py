DEBUG = False

from queue import Empty, PriorityQueue
from sys import maxsize as maxint
from threading import Lock, Thread
from time import time
from copy import deepcopy

uuid = 0
uuidlock = Lock()
def getUUID():
  global uuid
  uuidlock.acquire()
  uuid += 1
  newId = uuid
  uuidlock.release()
  return newId

def getCell(board, x, y):
  if x < 0 or y < 0:
    raise StopIteration
  if x >= len(board) or y >= len(board[0]):
    raise StopIteration
  return board[x][y]

def move(board, num, dir):
  # Get all cells marked num, being careful to only pick the edge facing dir
  cells = []
  if dir[1] == -1: # Left
    for x in range(0, len(board), 1):
      for y in range(0, len(board[0]), 1):
        if getCell(board, x, y) == num:
          cells.append((x, y))
          break
  elif dir[1] == 1: # Right
    for x in range(0, len(board), 1):
      for y in range(len(board[0])-1, -1, -1):
        if getCell(board, x, y) == num:
          cells.append((x, y))
          break
  elif dir[0] == -1: # Up
    for y in range(0, len(board[0]), 1):
      for x in range(0, len(board), 1):
        if getCell(board, x, y) == num:
          cells.append((x, y))
          break
  elif dir[0] == 1: # Down
    for y in range(0, len(board[0]), 1):
      for x in range(len(board)-1, -1, -1):
        if getCell(board, x, y) == num:
          cells.append((x, y))
          break

  for cell in cells:
    new_num = getCell(board, cell[0] + dir[0], cell[1] + dir[1])
    if new_num is not None:
      move(board, new_num, dir)
  for cell in cells:
    board[cell[0] + dir[0]][cell[1] + dir[1]] = num

class PartialSolution(Thread):
  def __init__(self, root=None):
    if root != None:
      self.board, self.steps, self.uuid, self.cost = root
      return
    super(PartialSolution, self).__init__()

  def __gt__(self, other):
    return self.cost > other.cost

  def debug(self):
    print('UUID:', self.uuid)
    print('Board:', self.board)
    print('Cost:', self.cost)
    print('Steps:', self.steps)

  def clone(self):
    return PartialSolution(root=(
      deepcopy(self.board),
      list(self.steps),
      getUUID(),
      self.cost
      ))

  # Done with helper functions, real code starts here
  def run(self):
    while True:
      global q
      try:
        self = q.get(True, 1)
      except Empty:
        if DEBUG:
          print('Queue empty')
        return
      if DEBUG:
        self.debug()
      global max_cost
      if self.cost > max_cost:
        if DEBUG:
          print('cost > max_cost:', self.cost, '>', max_cost)
        continue
      # Completed solution, reached the exit
      if self.board[1][6] == 0:
        if DEBUG:
          print('(complete solution)')
        global solutions, MAXSOLNS
        if MAXSOLNS != 'All': # Don't update max cost
          max_cost = min(max_cost, self.cost)
        if MAXSOLNS == len(solutions):
          return
        solutions.append(self)
        q.task_done()
        continue


      for num in range(15):
        for dir in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
          board = deepcopy(self.board)
          try:
            move(board, num, dir)
            new_partial = self.clone()
            new_partial.board = board
            new_partial.steps.append((num, dir))
            new_partial.cost += 1
            if new_partial.cost <= max_cost:
              q.put(new_partial)

          except StopIteration:
            pass
      q.task_done()

class Box:
  def __init__(self, others):
    self.others = others

if __name__ == '__main__':
  global MAXSOLNS, max_cost, solutions
  # MAXSOLNS can be set to 'All', maxint, or a value
  max_cost = 4
  MAXSOLNS = maxint
  solutions = []
  NUMTHREADS = 8
  if DEBUG:
    NUMTHREADS = 1
  startTime = time()

  board = [
    [0,   1,  2, None,  3,  4, None],
    [5,   6,  7,    8,  9, 10,   10],
    [11, 12, 12,    8, 13, 13,   13],
  ]
  # iterate grid and turn into boxes


  global q
  q = PriorityQueue()


  # self.board, self.steps, self.uuid, self.cost
  q.put(PartialSolution(root=(board, [], 0, 0)))

  threads = []
  for i in range(NUMTHREADS):
    thread = PartialSolution()
    threads.append(thread)
    thread.start()
  for thread in threads:
    thread.join()
  runtime = time()-startTime
  print('Took', runtime, 'seconds using', uuid, 'partials.')
  if max_cost != maxint:
    print('Minimal solution cost:', max_cost)
  if len(solutions) > 0:
    print('Found', len(solutions), 'solutions:')
  solutions.sort(key=lambda s: s.steps)




