# Work isValidSolution() into stage 1 not stage 0... May not work because I need to know which blue_paths are a valid start -- which involves doing all the work anyways.

from collections import deque
from time import time

class Path():
  def __init__(self, path):
    if isinstance(path, list):
      self.path = path
    elif isinstance(path, tuple):
      self.path = [path]
    else:
      raise TypeError('Path.__init__ called with: %s' % str(path))
    self.sortedpath = sorted(self.path)

  # Required for dictionary entry. If two paths are the same, their hashes must be the same.
  def __hash__(self):
    hash = 0
    for point in self.path:
      hash << 5 # Multiply by 32, which isn't quite 36 -- but a hash doesn't have to be unique
      hash += point[1]<<3 + point[0] # (0-4)*8+(0-6) = (0-36)
    return hash

  # Required for dictionary entry.
  def __eq__(self, other):
    if len(self.sortedpath) != len(other.sortedpath):
      return False
    i = 0
    while i < len(self.sortedpath):
      if self.sortedpath[i] != other.sortedpath[i]:
        return False
      i += 1
    return True

  # Called with len()
  def __len__(self):
    return len(self.path)

  # Called when trying to print.
  def __repr__(self):
    return 'Path(%s)' % repr(self.path)

  # Returns if there is an overlap between the two paths
  def collides(self, other):
    i = j = 0
    while i < len(self.sortedpath) and j < len(other.sortedpath):
      if self.sortedpath[i] == other.sortedpath[j]:
        return True
      elif self.sortedpath[i] < other.sortedpath[j]:
        i += 1
      elif self.sortedpath[i] > other.sortedpath[j]:
        j += 1
    return False

# Adds (b, c) to a=(x, y)
def plus(a, b, c):
  return (a[0]+b, a[1]+c)

# Checks if a path is valid. Considerations are:
# 1. Steps forward should avoid forming loops (pictured in the comments, with o as the head and .. as the potential next step)
# 1a. Loops are OK when capturing an interesting point, such as a star or a square.
# 1b. Loops are OK when they hit the edge of the board, as this can divide stars.
# 2. Steps forward need to not collide with other paths
# 3. Steps forward need to be in bounds
# 4. Steps forward need to respect the breaks in the board
def isValidConnection(color, blue_path, orange_path, dir):
  banned_connections = {
    (0,2):['down'],
    (0,3):['up', 'down'],
    (0,4):['up'],
    (1,0):['right'],
    (2,0):['left'],
    (4,0):['right'],
    (5,0):['left']
  }
  head2 = None
  if color == 'blue':
    head = blue_path[-1]
    if len(blue_path) > 2:
      head2 = blue_path[-3]
  elif color == 'orange':
    head = orange_path[-1]
    if len(orange_path) > 2:
      head2 = orange_path[-3]
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
    if plus(head, 1, 0) in blue_path:
      return False # Issue 2
    if plus(head, 1, 0) in orange_path:
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
    if plus(head, 0, 1) in blue_path:
      return False
    elif plus(head, 0, 1) in orange_path:
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
    if plus(head, -1, 0) in blue_path:
      return False
    if plus(head, -1, 0) in orange_path:
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
    if plus(head, 0, -1) in blue_path:
      return False
    if plus(head, 0, -1) in orange_path:
      return False
  return True

# Convert seconds into a more human-readable time amount
def format_time(seconds):
  from math import floor
  if seconds < 1:
    return '%0.2f milliseconds' % (seconds*1000)
  seconds = floor(seconds)
  time_spent = ''
  if seconds > 3600:
    time_spent += '%d hour%s' % (seconds/3600, '' if seconds/3600 == 1 else 's')
    seconds %= 60
  if seconds > 60:
    time_spent += '%d minute%s, ' % (seconds/60, '' if seconds/60 == 1 else 's')
    seconds %= 60
  if seconds > 0:
    time_spent += '%d second%s, ' % (seconds, '' if seconds == 1 else 's')
  return time_spent[:-2]

# Find all valid blue and orange paths from a given base point
def findSolutions(base):
  to_visit = deque([base])
  solutions = []
  while len(to_visit) > 0:
    color, blue_path, orange_path = to_visit.popleft()
    if color == 'blue':
      head = blue_path[-1]
    elif color == 'orange':
      head = orange_path[-1]
    if head in [(0, 0), (6, 0), (0, 3), (0, 4), (6, 4)]: # Valid exits
      if color == 'blue':
        solutions.append(Path(blue_path))
      elif color == 'orange':
        solutions.append(Path(orange_path))
    if isValidConnection(color, blue_path, orange_path, 'left'):
      if color == 'blue':
        to_visit.append((color, blue_path + [plus(head, -1, 0)], orange_path))
      elif color == 'orange':
        to_visit.append((color, blue_path, orange_path + [plus(head, -1, 0)]))
    if isValidConnection(color, blue_path, orange_path, 'right'):
      if color == 'blue':
        to_visit.append((color, blue_path + [plus(head, 1, 0)], orange_path))
      elif color == 'orange':
        to_visit.append((color, blue_path, orange_path + [plus(head, 1, 0)]))
    if isValidConnection(color, blue_path, orange_path, 'up'):
      if color == 'blue':
        to_visit.append((color, blue_path + [plus(head, 0, -1)], orange_path))
      elif color == 'orange':
        to_visit.append((color, blue_path, orange_path + [plus(head, 0, -1)]))
    if isValidConnection(color, blue_path, orange_path, 'down'):
      if color == 'blue':
        to_visit.append((color, blue_path + [plus(head, 0, 1)], orange_path))
      elif color == 'orange':
        to_visit.append((color, blue_path, orange_path + [plus(head, 0, 1)]))
  return solutions

# Check if a square is contiguous to a square in the given direction.
def isConnected(blue_path, orange_path, square, dir):
  x, y = square
  if dir == 'left':
    if x == 0:
      return False
    try:
      index = blue_path.path.index((x, y))
      if index > 0 and blue_path.path[index-1] == (x, y+1):
        return False
      if index < len(blue_path)-1 and blue_path.path[index+1] == (x, y+1):
        return False
    except ValueError:
      pass
    try:
      index = orange_path.path.index((x, y))
      if index > 0 and orange_path.path[index-1] == (x, y+1):
        return False
      if index < len(orange_path)-1 and orange_path.path[index+1] == (x, y+1):
        return False
    except ValueError:
      pass
  elif dir == 'up':
    if y == 0:
      return False
    try:
      index = blue_path.path.index((x, y))
      if index > 0 and blue_path.path[index-1] == (x+1, y):
        return False
      if index < len(blue_path)-1 and blue_path.path[index+1] == (x+1, y):
        return False
    except ValueError:
      pass
    try:
      index = orange_path.path.index((x, y))
      if index > 0 and orange_path.path[index-1] == (x+1, y):
        return False
      if index < len(orange_path)-1 and orange_path.path[index+1] == (x+1, y):
        return False
    except ValueError:
      pass
  elif dir == 'right':
    if x == 5:
      return False
    try:
      index = blue_path.path.index((x+1, y+1))
      if index > 0 and blue_path.path[index-1] == (x+1, y):
        return False
      if index < len(blue_path)-1 and blue_path.path[index+1] == (x+1, y):
        return False
    except ValueError:
      pass
    try:
      index = orange_path.path.index((x+1, y+1))
      if index > 0 and orange_path.path[index-1] == (x+1, y):
        return False
      if index < len(orange_path)-1 and orange_path.path[index+1] == (x+1, y):
        return False
    except ValueError:
      pass
  elif dir == 'down':
    if y == 3:
      return False
    try:
      index = blue_path.path.index((x+1, y+1))
      if index > 0 and blue_path.path[index-1] == (x, y+1):
        return False
      if index < len(blue_path)-1 and blue_path.path[index+1] == (x, y+1):
        return False
    except ValueError:
      pass
    try:
      index = orange_path.path.index((x+1, y+1))
      if index > 0 and orange_path.path[index-1] == (x, y+1):
        return False
      if index < len(orange_path)-1 and orange_path.path[index+1] == (x, y+1):
        return False
    except ValueError:
      pass
  return True

def isValidSolution(blue_path, orange_path):
  # Given n paths of length m each:
  # Comparing naively is O(n^2 * m^2)
  # Sorting first costs O(n * log(m)) and comparing is then O(n^2 * m)
  if blue_path.collides(orange_path):
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

# Stage 0: Calculate all valid blue and orange paths.
stageStart = time()
blue_paths = findSolutions(('blue', [(3, 4)], [(3, 0)]))
blue_paths.append(Path((3, 4))) # Added in for the start point
orange_paths = findSolutions(('orange', [(3, 4)], [(3, 0)]))
orange_paths.append(Path((3, 0))) # Added in for the start point
# These are initialized separately because A. they aren't valid paths, and B. they need to have a children array defined (as a base case).
path_combos_b = {Path((3, 4)):{Path((3, 0)):{'parents':[],'cost':None, 'pCost': (0, None)}}}
path_combos_o = {Path((3, 0)):{Path((3, 4)):{'parents':[],'cost':None, 'pCost': (0, None)}}}
for bPath in blue_paths:
  for oPath in orange_paths:
    if isValidSolution(bPath, oPath):
      if bPath not in path_combos_b:
        path_combos_b[bPath] = {}
      path_combos_b[bPath][oPath] = {'parents':[], 'cost':None, 'pCost':None}
      if oPath not in path_combos_o:
        path_combos_o[oPath] = {}
      path_combos_o[oPath][bPath] = {'parents':[], 'cost':None, 'pCost':None}
stageEnd = time()
print 'Stage 0 done in', format_time(stageEnd-stageStart)
stageStart = stageEnd

# Stage 1: Create a tree through combos which connects all the possible paths (from start)
exits_b = []
exits_o = []
to_visit = deque([(Path((3, 4)), Path((3, 0)), 'blue')]) # Base starting point: Each path is length 1, and we start on the blue side.
while len(to_visit) > 0:
  bPath, oPath, color = to_visit.popleft()
  if color == 'blue' or oPath.path[-1][1] == 0: # Orange path connects to blue side or we're on the blue side, look for a new blue path.
    if oPath not in path_combos_o:
      raise Exception
    if oPath in path_combos_o:
      for new_bPath in blue_paths:
        if new_bPath == bPath:
          continue
        if new_bPath in path_combos_o[oPath]: # Valid path
          path_combos_b[new_bPath][oPath]['parents'].append((bPath, oPath))
          path_combos_o[oPath][new_bPath]['parents'].append((bPath, oPath))
          if path_combos_o[oPath][new_bPath]['pCost'] == None:
            path_combos_b[new_bPath][oPath]['pCost'] = (path_combos_b[bPath][oPath]['pCost'][0]+len(bPath), (bPath, oPath))
            path_combos_o[oPath][new_bPath]['pCost'] = (path_combos_o[oPath][bPath]['pCost'][0]+len(bPath), (bPath, oPath))
            to_visit.append((new_bPath, oPath, 'blue'))
          if path_combos_o[oPath][bPath]['pCost'][0] + len(bPath) < path_combos_o[oPath][new_bPath]['pCost'][0]:
            path_combos_b[new_bPath][oPath]['pCost'] = (path_combos_b[bPath][oPath]['pCost'][0]+len(bPath), (bPath, oPath))
            path_combos_o[oPath][new_bPath]['pCost'] = (path_combos_o[oPath][bPath]['pCost'][0]+len(bPath), (bPath, oPath))
          if new_bPath.path[-1] == (0, 3) and len(oPath) > 1: # Found a solution!
            path_combos_b[new_bPath][oPath]['cost'] = (0, None)
            exits_b.append((new_bPath, oPath))
  if color == 'orange' or bPath.path[-1][1] == 4: # Blue path connects to orange side or we're on the orange side, look for a new orange path.
    if bPath in path_combos_b:
      for new_oPath in orange_paths:
        if new_oPath == oPath:
          continue
        if new_oPath in path_combos_b[bPath]: # Valid path
          path_combos_b[bPath][new_oPath]['parents'].append((bPath, oPath))
          path_combos_o[new_oPath][bPath]['parents'].append((bPath, oPath))
          if path_combos_b[bPath][new_oPath]['pCost'] == None:
            path_combos_b[bPath][new_oPath]['pCost'] = (path_combos_b[bPath][oPath]['pCost'][0]+len(oPath), (bPath, oPath))
            path_combos_o[new_oPath][bPath]['pCost'] = (path_combos_o[oPath][bPath]['pCost'][0]+len(oPath), (bPath, oPath))
            to_visit.append((bPath, new_oPath, 'orange'))
          if path_combos_b[bPath][oPath]['pCost'][0] + len(oPath) < path_combos_b[bPath][new_oPath]['pCost'][0]:
            path_combos_b[bPath][new_oPath]['pCost'] = (path_combos_b[bPath][oPath]['pCost'][0]+len(oPath), (bPath, oPath))
            path_combos_o[new_oPath][bPath]['pCost'] = (path_combos_o[oPath][bPath]['pCost'][0]+len(oPath), (bPath, oPath))
          if new_oPath.path[-1] == (0, 3) and len(bPath) > 1: # Found a solution!
            path_combos_o[new_oPath][bPath]['cost'] = (0, None)
            exits_o.append((bPath, new_oPath))

stageEnd = time()
print 'Stage 1 done in', format_time(stageEnd-stageStart)
stageStart = stageEnd

# Stage 2: Calculate distance to exit at each node
# pPath = (bPath, oPath) for the parent
def update_cost(pPath, parent, cPath, child):
  if pPath[0] == cPath[0]: # Orange path was changed to make this connection
    if parent['cost'] == None:
      parent['cost'] = (child['cost'][0]+len(cPath[1]), cPath)
      return True
    if parent['cost'][0] > child['cost'][0] + len(cPath[1]):
      parent['cost'] = (child['cost'][0]+len(cPath[1]), cPath)
  else: # Blue path was changed to make this connection
    if parent['cost'] == None:
      parent['cost'] = (child['cost'][0]+len(cPath[0]), cPath)
      return True
    if parent['cost'][0] > child['cost'][0] + len(cPath[0]):
      parent['cost'] = (child['cost'][0]+len(cPath[0]), cPath)
  return False

# Calculates cost at each node to reach a blue solution
to_visit = deque(exits_b)
while len(to_visit) > 0:
  bPath, oPath = to_visit.popleft()
  for parent in path_combos_b[bPath][oPath]['parents']:
    if update_cost(
      parent,
      path_combos_b[parent[0]][parent[1]],
      (bPath, oPath),
      path_combos_b[bPath][oPath]
    ):
      to_visit.append(parent)

# Calculates cost at each node to reach an orange solution
to_visit = deque(exits_o)
while len(to_visit) > 0:
  bPath, oPath = to_visit.popleft()
  for parent in path_combos_o[oPath][bPath]['parents']:
    if update_cost(
      parent,
      path_combos_o[parent[1]][parent[0]],
      (bPath, oPath),
      path_combos_o[oPath][bPath]
    ):
      to_visit.append(parent)

stageEnd = time()
print 'Stage 2 done in', format_time(stageEnd-stageStart)
stageStart = stageEnd
# Stage 3: Find and print the optimal solutions.

min_both = (999, None)
min_single = (999, None)

for exit in exits_b:
  bPath, oPath = exit
  cost_single = path_combos_b[bPath][oPath]['pCost'][0]
  cost_both = cost_single+path_combos_o[oPath][bPath]['cost'][0]
  if cost_single < min_single[0]:
    min_single = (cost_single, exit)
  if cost_both < min_both[0]:
    min_both = (cost_both, exit)

for exit in exits_o:
  bPath, oPath = exit
  cost_single = path_combos_o[oPath][bPath]['pCost'][0]
  cost_both = cost_single+path_combos_b[bPath][oPath]['cost'][0]
  if cost_single < min_single[0]:
    min_single = (cost_single, exit)
  if cost_both < min_both[0]:
    min_both = (cost_both, exit)

print 'Minimum cost for a single exit:', min_single[0]
node = min_single[1]
while node is not None:
  print node
  node = path_combos_b[node[0]][node[1]]['pCost'][1]

print 'Minimum cost for a both exits:', min_both[0]
node = min_both[1]
while node is not None:
  print node
  node = path_combos_b[node[0]][node[1]]['pCost'][1]
