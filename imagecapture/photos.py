from time import sleep
from winsound import Beep
from math import pi
from subprocess import check_output
import win32gui, win32ui, win32con
# TODO: Automatic photomerge? -- working on it
# Maybe crop capture further to avoid some lens distortion? 50% square might work.

def mem(*params):
  params = ['x64/Debug/mem.exe'] + [str(param) for param in params]
  out = check_output(params).decode('utf-8').strip()
  if out == '':
    return
  return [float(o) for o in out.split(' ')]

srcdc = win32ui.CreateDCFromHandle(win32gui.GetWindowDC(win32gui.GetDesktopWindow()))
def capture(name):
  Beep(200, 100)
  sleep(0.5)

  # https://stackoverflow.com/a/4589290
  mid = (-1920, 10)
  width = 1500
  height = 1500
  left = mid[0] - width//2
  top = mid[1] - height//2

  bmp = win32ui.CreateBitmap()
  bmp.CreateCompatibleBitmap(srcdc, width, height)

  memdc = srcdc.CreateCompatibleDC()
  memdc.SelectObject(bmp)
  memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
  bmp.SaveBitmapFile(memdc, f'photos/{name}.bmp')

print('starting in 10')
for i in range(10):
  Beep(1000-50*i, 100)
  sleep(1)

mem('noclip', 1)
mem('angle', 0, -pi/2)
mem('pos', 0, 0, 0)
sleep(2.0)

# TODO: Try Z=25 mapping for town
# 1500x1500 is too small, and 25 might be too low. Too much detail is actually a bad thing here.
z = 25
spacing = 5
for x in range(0, -40, -2*spacing):
  for y in range(0, -30, -spacing):
    mem('pos', x, y, z)
    capture(f'{x}_{y}_{z}')
  x -= spacing
  for y in range(-25, 5, spacing):
    mem('pos', x, y, z)
    capture(f'{x}_{y}_{z}')
"""

from PIL import Image
width = 1000
height = 1000
crop_box = (
  1920 - width//2, # left
  1080 - height//2, # top
  1920 + width//2, # right
  1080 + height//2, # bottom
)

z = 25
for x in range(-2, -10, -4):
  for y in range(-2, -10, -4):
    im = Image.open(f'photos/{x}_{y}_{z}.bmp')
    im2 = im.crop(crop_box)
    im2.save(f'photos2/{x}_{y}_{z}.bmp')
"""
