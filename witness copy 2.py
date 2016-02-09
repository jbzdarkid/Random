from Queue import Queue
from threading import Lock, Thread # Threads are used for the queue of PartialSolutions.
from multiprocessing import Process, Array # Processes are used for simplifying solutions and calculating steps
from time import time
from copy import copy

def plus(a, b, c):
  return (a[0]+b, a[1]+c)

# The puzzle grid is a 7x5, so indices range from [0-6][0-4].
banned_connections = {
  (0,2):['down'],
  (0,3):['up', 'down'],
  (0,4):['up'],
  (1,0):['right'],
  (2,0):['left'],
  (4,0):['right'],
  (5,0):['left']
}

global uuidlock
uuidlock = Lock()
def getUUID():
  global uuid
  uuidlock.acquire()
  uuid += 1
  newId = uuid
  uuidlock.release()
  return newId

def findSolutions():
  global solutions
  solutions = []
  threads = []
  for i in range(16): # Number of threads
    thread = PartialSolution()
    threads.append(thread)
    thread.start()
  for thread in threads:
    thread.join()
  return solutions

class PartialSolution(Thread):
  def __init__(self, root=None):
    if root != None:
      self.color, self.blue_solved, self.orange_solved, self.blue_path, self.orange_path, self.uuid = root
      return
    super(PartialSolution, self).__init__()

  # Checks if a path is valid. Considerations are:
  # 1. Steps forward should avoid forming loops (pictured in the comments, with o as the head and .. as the potential next step)
  # 1a. Loops are OK when capturing an interesting point, such as a star or a square.
  # 1b. Loops are OK when they hit the edge of the board, as this can divide stars.
  # 2. Steps forward need to not collide with other paths
  # 3. Steps forward need to be in bounds
  # 4. Steps forward need to respect the breaks in the board
  def isValidConnection(self, dir):
    debug = False
    if self.blue_path == [(3, 4), (4, 4), (5, 4), (6, 4), (6, 3), (6, 2), (5, 2), (5, 3), (4, 3), (3, 3), (2, 3), (2, 4), (1, 4)]:
      debug = True
    head2 = None
    if self.color == 'blue':
      head = self.blue_path[-1]
      if len(self.blue_path) > 2:
        head2 = self.blue_path[-3]
    if self.color == 'orange':
      head = self.orange_path[-1]
      if len(self.orange_path) > 2:
        head2 = self.orange_path[-3]
    if head in banned_connections and dir in banned_connections[head]:
      return False
    # 6 stars, 2 squares
    interesting_points = [(2, 0), (3, 1), (0, 2), (0, 3), (5, 2), (5, 3), (0, 1), (5, 1)]
    if dir == 'right':
      if head[0] == 6: # Issue 3
        return False
      if head[0] != 0: # Issue 1b
        # o..
        # |
        # +--
        if plus(head, 1, 1) == head2 and plus(head, 0, 0) not in interesting_points:
          return False # Issues 1 and 1a
        # +--
        # |
        # o..
        if plus(head, 1, -1) == head2 and plus(head, 0, -1) not in interesting_points:
          return False # Issues 1 and 1a
      if plus(head, 1, 0) in self.blue_path:
        return False # Issue 2
      if plus(head, 1, 0) in self.orange_path:
        return False # Issue 2
    elif dir == 'down':
      if head[1] == 4:
        return False
      if head[1] != 0:
        # +-o
        # | .
        # | .
        if plus(head, -1, 1) == head2 and plus(head, -1, 0) not in interesting_points:
          return False
        # o-+
        # . |
        # . |
        if plus(head, 1, 1) == head2 and plus(head, 0, 0) not in interesting_points:
          return False
      if plus(head, 0, 1) in self.blue_path:
        return False
      elif plus(head, 0, 1) in self.orange_path:
        return False
    elif dir == 'left':
      if head[0] == 0:
        return False
      if head[0] != 6:
        # --+
        #   |
        # ..o
        if plus(head, -1, -1) == head2 and plus(head, -1, -1) not in interesting_points:
          return False
        # ..o
        #   |
        # --+
        if plus(head, -1, 1) == head2 and plus(head, -1, 0) not in interesting_points:
          return False
      if plus(head, -1, 0) in self.blue_path:
        return False
      if plus(head, -1, 0) in self.orange_path:
        return False
    elif dir == 'up':
      if head[1] == 0:
        return False
      if head[1] != 4:
        # . |
        # . |
        # o-+
        if plus(head, 1, -1) == head2 and plus(head, 0, -1) not in interesting_points:
          return False
        # | .
        # | .
        # +-o
        if plus(head, -1, -1) == head2 and plus(head, -1, -1) not in interesting_points:
          return False
      if plus(head, 0, -1) in self.blue_path:
        return False
      if plus(head, 0, -1) in self.orange_path:
        return False
    return True

  def clone(self):
    return PartialSolution(root=(
      self.color,
      self.blue_solved,
      self.orange_solved,
      copy(self.blue_path),
      copy(self.orange_path),
      getUUID()
    ))

  def run(self):
    while True:
      from Queue import Empty
      global q
      try:
        self = q.get(True, 1)
      except Empty:
        return
      if self.color == 'blue':
        head = self.blue_path[-1]
      elif self.color == 'orange':
        head = self.orange_path[-1]
      if head in [(0, 0), (6, 0), (0, 3), (0, 4), (6, 4)]: # Valid exits
        global solutions
        if self.color == 'blue':
          solutions.append(self.blue_path)
        elif self.color == 'orange':
          solutions.append(self.orange_path)
      if self.isValidConnection('left'):
        newSolution = self.clone()
        if self.color == 'blue':
          newSolution.blue_path.append(plus(head, -1, 0))
        elif self.color == 'orange':
          newSolution.orange_path.append(plus(head, -1, 0))
        q.put(newSolution)
      if self.isValidConnection('right'):
        newSolution = self.clone()
        if self.color == 'blue':
          newSolution.blue_path.append(plus(head, 1, 0))
        elif self.color == 'orange':
          newSolution.orange_path.append(plus(head, 1, 0))
        q.put(newSolution)
      if self.isValidConnection('up'):
        newSolution = self.clone()
        if self.color == 'blue':
          newSolution.blue_path.append(plus(head, 0, -1))
        elif self.color == 'orange':
          newSolution.orange_path.append(plus(head, 0, -1))
        q.put(newSolution)
      if self.isValidConnection('down'):
        newSolution = self.clone()
        if self.color == 'blue':
          newSolution.blue_path.append(plus(head, 0, 1))
        elif self.color == 'orange':
          newSolution.orange_path.append(plus(head, 0, 1))
        q.put(newSolution)
      q.task_done()

# Check if a square is contiguous to a square in the given direction.
def isConnected(blue_path, orange_path, square, dir):
  x, y = square
  if dir == 'left':
    if x == 0:
      return False
    try:
      index = blue_path.index((x, y))
      if index > 0 and blue_path[index-1] == (x, y+1):
        return False
      if index < len(blue_path)-1 and blue_path[index+1] == (x, y+1):
        return False
    except ValueError:
      pass
    try:
      index = orange_path.index((x, y))
      if index > 0 and orange_path[index-1] == (x, y+1):
        return False
      if index < len(orange_path)-1 and orange_path[index+1] == (x, y+1):
        return False
    except ValueError:
      pass
  elif dir == 'up':
    if y == 0:
      return False
    try:
      index = blue_path.index((x, y))
      if index > 0 and blue_path[index-1] == (x+1, y):
        return False
      if index < len(blue_path)-1 and blue_path[index+1] == (x+1, y):
        return False
    except ValueError:
      pass
    try:
      index = orange_path.index((x, y))
      if index > 0 and orange_path[index-1] == (x+1, y):
        return False
      if index < len(orange_path)-1 and orange_path[index+1] == (x+1, y):
        return False
    except ValueError:
      pass
  elif dir == 'right':
    if x == 5:
      return False
    try:
      index = blue_path.index((x+1, y+1))
      if index > 0 and blue_path[index-1] == (x+1, y):
        return False
      if index < len(blue_path)-1 and blue_path[index+1] == (x+1, y):
        return False
    except ValueError:
      pass
    try:
      index = orange_path.index((x+1, y+1))
      if index > 0 and orange_path[index-1] == (x+1, y):
        return False
      if index < len(orange_path)-1 and orange_path[index+1] == (x+1, y):
        return False
    except ValueError:
      pass
  elif dir == 'down':
    if y == 3:
      return False
    try:
      index = blue_path.index((x+1, y+1))
      if index > 0 and blue_path[index-1] == (x, y+1):
        return False
      if index < len(blue_path)-1 and blue_path[index+1] == (x, y+1):
        return False
    except ValueError:
      pass
    try:
      index = orange_path.index((x+1, y+1))
      if index > 0 and orange_path[index-1] == (x, y+1):
        return False
      if index < len(orange_path)-1 and orange_path[index+1] == (x, y+1):
        return False
    except ValueError:
      pass
  return True

def isValidSolution(blue_path, orange_path, verbose=False):
  # This is o(n^2) and can be sped up to o(n) if the lists are sorted.
  for b in blue_path:
    for o in orange_path:
      if b == o:
        return False
  # For region definitions, we use square centers rather than square corners. The range for stars is thus [0-5, 0-3]
  stars = [(2, 0), (3, 1), (0, 2), (0, 3), (5, 2), (5, 3)]
  for i in range(3): # There are 6 stars, and each time we find one it needs to remove exactly 1 other star.
    pair_star = None
    visit_list = [stars.pop()]
    if verbose:
      print 'Iteration', i, 'selected star:', visit_list
    j = 0
    while j < len(visit_list):
      square = visit_list[j]
      if square in stars:
        if pair_star is not None:
          if verbose:
            print 'Tried to remove 2 stars in one region'
          return False
        pair_star = square
        if verbose:
          print 'Found pair star:', square
      if isConnected(blue_path, orange_path, square, 'left'):
        if verbose:
          print square, 'is connected to the left'
        if plus(square, -1, 0) not in visit_list:
          visit_list.append(plus(square, -1, 0))
      if isConnected(blue_path, orange_path, square, 'up'):
        if verbose:
          print square, 'is connected up'
        if plus(square, 0, -1) not in visit_list:
          visit_list.append(plus(square, 0, -1))
      if isConnected(blue_path, orange_path, square, 'right'):
        if verbose:
          print square, 'is connected to the right'
        if plus(square, 1, 0) not in visit_list:
          visit_list.append(plus(square, 1, 0))
      if isConnected(blue_path, orange_path, square, 'down'):
        if verbose:
          print square, 'is connected down'
        if plus(square, 0, 1) not in visit_list:
          visit_list.append(plus(square, 0, 1))
      j += 1
    if verbose:
      print 'Done visiting, contiguous region:', visit_list
    if pair_star is None:
      if verbose:
        print 'Only 1 star in region'
      return False
    stars.remove(pair_star)
  # All stars verified, now check the colored squares
  if verbose:
    print 'Valid solution with stars found'

  # Black square
  visit_list = [(0, 1)]
  j = 0
  while j < len(visit_list):
    square = visit_list[j]
    # White square
    if square == (5, 1):
      if verbose:
        print 'Squares are connected'
      return False
    if isConnected(blue_path, orange_path, square, 'left'):
      if verbose:
        print square, 'is connected to the left'
      if plus(square, -1, 0) not in visit_list:
        visit_list.append(plus(square, -1, 0))
    if isConnected(blue_path, orange_path, square, 'up'):
      if verbose:
        print square, 'is connected up'
      if plus(square, 0, -1) not in visit_list:
        visit_list.append(plus(square, 0, -1))
    if isConnected(blue_path, orange_path, square, 'right'):
      if verbose:
        print square, 'is connected to the right'
      if plus(square, 1, 0) not in visit_list:
        visit_list.append(plus(square, 1, 0))
    if isConnected(blue_path, orange_path, square, 'down'):
      if verbose:
        print square, 'is connected down'
      if plus(square, 0, 1) not in visit_list:
        visit_list.append(plus(square, 0, 1))
    j += 1
  if verbose:
    print 'Valid solution found'
  return True

# This attempts to cut out any trivial loops that might have been found.
def simplify(to_simplify, to_compare): # Simplify during creation (as per copy 0) -> 100n < n^2
  solutions = []
  for s in to_simplify:
    try:
      for c in to_compare:
        if c.blue_path == simplify:
          raise StopIteration
      for c in to_compare:
        if c.orange_path == simplify:
          raise StopIteration
      solutions.append(s)
    except StopIteration:
      pass
  return solutions

global uuid
uuid = 0
global q
q = Queue()

# Stage 0: Calculate all blue and orange paths.
stage0 = time()
q.put(PartialSolution(root=('blue', False, False, [(3, 4)], [(3, 0)], uuid)))
blue_paths = findSolutions()
q.put(PartialSolution(root=('orange', False, False, [(3, 4)], [(3, 0)], uuid)))
orange_paths = findSolutions()
stage1 = time()
print 'Stage 0 done in', stage1-stage0
print 'Search space', len(blue_paths)+len(orange_paths)
# Stage 1: Calculate blue paths that take us across
stage1paths = []
for bPath in blue_paths:
  if bPath[:14] == [(3, 4), (4, 4), (5, 4), (6, 4), (6, 3), (6, 2), (5, 2), (5, 3), (4, 3), (3, 3), (2, 3), (2, 4), (1, 4), (1, 3)]:#, (1, 2), (1, 1), (0, 1), (0, 0)]:
    print 0
  if bPath[-1] in [(0, 0), (0, 6)] and isValidSolution(bPath, [(3, 0)]):
    stage1paths.append(bPath)
stage2 = time()
print 'Stage 1 done in', stage2-stage1
print 'Search space', len(stage1paths)
# Stage 2: Calculate orange paths. It's unlikely that they take us back to blue.
exits = set()
stage2paths = {}
for bPath in stage1paths:
  for oPath in orange_paths:
    if isValidSolution(bPath, oPath):
      if str(oPath) not in stage2paths:
        stage2paths[str(oPath)] = {}
      if str(bPath) not in stage2paths[str(oPath)]:
        stage2paths[str(oPath)][str(bPath)] = True
        exits.add(str(bPath[-1])+'|'+str(oPath[-1]))
print exits
stage3 = time()
print 'Stage 2 done in', stage3-stage2
print 'Search space', sum([len(stage2paths[g]) for g in stage2paths])
# Stage 3: Calculate blue paths. These probably still need to take us back to orange.
exits = set()
stage3paths = {}
for oPath in orange_paths:
  if str(oPath) not in stage2paths: # Only consider valid oPaths
    continue
  for bPath in blue_paths:
    if str(bPath) not in stage2paths[str(oPath)]: # Only consider bPath, oPath pairs that were not previously possible.
      if isValidSolution(bPath, oPath):
        if str(bPath) not in stage3paths:
          stage3paths[str(bPath)] = {}
        if str(oPath) not in stage3paths[str(bPath)]:
          stage3paths[str(bPath)][str(oPath)] = True
          exits.add(str(bPath[-1])+'|'+str(oPath[-1]))
print exits
stage4 = time()
print 'Stage 3 done in', stage4-stage3
print 'Search space', sum([len(stage3paths[g]) for g in stage3paths])
# Stage 4: Calculate an orange path. There is a possiblity that these connect to blue.


