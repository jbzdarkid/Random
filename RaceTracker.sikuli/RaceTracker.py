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
#		- Solution:
#		Maintain a list of frames, captured every {30 sec}. For 1 minute, watch for frame 0 {0-60 sec delay}.
#		For the next minute, watch for frame 1 {30-90 sec delay}. Etc, etc. Delays are calculated twice as slowly, but twice as accurately.

from time import time
from threading import Lock, Thread
import sys

Settings.WaitScanRate = 60 # 60 scans per sec, this is 20x faster than normal!
setThrowException(False) # If a match fails, returns None rather than raising exception FindFailed
ACCURACY = int(input('Frequency of checkpoints (image captures), in seconds.\nSuggested is 30: '))
n = int(input('Number of runners: '))
regions = [None]*n
popup('For each region, hover your mouse over a corner, press caps lock,\nmove to the other corner, and then release caps lock.')
for region in regions
	while (!Env.isLockOn(Key.CAPS_LOCK)):
		sleep(0.1)
	l1 = Env.getMouseLocation()
	while (Env.isLockOn(Key.CAPS_LOCK)):
		sleep(0.1)
	l2 = Env.getMouseLocation()
	x = l1.getX()
	y = l1.getY()
	if l2.getX() < x:
		x = l2.getX()
		w = l1.getX()-x
	else:
		w = l2.getX()-x
	if l2.getY() < y:
		y = l2.getY()
		h = l1.getY()-y
	else:
		h = l2.getY()-y
	region = Region(x, y, w, h)
	region.highlight()

for region in regions:
	region.highlight() # De-highlight

challenges = [[] for _ in range(n)]
responses = [[]]
threads = [None]*n
# Get regions w/ mouse clicks, highlight to confirm
start_time = time()

for i in range(n):
	threads[i] = Thread(target=watch, kwargs={'num':i})

while (True): # This generates the comparison frames.
	for i in range(len(regions)):
		#challenges[i].append(regions[i].capture())
		print ''
	sleep(ACCURACY)

def watch(num):
	region = regions[num]
	while (True):
		c = 0
		match = None
		while (match == None):
			challenge = challenges[c]
			match = region.wait(challenge, ACCURACY*2)
			c += 1
		responses[num][c-1] = time()