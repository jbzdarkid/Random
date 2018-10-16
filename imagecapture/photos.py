from time import sleep
from winsound import Beep
from math import pi
from subprocess import check_output
import win32gui, win32ui, win32con, win32api

def mem(*params):
  params = ['x64/Debug/mem.exe'] + [str(param) for param in params]
  out = check_output(params).decode('utf-8').strip()
  if out == '':
    return
  return [float(o) for o in out.split(' ')]

srcdc = win32ui.CreateDCFromHandle(win32gui.GetWindowDC(win32gui.GetDesktopWindow()))
def capture(name):
  bmp = win32ui.CreateBitmap()
  bmp.CreateCompatibleBitmap(srcdc, 3840, 2150)

  memdc = srcdc.CreateCompatibleDC()
  memdc.SelectObject(bmp)
  memdc.BitBlt((0, 0), (3840, 2150), srcdc, (-3840, -1070), win32con.SRCCOPY)
  bmp.SaveBitmapFile(memdc, f'photos/{name}.bmp')
  Beep(200, 100)
  sleep(0.1)

print('starting in 10')
for i in range(10):
  Beep(1000-50*i, 100)
  sleep(1)

mem('noclip', 1)
mem('angle', 0, -pi/2)
for x in range(4):
  for y in range(4):
    mem('pos', -384 + x*256, -384 + y*256, 256)
    capture(f'{x}_{y}')

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