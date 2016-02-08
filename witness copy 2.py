from Queue import Queue
from threading import Lock, Thread # Threads are used for the queue of PartialSolutions.
from multiprocessing import Process, Array # Processes are used for simplifying solutions and calculating steps
from time import time
from copy import copy

# Add two tuples together. Credit http://stackoverflow.com/questions/497885/python-element-wise-tuple-operations-like-sum
def plus(a, b):
  import operator
  return tuple(map(operator.add, a, b))

# The puzzle grid is a 7x5, so indices range from [0-6][0-3].
banned_connections = {
	(0,2):(0,3),
	(0,3):(0,2),
	(0,3):(0,4),
	(0,4):(0,3),
	(1,0):(2,0),
	(2,0):(1,0),
	(4,0):(5,0),
	(5,0):(4,0)
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
      self.color, self.blue_solved, self.orange_solved, self.blue_path, self.orange_path, self.history, self.uuid = root
      return
    super(PartialSolution, self).__init__()

  def __eq__(self, other):
    if self.blue_path != other.blue_path:
      return False
    if self.orange_path != other.orange_path:
      return False
    if self.history != other.history:
      return False
    if self.blue_solved != other.blue_solved:
      return False
    if self.orange_solved != other.orange_solved:
      return False
    return True

  def isValidConnection(self, head, (x, y)):
    if x < 0 or x > 6:
      return False
    if y < 0 or y > 4:
      return False
    if (x, y) in self.blue_path:
      return False
    if (x, y) in self.orange_path:
      return False
    if (x, y) in banned_connections and banned_connections[(x, y)] == head:
      return False
    return True

  def clone(self):
    return PartialSolution(root=(
      self.color,
      self.blue_solved,
      self.orange_solved,
      copy(self.blue_path),
      copy(self.orange_path),
      copy(self.history),
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
        solutions.append(self)
      if self.isValidConnection(head, plus(head, (-1, 0))): # Left
        newSolution = self.clone()
        if self.color == 'blue':
          newSolution.blue_path.append(plus(head, (-1, 0)))
        elif self.color == 'orange':
          newSolution.orange_path.append(plus(head, (-1, 0)))
        q.put(newSolution)
      if self.isValidConnection(head, plus(head, (1, 0))): # Right
        newSolution = self.clone()
        if self.color == 'blue':
          newSolution.blue_path.append(plus(head, (1, 0)))
        elif self.color == 'orange':
          newSolution.orange_path.append(plus(head, (1, 0)))
        q.put(newSolution)
      if self.isValidConnection(head, plus(head, (0, -1))): # Up
        newSolution = self.clone()
        if self.color == 'blue':
          newSolution.blue_path.append(plus(head, (0, -1)))
        elif self.color == 'orange':
          newSolution.orange_path.append(plus(head, (0, -1)))
        q.put(newSolution)
      if self.isValidConnection(head, plus(head, (0, 1))): # Down
        newSolution = self.clone()
        if self.color == 'blue':
          newSolution.blue_path.append(plus(head, (0, 1)))
        elif self.color == 'orange':
          newSolution.orange_path.append(plus(head, (0, 1)))
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
      if b == 0:
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
        if plus(square, (-1, 0)) not in visit_list:
          visit_list.append(plus(square, (-1, 0)))
      if isConnected(blue_path, orange_path, square, 'up'):
        if verbose:
          print square, 'is connected up'
        if plus(square, (0, -1)) not in visit_list:
          visit_list.append(plus(square, (0, -1)))
      if isConnected(blue_path, orange_path, square, 'right'):
        if verbose:
          print square, 'is connected to the right'
        if plus(square, (1, 0)) not in visit_list:
          visit_list.append(plus(square, (1, 0)))
      if isConnected(blue_path, orange_path, square, 'down'):
        if verbose:
          print square, 'is connected down'
        if plus(square, (0, 1)) not in visit_list:
          visit_list.append(plus(square, (0, 1)))
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
      if plus(square, (-1, 0)) not in visit_list:
        visit_list.append(plus(square, (-1, 0)))
    if isConnected(blue_path, orange_path, square, 'up'):
      if verbose:
        print square, 'is connected up'
      if plus(square, (0, -1)) not in visit_list:
        visit_list.append(plus(square, (0, -1)))
    if isConnected(blue_path, orange_path, square, 'right'):
      if verbose:
        print square, 'is connected to the right'
      if plus(square, (1, 0)) not in visit_list:
        visit_list.append(plus(square, (1, 0)))
    if isConnected(blue_path, orange_path, square, 'down'):
      if verbose:
        print square, 'is connected down'
      if plus(square, (0, 1)) not in visit_list:
        visit_list.append(plus(square, (0, 1)))
    j += 1
  if verbose:
    print 'Valid solution found'
  return True

def simplify(to_simplify, to_compare):
  solutions = []
  for s in to_simplify:
    try:
      for i in range(len(s.blue_path)-2):
        # This attempts to cut out any trivial loops that might have been found.
        simplify = s.blue_path[:i]+s.blue_path[i+2:]
        for c in to_compare:
          # Avoid simplifications which cut out the colored squares
          x1, y1 = s.blue_path[i]
          x2, y2 = s.blue_path[i+2]
          if (min(x1, x2), min(y1, y2)) == (0, 1):
            continue
          if (min(x1, x2), min(y1, y2)) == (5, 1):
            continue
          if c.blue_path == simplify:
            raise StopIteration
      for i in range(len(s.orange_path)-2):
        # This attempts to cut out any trivial loops that might have been found.
        simplify = s.orange_path[:i]+s.orange_path[i+2:]
        for c in to_compare:
          # Avoid simplifications which cut out the colored squares
          x1, y1 = s.orange_path[i]
          x2, y2 = s.orange_path[i+2]
          if (min(x1, x2), min(y1, y2)) == (0, 1):
            continue
          if (min(x1, x2), min(y1, y2)) == (5, 1):
            continue
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
# Color, blue solved, orange solved, blue path, orange path, history, uuid
stage0 = time()
q.put(PartialSolution(root=('blue', False, False, [(3, 4)], [(3, 0)], [], uuid)))
blue_paths = findSolutions()
# blue_paths = simplify(blue_paths, blue_paths)
q.put(PartialSolution(root=('orange', False, False, [(3, 4)], [(3, 0)], [], uuid)))
orange_paths = findSolutions()
# orange_paths = simplify(orange_paths, orange_paths)
stage1 = time()
print 'Stage 0 done in', stage1-stage0
print 'Search space', len(blue_paths)+len(orange_paths)
# Stage 1: Calculate blue paths that take us across
stage1paths = []
for bPath in blue_paths:
  if bPath.blue_path[-1] in [(0, 0), (0, 6)] and isValidSolution(bPath.blue_path, [(3, 0)]):
    stage1paths.append(bPath)
stage2 = time()
print 'Stage 1 done in', stage2-stage1
print 'Search space', len(stage1paths)
# Stage 2: Calculate orange paths. It's unlikely that they take us back to blue.
stage2paths = []
for bPath in stage1paths:
  for oPath in orange_paths:
    if isValidSolution(bPath.blue_path, oPath.orange_path):
      newSolution = oPath.clone()
      newSolution.blue_path = bPath.blue_path
      stage2paths.append(newSolution)
stage3 = time()
print 'Stage 2 done in', stage3-stage2
print 'Search space', len(stage2paths)
# Stage 3: Calculate blue paths. These probably still need to take us back to orange.

# Stage 4: Calculate orange paths. These are now allowed



