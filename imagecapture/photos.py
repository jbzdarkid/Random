from time import sleep
from winsound import Beep
from math import pi
from subprocess import check_output
from os import system
import win32gui, win32ui, win32con, win32api
# TODO: Automatic photomerge? -- working on it
# TODO: Try Z=25 mapping for town
# Crop capture() to square
# Maybe crop capture further to avoid some lens distortion? 50% square might work.

def mem(*params):
  params = ['x64/Debug/mem.exe'] + [str(param) for param in params]
  out = check_output(params).decode('utf-8').strip()
  if out == '':
    return
  return [float(o) for o in out.split(' ')]

srcdc = win32ui.CreateDCFromHandle(win32gui.GetWindowDC(win32gui.GetDesktopWindow()))
def capture(name):
  sleep(2.0)
  Beep(200, 100)
  bmp = win32ui.CreateBitmap()
  bmp.CreateCompatibleBitmap(srcdc, 3840, 2150)

  memdc = srcdc.CreateCompatibleDC()
  memdc.SelectObject(bmp)
  memdc.BitBlt((0, 0), (3840, 2150), srcdc, (-3840, -1070), win32con.SRCCOPY)
  bmp.SaveBitmapFile(memdc, f'photos/{name}.bmp')

def recurse_photos(x, y, z, name, depth):
  if depth == 0:
    return
  recurse_photos(x - z/8, y - z/8, z/2, name + '0', depth - 1)
  recurse_photos(x - z/8, y + z/8, z/2, name + '1', depth - 1)
  recurse_photos(x + z/8, y - z/8, z/2, name + '2', depth - 1)
  recurse_photos(x + z/8, y + z/8, z/2, name + '3', depth - 1)

  print(x, y, z, depth)
  mem('pos', x, y, z)
  #capture(f'{depth}_{name}')

z = 2/3z

  # system('.\photomerge.vbs')
"""
0 0 75 2
-12.5 -12.5 50.0 1
-12.5 12.5 50.0 1
12.5 -12.5 50.0 1
12.5 12.5 50.0 1
"""
print('starting in 10')
for i in range(0):
  Beep(1000-50*i, 100)
  sleep(1)

mem('noclip', 1)
mem('angle', 0, -pi/2)

recurse_photos(0, 0, 100, '', 2)

"""
# Scale: 1:4
mem('pos', -384, -384, 256);
mem('pos', -384, -128, 256);
mem('pos', -384, 128, 256);
mem('pos', -384, 384, 256);

mem('pos', -128, -384, 256);
mem('pos', -128, -128, 256);
mem('pos', -128, 128, 256);
mem('pos', -128, 384, 256);

mem('pos', 128, -384, 256);
mem('pos', 128, -128, 256);
mem('pos', 128, 128, 256);
mem('pos', 128, 384, 256);

mem('pos', 384, -384, 256);
mem('pos', 384, -128, 256);
mem('pos', 384, 128, 256);
mem('pos', 384, 384, 256);
"""