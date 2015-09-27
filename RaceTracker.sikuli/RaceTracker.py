# Suggestion: When potential difference between runners is > 20% of the time (i.e. frame 0 at time 5, difference = 2), restart calc.
#
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
from threading import Thread
from config import config

Settings.WaitScanRate = config['RaceTracker']['Scan Rate']
30 # 30 scans per sec, this is 10x faster than normal!
setThrowException(False) # If a match fails, returns None rather than raising exception FindFailed
n = int(input('Number of runners: '))
regions = [None]*n
positions = [None]*n
print positions
for i in range(n):
	positions[i] = [i]
overtakes = [0]*n

popup('For each region, hover your mouse over a corner, press caps lock,\nmove to the other corner, and then release caps lock.')
App.focus('Google Chrome')
min_width = Screen().getW()
min_height = Screen().getH()
max_width = 0
max_height = 0
for i in range(n):
	while (not Env.isLockOn(Key.CAPS_LOCK)):
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
	if min_width > w:
		min_width = w
	if max_width < w:
		max_width = w
	if min_height > h:
		min_height = h
	if max_height < h:
		max_height = h
	region = Region(x, y, w, h)
	region.highlight() # Highlight
	regions[i] = [region]
sleep(1)
for i in range(n):
	regions[i][0].highlight() # De-highlight
	error = 0
	if error < max_width - regions[i][0].getW():
		error = max_width - regions[i][0].getW()
	if error < max_height - regions[i][0].getH():
		error = max_height - regions[i][0].getH()
	regions[i].append(error)
	regions[i][0].setW(min_width)
	regions[i][0].setH(min_height)

challenges = [[] for _ in range(n)]
responses = [[]]
threads = []
start_time = time()

# For a given match object, determine which racer it refers to.
def get_racer_num(match):
	midX = match.getX()+match.getW()/2.0
	midY = match.getY()+match.getH()/2.0
	for i in range(n):
		if regions[i][0].getX() < midX and regions[i][0].getX() + regions[i][0].getW() > midX:
			if regions[i][0].getY() < midY and regions[i][0].getY() + regions[i][0].getH() > midY:
				return i # This assumes no overlapping regions.

def watch(num):
	while (True):
		c = 0
		match = None
		while (match == None):
			challenge = challenges[c]
			match = Screen().wait(challenge, config['RaceTracker']['Accuracy']*config['RaceTracker']['Redundancy']) # Add comment here.
			c += 1
		print match
		found_num = get_racer_num(match)
		if positions[found_num] - positions[num] == -1: # The player ahead of us
			overtakes[num] += 1
		elif positions[found_num] - positions[num] == 1: # The player behind us
			overtakes[num+1] == 0
		elif positions[found_num] - positions[num] == 2: # The player behind the player behind us
			overtakes[num+2] += 1
		
		responses[num][c-1] = time()

for i in range(n):
	threads.append(Thread(target=watch, kwargs={'num':i}))

for _ in range(10): # This generates the comparison frames.
	for i in range(len(regions)):
		challenges[i].append(Screen().capture(regions[i][0]))
	sleep(config['RaceTracker']['Accuracy'])

# This thread (main) is now going to generate the graphical output. The most straightforward way to do this is a spaghetti graph.
# With only knowledge of the difference between runners, if there is no new data, assume linear.
# Interpolation between should probably be linear.

import pprint
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(challenges)
pp.pprint(responses)
