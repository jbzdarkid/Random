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
    if len(self.history) > 0:
      if self.history[:1][0][:10] == ['blue', (3, 4), (4, 4), (5, 4), (6, 4), (6, 3), (6, 2), (5, 2), (5, 3), (4, 3)]:
        print 0, uuid, self.history
      if self.history[:1] == [['blue', (3, 4), (4, 4), (5, 4), (6, 4), (6, 3), (6, 2), (5, 2), (5, 3), (4, 3), (3, 3), (2, 3), (2, 4), (1, 4), (1, 3), (1, 2), (1, 1), (0, 1), (0, 0)]]:
        print 1, uuid, self.history
        raw_input()
    # print 'Color', self.color
    # print 'Blue:', self.blue_solved, 'Orange:', self.orange_solved
    # print 'Blue path:', self.blue_path
    # print 'Orange path:', self.orange_path
    # print 'UUID:', uuid
    # print self.isValidSolution(verbose=True)

  def isValidSolution(self, verbose=False):
    # If any corner around a star is included in a region, the star is included in that region.
    stars = [
      [(2, 0), (2, 1), (3, 0), (3, 1)],
      [(3, 1), (3, 2), (4, 1), (4, 2)],
      [(0, 2), (0, 3), (1, 2), (1, 3)],
      [(0, 3), (0, 4), (1, 3), (1, 4)],
      [(5, 2), (5, 3), (6, 2), (6, 3)],
      [(5, 3), (5, 4), (6, 3), (6, 4)]
    ]
    for i in range(3): # There are 6 stars, and each time we find one it needs to remove exactly 1 other star.
      visited = {}
      to_visit = stars.pop()
      if verbose:
        print 'Iteration', i, 'selected star:', to_visit
      while len(to_visit) > 0:
        square = to_visit.pop()
        if square in visited:
          continue
        # Regions are contiguous over line breaks, so no color spec.
        if self.isValid('none', square):
          visited[square] = True
          to_visit += [
            plus(square, (-1, 0)),
            plus(square, (1, 0)),
            plus(square, (0, -1)),
            plus(square, (0, 1))
          ]
        else:
          visited[square] = False
      if verbose:
        print 'Done visiting, continguous region:', to_visit
      new_stars = []
      for star in stars:
        if star[0] in visited and visited[star[0]]:
          continue
        if star[1] in visited and visited[star[1]]:
          continue
        if star[2] in visited and visited[star[2]]:
          continue
        if star[3] in visited and visited[star[3]]:
          continue
        new_stars.append(star)
      if len(new_stars) != len(stars) - 1:
        return False # Removed more or less than 1 other star
      if verbose:
        print len(new_stars), 'new stars:', new_stars
      stars = new_stars
    # All stars verified, now check the squares
    if verbose:
      print 'Valid solution with stars found'

    white_square = [(5, 1), (5, 2), (6, 1), (6, 2)]
    # Black square
    to_visit = [(0, 1), (0, 2), (1, 1), (1, 2)]
    visited = {}
    while len(to_visit) > 0:
      square = to_visit.pop()
      if square in visited:
        continue
      # Regions are contiguous over line breaks, so no color spec.
      if self.isValid('none', square):
        visited[square] = True
        to_visit += [
          plus(square, (-1, 0)),
          plus(square, (1, 0)),
          plus(square, (0, -1)),
          plus(square, (0, 1))
        ]
      else:
        visited[square] = False
    if white_square[0] in visited and visited[white_square[0]]:
      return False
    if white_square[1] in visited and visited[white_square[1]]:
      return False
    if white_square[2] in visited and visited[white_square[2]]:
      return False
    if white_square[3] in visited and visited[white_square[3]]:
      return False

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
      self.debug()
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
for i in range(1): # Number of threads
  thread = PartialSolution()
  threads.append(thread)
  thread.start()
for thread in threads:
  thread.join()
print 'Puzzle solved in', time()-startTime, 'seconds'
