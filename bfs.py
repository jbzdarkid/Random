from Queue import Queue, Empty
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

def worker(q, solutions):
  while True:
    try:
      task = q.get(True, 1) # Solutions can potentially go through a bottleneck. If this happens, the queue might run dry breifly. I don't want threads to close during this time.
    except Empty:
      return
    if task['id'] >= 100:
      solutions.append(task)
      continue
    for _ in range(5):
      task['id'] += 1
      task['uuid'] = getUUID()
      q.put(task)
    continue

global uuid
uuid = 0
q = Queue()
solutions = []
q.put({'id':0, 'uuid':uuid})
threads = []
startTime = time()
for i in range(16): # Number of threads
  thread = Thread(target=worker, args=(q, solutions))
  threads.append(thread)
  thread.start()
for thread in threads:
  thread.join()
print 'Counted to 100 in', time()-startTime, 'seconds'
print 'Found', len(solutions), 'solutions'