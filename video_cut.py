import os
import subprocess
import shutil
import re
from tkinter import *
from PIL import Image, ImageTk

FFMPEG = r'C:\Users\localhost\Downloads\ffmpeg-4.0-win64-static\bin\ffmpeg.exe'
TMP = os.path.dirname(os.path.abspath(__file__)) + '/tmp'
  
def draw(delta):
  global current_frame
  target_frame = current_frame + delta
  try:
    pil_img = Image.open(TMP+r'\%05d.jpg' % target_frame).resize((width, height))
    global active_image # Keep a reference to the image so it isn't GCd
    active_image = ImageTk.PhotoImage(pil_img)
  except: # Frame doesn't exist, most likely
    return

  global image_label
  image_label.configure(image=active_image)
  image_label.pack()
  current_frame = target_frame

def something():
  global split_frames
  global current_frame
  split_frames.append(current_frame)
  
if __name__ == '__main__':
  # if os.path.isdir(TMP):
    # shutil.rmtree(TMP)
  # os.mkdir(TMP)
  file = r'D:\Videos\2018-06-23 18-12-44.mov'

  # Parse video data to get width/height/framerate
  try:
    file_data = subprocess.check_output([FFMPEG, '-i', file], cwd=TMP, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as e:
    file_data = str(e.output)
  m = re.search('(\d+)x(\d+) .*?, \d+ kb/s, (\d+) fps,', file_data)
  width = int(m.group(1))//2
  height = int(m.group(2))//2
  framerate = int(m.group(3))
  """
  # Set up the TK window
  root = Tk()
  root.geometry('%dx%d' % (width, height + 50))
  global image_label
  image_label = Label()
  image_label.pack()
  buttons = Frame(root)
  buttons.pack(side=BOTTOM, fill=BOTH, expand=True)
  Button(buttons, text='<<', command=lambda: draw(-framerate*60), font='Courier').pack(side='left')
  Button(buttons, text='<', command=lambda: draw(-framerate), font='Courier').pack(side='left')
  Button(buttons, text='|<', command=lambda: draw(-1), font='Courier').pack(side='left')
  Button(buttons, text='X', command=something, font='Courier').pack(side='left')
  Button(buttons, text='>|', command=lambda: draw(1), font='Courier').pack(side='left')
  Button(buttons, text='>', command=lambda: draw(framerate), font='Courier').pack(side='left')
  Button(buttons, text='>>', command=lambda: draw(framerate*60), font='Courier').pack(side='left')

  global current_frame
  current_frame = 1
  global split_frames
  split_frames = set([1]) # Using a set to prevent duplicates
  draw(0)
  """
  # Convert the video to images TODO: Background thread?
  subprocess.check_call([FFMPEG, '-i', file, '%05d.jpg'], cwd=TMP)
  # Run TK, wait for user to select frames
  #root.mainloop()
  split_frames = []
  # Convert the frame groups into new videos
  split_frames = list(split_frames)
  split_frames.sort()
  for i in range(len(split_frames)):
    args = [FFMPEG, '-start_number', str(split_frames[i])]
    if i < len(split_frames) - 1:
      args += ['-vframes', str(split_frames[i+1] - split_frames[i])]
    args += ['-framerate', str(framerate), '-i', '%05d.jpg', 'out%d.mp4' % i]
    print(args)
    subprocess.check_call(args, cwd=TMP)
    
  
  
  
  
