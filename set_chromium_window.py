import json
import sys
from pathlib import Path

p = Path.home() / 'AppData/Local/Chromium/User Data/Default/Preferences'
with p.open('r') as f:
  prefs = json.load(f)

corner = (50, 50) # X, Y
size = (1252, 993) # Width, Height

window_placement = prefs['browser']['window_placement']
if sys.argv[1] == 'read':
  print('Corner: ', window_placement['left'], window_placement['top'])
  print('Size: ', window_placement['right'] - window_placement['left'], window_placement['bottom'] - window_placement['top'])
elif sys.argv[1] == 'write':
  window_placement['left']   = corner[0]
  window_placement['right']  = corner[0] + size[0]
  window_placement['top']    = corner[1]
  window_placement['bottom'] = corner[1] + size[1]
  prefs['browser']['window_placement'] = window_placement

  with p.open('w') as f:
    json.dump(prefs, f)
