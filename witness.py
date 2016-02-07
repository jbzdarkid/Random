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
	(0,2):[0,3],
	(0,3):[0,2],
	(0,3):[0,4],
	(0,4):[0,3],
	(1,0):[2,0],
	(2,0):[1,0],
	(4,0):[5,0],
	(5,0):[4,0]
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
    # uuid = 177102 is the first step in the given solution
    print 'Color', self.color
    print 'Blue:', self.blue_solved, 'Orange:', self.orange_solved
    print 'Blue path:', self.blue_path
    print 'Orange path:', self.orange_path
    print 'UUID:', uuid
    print self.isValidSolution(verbose=True)

  # Check if a square is contiguous to a square in the given direction.
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

  # TODO: Handle the following:
  # Solve blue, go to orange
  # Solve orange, go to blue
  # Reset blue, go to orange
  # Re-solve orange, go to blue
  # Solve blue, exit
  def run(self):
    global done
    while not done:
      from Queue import Empty
      global q
      try:
        self = q.get(True, 1)
      except Empty:
        return
      # self.debug()
      # raw_input()
      if self.color == 'blue':
        head = self.blue_path[-1]
        if head == (0, 3) and len(self.orange_path) > 0:
          if self.isValidSolution():
            # Reached the exit! Blue is now solved.
            self.blue_solved = True
            self.history.append(['blue']+self.blue_path)
            if self.orange_solved:
              done = True
              print uuid, self.history
              return
        elif head == (0, 0) or head == (6, 0):
          if self.isValidSolution():
            newSolution = self.clone()
            newSolution.color = 'orange'
            newSolution.orange_path = [(3, 0)]
            q.put(newSolution)
        if self.isValid(self.color, plus(head, (-1, 0))):
          newSolution = self.clone()
          newSolution.blue_path.append(plus(head, (-1, 0)))
          q.put(newSolution)
        if self.isValid(self.color, plus(head, (1, 0))):
          newSolution = self.clone()
          newSolution.blue_path.append(plus(head, (1, 0)))
          q.put(newSolution)
        if self.isValid(self.color, plus(head, (0, -1))):
          newSolution = self.clone()
          newSolution.blue_path.append(plus(head, (0, -1)))
          q.put(newSolution)
        if self.isValid(self.color, plus(head, (0, 1))):
          newSolution = self.clone()
          newSolution.blue_path.append(plus(head, (0, 1)))
          q.put(newSolution)
      elif self.color == 'orange':
        head = self.orange_path[-1]
        if head == (0, 3) and len(self.orange_path) > 0:
          if self.isValidSolution():
            # Reached the exit! Orange is now solved.
            self.orange_solved = True
            print 'Found orange path'
            self.history.append(['orange']+self.orange_path)
            if self.blue_solved:
              done = True
              print uuid, self.history
              return
        elif head == (0, 4) or head == (6, 4):
          if self.isValidSolution():
            newSolution = self.clone()
            newSolution.color = 'blue'
            newSolution.blue_path = [(3, 4)]
            q.put(newSolution)
        if self.isValid(self.color, plus(head, (-1, 0))):
          newSolution = self.clone()
          newSolution.orange_path.append(plus(head, (-1, 0)))
          q.put(newSolution)
        if self.isValid(self.color, plus(head, (1, 0))):
          newSolution = self.clone()
          newSolution.orange_path.append(plus(head, (1, 0)))
          q.put(newSolution)
        if self.isValid(self.color, plus(head, (0, -1))):
          newSolution = self.clone()
          newSolution.orange_path.append(plus(head, (0, -1)))
          q.put(newSolution)
        if self.isValid(self.color, plus(head, (0, 1))):
          newSolution = self.clone()
          newSolution.orange_path.append(plus(head, (0, 1)))
          q.put(newSolution)
      q.task_done()

global uuid
uuid = 0
global done
done = False
global q
q = Queue()
# Color, blue solved, orange solved, blue path, orange path, history, uuid
q.put(PartialSolution(root=('blue', False, False, [(3, 4)], [(3, 0)], [], uuid)))
threads = []
startTime = time()
for i in range(16): # Number of threads
  thread = PartialSolution()
  threads.append(thread)
  thread.start()
for thread in threads:
  thread.join()
print 'Puzzle solved in', time()-startTime, 'seconds'
