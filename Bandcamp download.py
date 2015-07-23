from json import loads
from random import randint
from re import search
from threading import Lock, Thread
from time import sleep
from urllib import urlretrieve
from urllib2 import urlopen

# Credit to Vinko Vrsalovic on http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
import string
valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

lock = Lock()
data = urlopen("https://harrycallaghan.bandcamp.com/album/tier-3-soundtrack").read()
m = search('trackinfo :(.*),', data)
dict = loads(m.group(1))
numTracks = len(dict)
global gui
gui = ' '*numTracks
threads = [None] * numTracks

# Knuth randomization algorithm
order = range(numTracks)
for i in range(numTracks):
	j = randint(i, numTracks-1)
	temp = order[i]
	order[i] = order[j]
	order[j] = temp

def replace(string, char, location):
	if location == 0:
		return char + string[1:]
	return string[:location]+char+string[location+1:]

def download(url, title, i):
	global gui
	title = ''.join(c for c in title if c in valid_chars)
	urlretrieve(url, title)
	lock.acquire()
	print replace(gui, '^', i)
	gui = replace(gui, ' ', i)
	lock.release()

for i in order:
	track = dict[i]
	print replace(gui, 'v', i)
	gui = replace(gui, '|', i)
	title = '{0:02d}-{name}.mp3'.format(i+1, name=track['title'])
	thread = Thread(target=download, kwargs={
		'url': track['file']['mp3-128'],
		'title': title,
		'i': i})
	threads[i] = thread
	thread.start()
	sleep(0.1)

for thread in threads:
	thread.join()
