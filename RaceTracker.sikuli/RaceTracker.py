# Initially, I need to determine who is in the lead:
#	- Get current screenshot from all racers
#	- Watch every stream for every other stream's key
#	- Simple case: Within a reasonable amount of time (close race), each key is spotted: One stream sees n-1 keys, one n-2, ...
#	- Complex case 1: Severe disparity between runners.
#		- Solution: Create comparable groups. Maintain any non-found frames until groups are merged.
#	- Complex case 2: Chosen frame is unique (does not appear)
#		- Solution: Allow ties. If two runners match no frames (both signifying last place), allow them to be tied for this position.
#	- Complex case 3: Chosen frame is ambiguous (appears twice)
#		- Scenario:
#		- Runner A lists frame A. Runner B identifies frame A, but is in fact ahead of runner A.
#		- Similary, Runner A identifies frame B, and is correctly behind.
#		- Solution is probably to double-key (i.e. 2+ continuous frames) 
# General idea is to create an array of frames (challenges) and for each thread/runner to have an associated list of times (responses)
# Both of these should be read/write safe, using a semaphore...? Possibly threads will make local copies.
# We're going need to do complete challenges to reconstruct order, rather than allowing only the leader to challenge.
# 

from time import time
from threading import thread, lock

setThrowException(False) # If a match fails, returns None rather than raising exception FindFailed
challenges = []
responses = [[]]
challenge_lock = Lock() # Used when creating a challenge.
start_time = time()
threshold = 5*60 # 5 minute threshold
threads = []
keep_alive = True

def create_challenge(region, index):
	challenge_lock.acquire()
	challenges.append(capture(region)) # Current frame
	time = time()
	for i in range(len(responses)):
		if i == index:
			r.append(time)
		else:
			r.append(None)
	challenge_lock.release()
	return time

def t(name, x, y, w, h, index):
	responses.append([])
	region = Region(x, y, w, h)
	region.setAutoWaitTimeout(1) # Seconds
	last_response = create_challenge(region, index)
	while keep_alive:
		match = None
		i = 0
		while (match is None and time()-last_response < threshold*2):
			active_challenges = 0
			for i in range(len(challenges)):
				if responses[index][i] is not None: # Challenge already completed
					continue
				active_challenges += 1
				if active_challenges > len(threads)*2: # Don't consider challenges that are too recent. ***Warning: Limits number of acceptable failures.
					break
				match = region.wait(challenges[i])
		responses[index][i] = time() # Challenge completed
		if time() - last_response > threshold:
			last_response = create_challenge(region, index)

# Get the regions
# Start threads
# On a timer(?) update a spaghetti graph.

