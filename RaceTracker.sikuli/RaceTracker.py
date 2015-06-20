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

Settings.WaitScanRate = 30 # 30 scans per sec, this is 10x faster than normal!
setThrowException(False) # If a match fails, returns None rather than raising exception FindFailed
ACCURACY = int(input('Frequency of checkpoints (image captures), in seconds.\nSuggested is 30: '))
REDUNDANCY = 2 # Also effects timeliness of information. If a runner is 10 minutes behind, and this value is at 2,
# then this information will be discovered after 20 minutes.
n = int(input('Number of runners: '))
regions = []
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
	regions.append([region])
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
# Get regions w/ mouse clicks, highlight to confirm
start_time = time()

def watch(num):
	region = regions[num][0].nearby(regions[num][1])
	while (True):
		c = 0
		match = None
		while (match == None):
			challenge = challenges[c]
			match = Screen().wait(challenge, ACCURACY*REDUNDANCY) #?
			c += 1
		responses[num][c-1] = time()
		# I'm not getting any matches.

for i in range(n):
	threads.append(Thread(target=watch, kwargs={'num':i}))

for _ in range(10): # This generates the comparison frames.
	for i in range(len(regions)):
		challenges[i].append(Screen().capture(regions[i][0]))
	sleep(ACCURACY)

import pprint
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(challenges)
pp.pprint(responses)