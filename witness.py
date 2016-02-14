# Create a Path() class, define __hash__ and __cmp__ so that it can be used as a dictionary entry.
# Work isValidSolution() into stage 1 not stage 0... May not work because I need to know which blues are a valid start -- which involves doing all the work anyways.

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

  # Used for path + point. Returns a new Path() object with the point appended.
  def __add__(self, other):
    return Path(self.path + [other])

  # Used for "item in self"
  def __contains__(self, item):
    return item in self.path

  # Required for dictionary entry.
  def __eq__(self, other):
    return self.path == other.path

  # Getting a value in a list
  def __getitem__(self, key):
    return self.path[key]

  # Required for dictionary entry. If two paths are the same, their hashes must be the same.
  def __hash__(self):
    hash = 0
    for point in self.path:
      hash *= 35
      hash += 5*point[0] + 7*point[1]
    return hash

  # Called with len()
  def __len__(self):
    return len(self.path)

  # Called when trying to print.
  def __repr__(self):
    return 'Path(%s)' % repr(self.path)

  def index(self, point):
    return self.path.index(point)

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
def isValidConnection(color, blue, orange, dir):
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
    head = blue[-1]
    if len(blue) > 2:
      head2 = blue[-3]
  if color == 'orange':
    head = orange[-1]
    if len(orange) > 2:
      head2 = orange[-3]
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
    if plus(head, 1, 0) in blue:
      return False # Issue 2
    if plus(head, 1, 0) in orange:
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
    if plus(head, 0, 1) in blue:
      return False
    elif plus(head, 0, 1) in orange:
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
    if plus(head, -1, 0) in blue:
      return False
    if plus(head, -1, 0) in orange:
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
    if plus(head, 0, -1) in blue:
      return False
    if plus(head, 0, -1) in orange:
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
    color, blue, orange = to_visit.popleft()
    if color == 'blue':
      head = blue[-1]
    elif color == 'orange':
      head = orange[-1]
    if head in [(0, 0), (6, 0), (0, 3), (0, 4), (6, 4)]: # Valid exits
      if color == 'blue':
        solutions.append(blue)
      elif color == 'orange':
        solutions.append(orange)
    if isValidConnection(color, blue, orange, 'left'):
      if color == 'blue':
        to_visit.append((color, blue + plus(head, -1, 0), orange))
      elif color == 'orange':
        to_visit.append((color, blue, orange + plus(head, -1, 0)))
    if isValidConnection(color, blue, orange, 'right'):
      if color == 'blue':
        to_visit.append((color, blue + plus(head, 1, 0), orange))
      elif color == 'orange':
        to_visit.append((color, blue, orange + plus(head, 1, 0)))
    if isValidConnection(color, blue, orange, 'up'):
      if color == 'blue':
        to_visit.append((color, blue + plus(head, 0, -1), orange))
      elif color == 'orange':
        to_visit.append((color, blue, orange + plus(head, 0, -1)))
    if isValidConnection(color, blue, orange, 'down'):
      if color == 'blue':
        to_visit.append((color, blue + plus(head, 0, 1), orange))
      elif color == 'orange':
        to_visit.append((color, blue, orange + plus(head, 0, 1)))
  return solutions

# Check if a square is contiguous to a square in the given direction.
def isConnected(blue, orange, square, dir):
  x, y = square
  if dir == 'left':
    if x == 0:
      return False
    try:
      index = blue.index((x, y))
      if index > 0 and blue[index-1] == (x, y+1):
        return False
      if index < len(blue)-1 and blue[index+1] == (x, y+1):
        return False
    except ValueError:
      pass
    try:
      index = orange.index((x, y))
      if index > 0 and orange[index-1] == (x, y+1):
        return False
      if index < len(orange)-1 and orange[index+1] == (x, y+1):
        return False
    except ValueError:
      pass
  elif dir == 'up':
    if y == 0:
      return False
    try:
      index = blue.index((x, y))
      if index > 0 and blue[index-1] == (x+1, y):
        return False
      if index < len(blue)-1 and blue[index+1] == (x+1, y):
        return False
    except ValueError:
      pass
    try:
      index = orange.index((x, y))
      if index > 0 and orange[index-1] == (x+1, y):
        return False
      if index < len(orange)-1 and orange[index+1] == (x+1, y):
        return False
    except ValueError:
      pass
  elif dir == 'right':
    if x == 5:
      return False
    try:
      index = blue.index((x+1, y+1))
      if index > 0 and blue[index-1] == (x+1, y):
        return False
      if index < len(blue)-1 and blue[index+1] == (x+1, y):
        return False
    except ValueError:
      pass
    try:
      index = orange.index((x+1, y+1))
      if index > 0 and orange[index-1] == (x+1, y):
        return False
      if index < len(orange)-1 and orange[index+1] == (x+1, y):
        return False
    except ValueError:
      pass
  elif dir == 'down':
    if y == 3:
      return False
    try:
      index = blue.index((x+1, y+1))
      if index > 0 and blue[index-1] == (x, y+1):
        return False
      if index < len(blue)-1 and blue[index+1] == (x, y+1):
        return False
    except ValueError:
      pass
    try:
      index = orange.index((x+1, y+1))
      if index > 0 and orange[index-1] == (x, y+1):
        return False
      if index < len(orange)-1 and orange[index+1] == (x, y+1):
        return False
    except ValueError:
      pass
  return True

def isValidSolution(blue, orange):
  # This is o(n^2) and can be sped up to o(n) if the lists are sorted.
  for b in blue:
    for o in orange:
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
      if isConnected(blue, orange, square, 'left'):
        if plus(square, -1, 0) not in visit_list:
          visit_list.append(plus(square, -1, 0))
      if isConnected(blue, orange, square, 'up'):
        if plus(square, 0, -1) not in visit_list:
          visit_list.append(plus(square, 0, -1))
      if isConnected(blue, orange, square, 'right'):
        if plus(square, 1, 0) not in visit_list:
          visit_list.append(plus(square, 1, 0))
      if isConnected(blue, orange, square, 'down'):
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
    if isConnected(blue, orange, square, 'left'):
      if plus(square, -1, 0) not in visit_list:
        visit_list.append(plus(square, -1, 0))
    if isConnected(blue, orange, square, 'up'):
      if plus(square, 0, -1) not in visit_list:
        visit_list.append(plus(square, 0, -1))
    if isConnected(blue, orange, square, 'right'):
      if plus(square, 1, 0) not in visit_list:
        visit_list.append(plus(square, 1, 0))
    if isConnected(blue, orange, square, 'down'):
      if plus(square, 0, 1) not in visit_list:
        visit_list.append(plus(square, 0, 1))
    j += 1
  return True

# Stage 0: Calculate all blue and orange paths.
stageStart = time()
blues = findSolutions(('blue', Path((3, 4)), Path((3, 0))))
blues.append(Path((3, 4))) # Added in for the start point
oranges = findSolutions(('orange', Path((3, 4)), Path((3, 0))))
oranges.append(Path((3, 0))) # Added in for the start point
# These are initialized separately because A. they aren't valid paths, and B. they need to have a children array defined (as a base case).
path_combos_b = {Path((3, 4)):{Path((3, 0)):{'parents':[],'cost':None, 'pCost': (0, None)}}}
path_combos_o = {Path((3, 0)):{Path((3, 4)):{'parents':[],'cost':None, 'pCost': (0, None)}}}
for blue in blues:
  for orange in oranges:
    if isValidSolution(blue, orange):
      if blue not in path_combos_b:
        path_combos_b[blue] = {}
      path_combos_b[blue][orange] = {'parents':[], 'cost':None, 'pCost':None}
      if orange not in path_combos_o:
        path_combos_o[orange] = {}
      path_combos_o[orange][blue] = {'parents':[], 'cost':None, 'pCost':None}
stageEnd = time()
print 'Stage 0 done in', format_time(stageEnd-stageStart)
stageStart = stageEnd
exits_b = []
exits_o = []
to_visit = deque([(Path((3, 4)), Path((3, 0)), 'blue')]) # Base starting point: Each path is length 1, and we start on the blue side.
while len(to_visit) > 0:
  blue, orange, color = to_visit.popleft()
  if color == 'blue' or orange[-1][1] == 0: # Orange path connects to blue side or we're on the blue side, look for a new blue path.
    if orange in path_combos_o:
      for blue_new in blues:
        if blue_new == blue:
          continue
        if blue_new in path_combos_o[orange]: # Valid path
          path_combos_b[blue_new][orange]['parents'].append((blue, orange))
          path_combos_o[orange][blue_new]['parents'].append((blue, orange))
          if path_combos_o[orange][blue_new]['pCost'] == None:
            path_combos_b[blue_new][orange]['pCost'] = (path_combos_b[blue][orange]['pCost'][0]+len(blue), (blue, orange))
            path_combos_o[orange][blue_new]['pCost'] = (path_combos_o[orange][blue]['pCost'][0]+len(blue), (blue, orange))
            to_visit.append((blue_new, orange, 'blue'))
          if path_combos_o[orange][blue]['pCost'][0] + len(blue) < path_combos_o[orange][blue_new]['pCost'][0]:
            path_combos_b[blue_new][orange]['pCost'] = (path_combos_b[blue][orange]['pCost'][0]+len(blue), (blue, orange))
            path_combos_o[orange][blue_new]['pCost'] = (path_combos_o[orange][blue]['pCost'][0]+len(blue), (blue, orange))
          if blue_new[-1] == (0, 3) and len(orange) > 1: # Found a solution!
            path_combos_b[blue_new][orange]['cost'] = (0, None)
            exits_b.append((blue_new, orange))
  if color == 'orange' or blue[-1][1] == 4: # Blue path connects to orange side or we're on the orange side, look for a new orange path.
    if blue in path_combos_b:
      for orange_new in oranges:
        if orange_new == orange:
          continue
        if orange_new in path_combos_b[blue]: # Valid path
          path_combos_b[blue][orange_new]['parents'].append((blue, orange))
          path_combos_o[orange_new][blue]['parents'].append((blue, orange))
          if path_combos_b[blue][orange_new]['pCost'] == None:
            path_combos_b[blue][orange_new]['pCost'] = (path_combos_b[blue][orange]['pCost'][0]+len(orange), (blue, orange))
            path_combos_o[orange_new][blue]['pCost'] = (path_combos_o[orange][blue]['pCost'][0]+len(orange), (blue, orange))
            to_visit.append((blue, orange_new, 'orange'))
          if path_combos_b[blue][orange]['pCost'][0] + len(orange) < path_combos_b[blue][orange_new]['pCost'][0]:
            path_combos_b[blue][orange_new]['pCost'] = (path_combos_b[blue][orange]['pCost'][0]+len(orange), (blue, orange))
            path_combos_o[orange_new][blue]['pCost'] = (path_combos_o[orange][blue]['pCost'][0]+len(orange), (blue, orange))
          if orange_new[-1] == (0, 3) and len(blue) > 1: # Found a solution!
            path_combos_o[orange_new][blue]['cost'] = (0, None)
            exits_o.append((blue, orange_new))

stageEnd = time()
print 'Stage 1 done in', format_time(stageEnd-stageStart)
stageStart = stageEnd
# Stage 2: Calculate distance to exit at each node

# pPath = (blue, orange) for the parent
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
  blue, orange = to_visit.popleft()
  for parent in path_combos_b[blue][orange]['parents']:
    if update_cost(
      parent,
      path_combos_b[parent[0]][parent[1]],
      (blue, orange),
      path_combos_b[blue][orange]
    ):
      to_visit.append(parent)

# Calculates cost at each node to reach an orange solution
to_visit = deque(exits_o)
while len(to_visit) > 0:
  blue, orange = to_visit.popleft()
  for parent in path_combos_o[orange][blue]['parents']:
    if update_cost(
      parent,
      path_combos_o[parent[1]][parent[0]],
      (blue, orange),
      path_combos_o[orange][blue]
    ):
      to_visit.append(parent)

stageEnd = time()
print 'Stage 2 done in', format_time(stageEnd-stageStart)
stageStart = stageEnd
# Stage 3: Find and print the optimal solutions.

min_both = (999, None)
min_single = (999, None)

for exit in exits_b:
  blue, orange = exit
  cost_single = path_combos_b[blue][orange]['pCost'][0]
  cost_both = cost_single+path_combos_o[orange][blue]['cost'][0]
  if cost_single < min_single[0]:
    min_single = (cost_single, exit)
  if cost_both < min_both[0]:
    min_both = (cost_both, exit)

for exit in exits_o:
  blue, orange = exit
  cost_single = path_combos_o[orange][blue]['pCost'][0]
  cost_both = cost_single+path_combos_b[blue][orange]['cost'][0]
  if cost_single < min_single[0]:
    min_single = (cost_single, exit)
  if cost_both < min_both[0]:
    min_both = (cost_both, exit)

print min_single # 16
print min_both # 37
