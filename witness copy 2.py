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
      self.color, self.blue_path, self.orange_path, self.uuid = root
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

def isValidSolution(blue_path, orange_path):
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
    j = 0
    while j < len(visit_list):
      square = visit_list[j]
      if square in stars:
        if pair_star is not None:
          return False
        pair_star = square
      if isConnected(blue_path, orange_path, square, 'left'):
        if plus(square, -1, 0) not in visit_list:
          visit_list.append(plus(square, -1, 0))
      if isConnected(blue_path, orange_path, square, 'up'):
        if plus(square, 0, -1) not in visit_list:
          visit_list.append(plus(square, 0, -1))
      if isConnected(blue_path, orange_path, square, 'right'):
        if plus(square, 1, 0) not in visit_list:
          visit_list.append(plus(square, 1, 0))
      if isConnected(blue_path, orange_path, square, 'down'):
        if plus(square, 0, 1) not in visit_list:
          visit_list.append(plus(square, 0, 1))
      j += 1
    if pair_star is None:
      return False
    stars.remove(pair_star)
  # All stars verified, now check the colored squares

  # Black square
  visit_list = [(0, 1)]
  j = 0
  while j < len(visit_list):
    square = visit_list[j]
    # White square
    if square == (5, 1):
      return False
    if isConnected(blue_path, orange_path, square, 'left'):
      if plus(square, -1, 0) not in visit_list:
        visit_list.append(plus(square, -1, 0))
    if isConnected(blue_path, orange_path, square, 'up'):
      if plus(square, 0, -1) not in visit_list:
        visit_list.append(plus(square, 0, -1))
    if isConnected(blue_path, orange_path, square, 'right'):
      if plus(square, 1, 0) not in visit_list:
        visit_list.append(plus(square, 1, 0))
    if isConnected(blue_path, orange_path, square, 'down'):
      if plus(square, 0, 1) not in visit_list:
        visit_list.append(plus(square, 0, 1))
    j += 1
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

stages = [None]

path_combos_b = {}
path_combos_o = {}
# Stage 0: Calculate all blue and orange paths.
stageStart = time()
q.put(PartialSolution(root=('blue', [(3, 4)], [(3, 0)], uuid)))
blue_paths = findSolutions()
q.put(PartialSolution(root=('orange', [(3, 4)], [(3, 0)], uuid)))
orange_paths = findSolutions()
for bPath in blue_paths:
  path_combos_b[str(bPath)] = {}
for oPath in orange_paths:
  path_combos_o[str(oPath)] = {}
for bPath in blue_paths:
  for oPath in orange_paths:
    if isValidSolution(bPath, oPath):
      path_combos_b[str(bPath)][str(oPath)] = True
      path_combos_o[str(oPath)][str(bPath)] = True
stageEnd = time()
print 'Stage 0 done in', stageEnd-stageStart

stage = 1
stages = [{str([(3, 0)]):{str([(3, 4)]):True}}] # Starting point is no paths.
while True:
  stages.append({})
  exits = set()
  stageStart = stageEnd
  for oPath in orange_paths:
    if str(oPath) not in stages[stage-1]:
      continue
    # All orange paths from the previous configuration
    for bPath in path_combos_o[str(oPath)]:
      if str(bPath) in stages[stage-1][str(oPath)]:
        continue
      # All valid blue paths *not* from the previous configuration(s)
      if str(bPath) not in stages[stage]:
        stages[stage][str(bPath)] = {}
      stages[stage][str(bPath)][str(oPath)] = True
      exits.add(str(bPath[-1])+'|'+str(oPath[-1]))
      # Add to this stage.
  stageEnd = time()
  print 'Stage', stage, 'done in', stageEnd-stageStart
  print 'Exits:', exits
  stage += 1
  stages.append({})
  exits = set()
  stageStart = stageEnd
  for bPath in blue_paths:
    if str(bPath) not in stages[stage-1]:
      continue
    # All blue paths from the previous configuration
    for oPath in path_combos_b[str(bPath)]:
      if str(oPath) in stages[stage-1][str(bPath)]:
        continue
      # All valid orange paths *not* from the previous configuration(s)
      if str(oPath) not in stages[stage]:
        stages[stage][str(oPath)] = {}
      stages[stage][str(bPath)][str(oPath)] = True
  stageEnd = time()
  print 'Stage', stage, 'done in', stageEnd-stageStart
  print 'Exits:', exits
  stage += 1
# End while True



'''
# Stage 1: Calculate blue paths that take us across
stageStart = stageEnd
stages.append([])
for bPath in blue_paths:
  if bPath[-1] in [(0, 0), (0, 6)] and isValidSolution(bPath, [(3, 0)]):
    stages[1].append(bPath)
stageEnd = time()
print 'Stage 1 done in', stageEnd-stageStart
print 'Search space', len(stages[1])
# Stage 2: Calculate orange paths. It's unlikely that they take us back to blue.
stageStart = stageEnd
exits = set()
stages.append({})
for bPath in stages[1]:
  for oPath in orange_paths:
    if isValidSolution(bPath, oPath):
      if str(oPath) not in stages[2]:
        stages[2][str(oPath)] = {}
      if str(bPath) not in stages[2][str(oPath)]:
        stages[2][str(oPath)][str(bPath)] = True
        exits.add(str(bPath[-1])+'|'+str(oPath[-1]))
print exits # All exits here are blue-(0, 0) orange-(6, 0)
stageEnd = time()
print 'Stage 2 done in', stageEnd-stageStart
print 'Search space', sum([len(stages[2][g]) for g in stages[2]])
# Stage 3: Calculate blue paths.
stageStart = stageEnd
exits = set()
stages.append({})
for oPath in orange_paths:
  if str(oPath) not in stages[2]: # Only consider valid oPaths
    continue
  for bPath in blue_paths:
    if bPath[-1][1] != 0 and oPath[-1][1] != 4: # Impossible to cross the gap
      continue
    if str(bPath) in stages[2][str(oPath)]:
      continue
    # Only consider bPath, oPath pairs that were not previously possible.
    if isValidSolution(bPath, oPath):
      if str(bPath) not in stages[3]:
        stages[3][str(bPath)] = {}
      if str(oPath) not in stages[3][str(bPath)]:
        stages[3][str(bPath)][str(oPath)] = True
        exits.add(str(bPath[-1])+'|'+str(oPath[-1]))
print exits
stageEnd = time()
print 'Stage 3 done in', stageEnd-stageStart
print 'Search space', sum([len(stages[3][g]) for g in stages[3]])
# Stage 4: Calculate an orange path.
stageStart = stageEnd
exits = set()
stages.append({})
for bPath in blue_paths:
  if str(bPath) not in stages[3]: # Only consider valid bPaths
    continue
  for oPath in orange_paths:
    if bPath[-1][1] != 0 and oPath[-1][1] != 4: # Impossible to cross the gap
      continue
    if str(oPath) in stages[3][str(bPath)]:
      continue
    if str(oPath) in stages[2] and str(bPath) in stages[2][str(oPath)]:
      continue
    # Only consider bPath, oPath pairs that were not previously possible.
    if isValidSolution(bPath, oPath):
      if str(oPath) not in stages[4]:
        stages[4][str(oPath)] = {}
      if str(bPath) not in stages[4][str(oPath)]:
        stages[4][str(oPath)][str(bPath)] = True
        exits.add(str(bPath[-1])+'|'+str(oPath[-1]))
print exits
stageEnd = time()
print 'Stage 4 done in', stageEnd-stageStart
print 'Search space', sum([len(stages[4][g]) for g in stages[4]])
# Stage 5 ... loop time!

stage = 5

while True:
  stageStart = stageEnd
  exits = set()
  stages.append({})
  for bPath in blue_paths:
    if str(bPath) not in stages[-2]: # Only consider valid bPaths
      continue
    for oPath in orange_paths:
      if bPath[-1][1] != 0 and oPath[-1][1] != 4: # Impossible to cross the gap
        continue
      if str(oPath) in stages[3][str(bPath)]:
        continue
      if str(oPath) in stages[2] and str(bPath) in stages[2][str(oPath)]:
        continue
      # Only consider bPath, oPath pairs that were not previously possible.
      if isValidSolution(bPath, oPath):
        if str(oPath) not in stages[4]:
          stages[4][str(oPath)] = {}
        if str(bPath) not in stages[4][str(oPath)]:
          stages[4][str(oPath)][str(bPath)] = True
          exits.add(str(bPath[-1])+'|'+str(oPath[-1]))
  print exits
  stageEnd = time()
'''