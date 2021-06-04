from pathlib import Path
import math
import cv2

CV_CAP_PROP_POS_MSEC      = 0
CV_CAP_PROP_POS_FRAMES    = 1
CV_CAP_PROP_POS_AVI_RATIO = 2
CV_CAP_PROP_FRAME_WIDTH   = 3
CV_CAP_PROP_FRAME_HEIGHT  = 4
CV_CAP_PROP_FPS           = 5
CV_CAP_PROP_FOURCC        = 6
CV_CAP_PROP_FRAME_COUNT   = 7

first_video_path = Path.home() / 'Desktop' / 'Stephens Sausage Roll - Lachrymose Head 15.667s.mp4'
second_video_path = Path.home() / 'Desktop' / '2020-09-19 17-43-43.mov'

final_video_path = Path.home() / 'Desktop' / 'out.avi'

# Final output size
width = 1280
height = 720

interp = cv2.INTER_AREA







cap = cv2.VideoCapture(str(first_video_path))
video_l = {
  'width': int(cap.get(CV_CAP_PROP_FRAME_WIDTH)),
  'height': int(cap.get(CV_CAP_PROP_FRAME_HEIGHT)),
  'fps': int(cap.get(CV_CAP_PROP_FPS)),
  'frames': int(cap.get(CV_CAP_PROP_FRAME_COUNT)),
  'data': cap,
}
cap = cv2.VideoCapture(str(second_video_path))
video_r = {
  'width': int(cap.get(CV_CAP_PROP_FRAME_WIDTH)),
  'height': int(cap.get(CV_CAP_PROP_FRAME_HEIGHT)),
  'fps': int(cap.get(CV_CAP_PROP_FPS)),
  'frames': int(cap.get(CV_CAP_PROP_FRAME_COUNT)),
  'data': cap,
}

gcd = math.gcd(video_l['fps'], video_r['fps'])
video_l['timescale'] = video_r['fps']//gcd
video_r['timescale'] = video_l['fps']//gcd

i1 = 125
i2 = 889

while 0:
  video_l['data'].set(CV_CAP_PROP_POS_FRAMES, i1)
  ret, frame_l = video_l['data'].read()

  base = frame_l.copy()
  # Fill with black
  base[:] = (0, 0, 0)
  base = cv2.resize(base, (width, height))

  base[0:height//2, 0:width//2] = cv2.resize(frame_l, (width//2, height//2), interpolation=interp)

  video_r['data'].set(CV_CAP_PROP_POS_FRAMES, i2)
  ret, frame_r = video_r['data'].read()
  base[0:height//2, width//2:width] = cv2.resize(frame_r, (width//2, height//2), interpolation=interp)

  cv2.imshow('', base)
  key = cv2.waitKey(0)
  if key == ord('q'):
    i1 += 1
  elif key == ord('Q'):
    i1 += 30
  elif key == ord('a'):
    i1 -= 1
  elif key == ord('A'):
    i1 -= 30
  elif key == ord('e'):
    i2 += 1
  elif key == ord('E'):
    i2 += 30
  elif key == ord('d'):
    i2 -= 1
  elif key == ord('D'):
    i2 -= 30
  elif key == ord(' '):
    break
cv2.destroyAllWindows()

start = min(i1 * video_l['timescale'], i2 * video_r['timescale'])
start_l = (i1 * video_l['timescale'] - start) // video_l['timescale']
start_r = (i2 * video_r['timescale'] - start) // video_r['timescale']

print(start_l, start_r)

dur_l = (video_l['frames'] - start_l) * video_l['timescale']
dur_r = (video_r['frames'] - start_r) * video_r['timescale']
dur = min(dur_l, dur_r)

end_l = start_l + (dur // video_l['timescale'])
end_r = start_r + (dur // video_r['timescale'])

out = cv2.VideoWriter(str(final_video_path), cv2.VideoWriter_fourcc(*'DIVX'), video_l['fps'] * video_l['timescale'], (width, height))
out.set(CV_CAP_PROP_FRAME_WIDTH, width)
out.set(CV_CAP_PROP_FRAME_HEIGHT, height)
out.set(CV_CAP_PROP_FPS, video_l['fps'] * video_l['timescale'])
out.set(CV_CAP_PROP_FRAME_COUNT, dur)

for i in range(dur):
  if i%60 == 0:
    print(i, dur)
  video_l['data'].set(CV_CAP_PROP_POS_FRAMES, start_l + (i // video_l['timescale']))
  ret, frame_l = video_l['data'].read()

  base = frame_l.copy()
  # Fill with black
  base[:] = (0, 0, 0)
  base = cv2.resize(base, (width, height))

  base[0:height//2, 0:width//2] = cv2.resize(frame_l, (width//2, height//2), interpolation=interp)

  video_r['data'].set(CV_CAP_PROP_POS_FRAMES, start_r + (i // video_r['timescale']))
  ret, frame_r = video_r['data'].read()

  base[0:height//2, width//2:width] = cv2.resize(frame_r, (width//2, height//2), interpolation=interp)

  out.write(base)

video_l['data'].release()
video_r['data'].release()
out.release()
cv2.destroyAllWindows()
