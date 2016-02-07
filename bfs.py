from Queue import Queue
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
      self.uuid = root
      return
    super(PartialSolution, self).__init__()

  def clone(self):
    return PartialSolution(root=(
    	getUUID()
    ))

  def run(self):
    while True:
      from Queue import Empty
      global q
      try:
        self = q.get(True, 1) # Solutions can potentially go through a bottleneck. If this happens, the queue might run dry breifly. I don't want threads to close during this time.
      except Empty:
        return
      if self.uuid >= 100:
	      q.task_done()
	      continue
      for i in range(5):
				q.put(self.clone())
      q.task_done()

global uuid
uuid = 0
global q
q = Queue()
q.put(PartialSolution(root=(uuid)))
threads = []
startTime = time()
for i in range(16): # Number of threads
  thread = PartialSolution()
  threads.append(thread)
  thread.start()
for thread in threads:
  thread.join()
print 'Counted to 100 in', time()-startTime, 'seconds'