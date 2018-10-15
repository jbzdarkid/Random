from PIL.ImageGrab import grab
from time import sleep
from win32api import mouse_event, keybd_event
from winsound import Beep

def rotate90(inverted=False):
  # +1 for clockwise, -1 for counter-clockwise
  mouse_event(4, (1-2*inverted)*12620, 0, 0, 0)
  sleep(0.1)

def shift(release=False):
  # 1 for down, 2 for up
  keybd_event(160, 0, 1+(1*release), 0)
  sleep(0.1)

def move(left=False):
  # 68 for d, 65 for a
  keybd_event(68-(3*left), 0, 1, 0)
  sleep(5)
  keybd_event(68-(3*left), 0, 2, 0)
  sleep(0.1)

def capture(name):
  image = grab()
  image.save("photos/"+name+".png")
  Beep(200, 100)
  sleep(0.1)


print 'starting in 10'
for i in xrange(10):
  Beep(1000-50*i, 100)
  sleep(1)
dims = (15, 20)

shift()
inverted = False
for i in xrange(dims[0]):
  capture("%d_%d" % (i, 0))
  for j in xrange(dims[1]-1):
    move(inverted)
    if not inverted:
      capture("%d_%d" % (i, j+1))
    else:
      capture("%d_%d" % (i, dims[1]-j-2))
  rotate90(inverted)
  move(inverted)
  inverted = not inverted
  rotate90(inverted)
shift(True)
