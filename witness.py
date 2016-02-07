from Queue import Queue
from threading import Lock, Thread
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
interesting_points = [(2, 0), (3, 1), (0, 2), (0, 3), (5, 2), (5, 3), (0, 1), (5, 1)]

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
      self.color, self.blue_solved, self.orange_solved, self.blue_path, self.orange_path, self.history, self.uuid = root
      return
    super(PartialSolution, self).__init__()

  def isValid(self, color, (x, y)):
    if x < 0 or x > 6:
      return False
    if y < 0 or y > 4:
      return False
    if (x, y) in self.blue_path:
      return False
    if (x, y) in self.orange_path:
      return False
    if (x, y) in banned_connections:
      if color == 'blue' and banned_connections[(x, y)] == self.blue_path[-1]:
        return False
      if color == 'orange' and banned_connections[(x, y)] == self.orange_path[-1]:
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

  def debug(self):
    global longest, startTime
    if len(self.history) > longest:
      longest = len(self.history)
      print time()-startTime
      print self.uuid, len(self.history), self.history
    # if self.blue_path == [(3, 4), (4, 4), (5, 4), (6, 4), (6, 3), (6, 2), (5, 2), (5, 3), (4, 3), (3, 3), (2, 3), (2, 4), (1, 4), (1, 3), (1, 2), (1, 1), (0, 1), (0, 0)]:
      # print 1, self.uuid
      # if self.orange_path == [(3, 0), (2, 0), (2, 1), (3, 1), (3, 2), (4, 2), (4, 1), (5, 1), (5, 0), (6, 0)]:
        # print 2, self.uuid

  # Check if a square is contiguous to another square in the given direction.
  def isConnected(self, square, dir):
    x, y = square
    if dir == 'left':
      if x == 0:
        return False
      try:
        index = self.blue_path.index((x, y))
        if index > 0 and self.blue_path[index-1] == (x, y+1):
          return False
        if index < len(self.blue_path)-1 and self.blue_path[index+1] == (x, y+1):
          return False
      except ValueError:
        pass
      try:
        index = self.orange_path.index((x, y))
        if index > 0 and self.orange_path[index-1] == (x, y+1):
          return False
        if index < len(self.orange_path)-1 and self.orange_path[index+1] == (x, y+1):
          return False
      except ValueError:
        pass
    elif dir == 'up':
      if y == 0:
        return False
      try:
        index = self.blue_path.index((x, y))
        if index > 0 and self.blue_path[index-1] == (x+1, y):
          return False
        if index < len(self.blue_path)-1 and self.blue_path[index+1] == (x+1, y):
          return False
      except ValueError:
        pass
      try:
        index = self.orange_path.index((x, y))
        if index > 0 and self.orange_path[index-1] == (x+1, y):
          return False
        if index < len(self.orange_path)-1 and self.orange_path[index+1] == (x+1, y):
          return False
      except ValueError:
        pass
    elif dir == 'right':
      if x == 5:
        return False
      try:
        index = self.blue_path.index((x+1, y+1))
        if index > 0 and self.blue_path[index-1] == (x+1, y):
          return False
        if index < len(self.blue_path)-1 and self.blue_path[index+1] == (x+1, y):
          return False
      except ValueError:
        pass
      try:
        index = self.orange_path.index((x+1, y+1))
        if index > 0 and self.orange_path[index-1] == (x+1, y):
          return False
        if index < len(self.orange_path)-1 and self.orange_path[index+1] == (x+1, y):
          return False
      except ValueError:
        pass
    elif dir == 'down':
      if y == 3:
        return False
      try:
        index = self.blue_path.index((x+1, y+1))
        if index > 0 and self.blue_path[index-1] == (x, y+1):
          return False
        if index < len(self.blue_path)-1 and self.blue_path[index+1] == (x, y+1):
          return False
      except ValueError:
        pass
      try:
        index = self.orange_path.index((x+1, y+1))
        if index > 0 and self.orange_path[index-1] == (x, y+1):
          return False
        if index < len(self.orange_path)-1 and self.orange_path[index+1] == (x, y+1):
          return False
      except ValueError:
        pass
    return True

  def isValidSolution(self, verbose=False):
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
        if self.isConnected(square, 'left'):
          if verbose:
            print square, 'is connected to the left'
          if plus(square, (-1, 0)) not in visit_list:
            visit_list.append(plus(square, (-1, 0)))
        if self.isConnected(square, 'up'):
          if verbose:
            print square, 'is connected up'
          if plus(square, (0, -1)) not in visit_list:
            visit_list.append(plus(square, (0, -1)))
        if self.isConnected(square, 'right'):
          if verbose:
            print square, 'is connected to the right'
          if plus(square, (1, 0)) not in visit_list:
            visit_list.append(plus(square, (1, 0)))
        if self.isConnected(square, 'down'):
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
      if self.isConnected(square, 'left'):
        if verbose:
          print square, 'is connected to the left'
        if plus(square, (-1, 0)) not in visit_list:
          visit_list.append(plus(square, (-1, 0)))
      if self.isConnected(square, 'up'):
        if verbose:
          print square, 'is connected up'
        if plus(square, (0, -1)) not in visit_list:
          visit_list.append(plus(square, (0, -1)))
      if self.isConnected(square, 'right'):
        if verbose:
          print square, 'is connected to the right'
        if plus(square, (1, 0)) not in visit_list:
          visit_list.append(plus(square, (1, 0)))
      if self.isConnected(square, 'down'):
        if verbose:
          print square, 'is connected down'
        if plus(square, (0, 1)) not in visit_list:
          visit_list.append(plus(square, (0, 1)))
      j += 1
    if verbose:
      print 'Valid solution found'
    return True

  def run(self):
    while True:
      from Queue import Empty
      global q
      try:
        self = q.get(True, 1)
      except Empty:
        return
      self.debug()
      if self.color == 'blue':
        head = self.blue_path[-1]
        # Reached the exit for the first time and the door is open
        if head == (0, 3) and not self.blue_solved and len(self.orange_path) > 1:
          if self.isValidSolution():
            newSolution = self.clone()
            newSolution.blue_solved = True
            newSolution.history.append(['blue']+newSolution.blue_path)
            if newSolution.orange_solved:
              print 'Found solution at', uuid, self.history
              q.task_done()
              continue
            # If we haven't solved orange yet, we need to find that solution. Restart our blue path and keep looking
            newSolution.blue_path = [(3, 4)]
            q.put(newSolution)
        elif head == (0, 0) or head == (6, 0) or head == (0, 4) or head == (6, 4):
          if self.isValidSolution():
            # The obvious choice is to then travel to the other side, and build a new path back
            newSolution = self.clone()
            newSolution.color = 'orange'
            newSolution.history.append(['blue']+newSolution.blue_path)
            newSolution.orange_path = [(3, 0)]
            q.put(newSolution)
            # The non-obvious choice is to travel to the other side, RESET THE PATH there, and then make another blue solution. The only time this is useful is if we've already solved one of the two sides.
            if (self.blue_solved or self.orange_solved):
              newSolution = self.clone()
              newSolution.history.append(['blue']+newSolution.blue_path)
              newSolution.history.append(['orange', (3, 0)])
              newSolution.orange_path = [(3, 0)]
              newSolution.blue_path = [(3, 4)]
              # q.put(newSolution)
        # Below are the possible ways to extend the path. Complexity arises because:
        # 1. Steps forward should avoid forming loops (pictured in the comments, with o as the head and .. as the potential next step)
        # 1a. Loops are OK when capturing an interesting point, such as a star or a square.
        # 1b. Loops are OK when they hit the edge of the board, as this can divide stars.
        # 2. Steps forward need to not collide with other paths (handled in isValid)
        # 3. Steps forward need to be in bounds (handled in isValid)
        # 4. Steps forward need to respect the breaks in the board (handled in isValid)

        # o..  +--
        # |    |
        # +--  o..
        if len(self.blue_path) < 3 or head[0] < 5 or (
        (plus(head, (1, 1)) != self.blue_path[-3] or
         plus(head, (0, 0)) in interesting_points) and
        (plus(head, (1, -1)) != self.blue_path[-3] or
         plus(head, (0, -1)) in interesting_points)):
          if self.isValid(self.color, plus(head, (1, 0))):
            newSolution = self.clone()
            newSolution.blue_path.append(plus(head, (1, 0)))
            q.put(newSolution)
        # +-o  o-+
        # | .  . |
        # | .  . |
        if len(self.blue_path) < 3 or head[1] < 3 or (
        (plus(head, (-1, 1)) != self.blue_path[-3] or
         plus(head, (-1, 0)) in interesting_points) and
        (plus(head, (1, 1)) != self.blue_path[-3] or
         plus(head, (0, 0)) in interesting_points)):
          if self.isValid(self.color, plus(head, (0, 1))):
            newSolution = self.clone()
            newSolution.blue_path.append(plus(head, (0, 1)))
            q.put(newSolution)
        # --+  ..o
        #   |    |
        # ..o  --+
        if len(self.blue_path) < 3 or head[0] > 1 or (
        (plus(head, (-1, -1)) != self.blue_path[-3] or
         plus(head, (-1, -1)) in interesting_points) and
        (plus(head, (-1, 1)) != self.blue_path[-3] or
         plus(head, (-1, 0)) in interesting_points)):
          if self.isValid(self.color, plus(head, (-1, 0))):
            newSolution = self.clone()
            newSolution.blue_path.append(plus(head, (-1, 0)))
            q.put(newSolution)
        # . |  | .
        # . |  | .
        # o-+  +-o
        if len(self.blue_path) < 3 or head[1] > 1 or (
        (plus(head, (1, -1)) != self.blue_path[-3] or
         plus(head, (0, -1)) in interesting_points) and
        (plus(head, (-1, -1)) != self.blue_path[-3] or
         plus(head, (-1, -1)) in interesting_points)):
          if self.isValid(self.color, plus(head, (0, -1))):
            newSolution = self.clone()
            newSolution.blue_path.append(plus(head, (0, -1)))
            q.put(newSolution)
      elif self.color == 'orange':
        head = self.orange_path[-1]
        # Reached the exit for the first time and the door is open
        if head == (0, 3) and not self.orange_solved and len(self.blue_path) > 1:
          if self.isValidSolution():
            newSolution = self.clone()
            newSolution.orange_solved = True
            newSolution.history.append(['orange']+newSolution.orange_path)
            if newSolution.blue_solved:
              print 'Found solution at', uuid, newSolution.history
              q.task_done()
              continue
            # If we haven't solved blue yet, we need to find that solution. Restart our orange path and keep looking
            newSolution.orange_path = [(3, 0)]
            q.put(newSolution)
        elif head == (0, 0) or head == (6, 0) or head == (0, 4) or head == (6, 4):
          if self.isValidSolution():
            # The obvious choice is to then travel to the other side, and build a new path back
            newSolution = self.clone()
            newSolution.color = 'blue'
            newSolution.history.append(['orange']+newSolution.orange_path)
            newSolution.blue_path = [(3, 0)]
            q.put(newSolution)
            # The non-obvious choice is to travel to the other side, RESET THE PATH there, and then make another orange solution. This is potentially useful at any time.
            newSolution = self.clone()
            newSolution.history.append(['orange']+newSolution.orange_path)
            newSolution.history.append(['blue', (3, 4)])
            newSolution.orange_path = [(3, 0)]
            newSolution.blue_path = [(3, 4)]
            # q.put(newSolution)

        # o..  +--
        # |    |
        # +--  o..
        if len(self.orange_path) < 3 or (
        (plus(head, (1, 1)) != self.orange_path[-3] or
         plus(head, (0, 0)) in interesting_points) and
        (plus(head, (1, -1)) != self.orange_path[-3] or
         plus(head, (0, -1)) in interesting_points)):
          if self.isValid(self.color, plus(head, (1, 0))):
            newSolution = self.clone()
            newSolution.orange_path.append(plus(head, (1, 0)))
            q.put(newSolution)
        # +-o  o-+
        # | .  . |
        # | .  . |
        if len(self.orange_path) < 3 or (
        (plus(head, (-1, 1)) != self.orange_path[-3] or
         plus(head, (-1, 0)) in interesting_points) and
        (plus(head, (1, 1)) != self.orange_path[-3] or
         plus(head, (0, 0)) in interesting_points)):
          if self.isValid(self.color, plus(head, (0, 1))):
            newSolution = self.clone()
            newSolution.orange_path.append(plus(head, (0, 1)))
            q.put(newSolution)
        # --+  ..o
        #   |    |
        # ..o  --+
        if len(self.orange_path) < 3 or (
        (plus(head, (-1, -1)) != self.orange_path[-3] or
         plus(head, (-1, -1)) in interesting_points) and
        (plus(head, (-1, 1)) != self.orange_path[-3] or
         plus(head, (-1, 0)) in interesting_points)):
          if self.isValid(self.color, plus(head, (-1, 0))):
            newSolution = self.clone()
            newSolution.orange_path.append(plus(head, (-1, 0)))
            q.put(newSolution)
        # . |  | .
        # . |  | .
        # o-+  +-o
        if len(self.orange_path) < 3 or (
        (plus(head, (1, -1)) != self.orange_path[-3] or
         plus(head, (0, -1)) in interesting_points) and
        (plus(head, (-1, -1)) != self.orange_path[-3] or
         plus(head, (-1, -1)) in interesting_points)):
          if self.isValid(self.color, plus(head, (0, -1))):
            newSolution = self.clone()
            newSolution.orange_path.append(plus(head, (0, -1)))
            q.put(newSolution)
      q.task_done()

global uuid
uuid = 0
global done
done = False
global q
q = Queue()
global longest
longest = 0
# Color, blue solved, orange solved, blue path, orange path, history, uuid
q.put(PartialSolution(root=('blue', False, False, [(3, 4)], [(3, 0)], [], uuid)))
threads = []
global startTime
startTime = time()
for i in range(1): # Number of threads
  thread = PartialSolution()
  threads.append(thread)
  thread.start()
for thread in threads:
  thread.join()
print 'Puzzle solved in', time()-startTime, 'seconds'
