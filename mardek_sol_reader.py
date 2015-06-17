from struct import unpack
from os import walk, sep
from os.path import expanduser

shared_objects_dirs = [
	'Library/Application Support/Google/Chrome/Default/Pepper Data/Shockwave Flash/WritableRoot/#SharedObjects',
	'Library/Preferences/Macromedia/Flash Player/#SharedObjects'
]

savefiles = []
for shared_objects_dir in shared_objects_dirs:
	for root, dirs, files in walk(expanduser('~')+sep+shared_objects_dir):
		for filename in files:
			if filename[:13] == 'MARDEKv3__sg_':
				savefiles.append([root.split(sep)[-1], int(filename[13:-4]), root+sep+filename])

signal = 'playtime\x08\x00\x00\x00\x03' # 8 represents array, 0003 means 3 elements
for file in sorted(savefiles):
	try:
		f = open(file[2]).read()
		match = 0
		for char in f:
			if char != signal[match]:
				match = 0
			else:
				match += 1
				if match == len(signal)
					time = ''.join(f[j+len(signal):j+len(signal)+36])
					h, m, s = unpack('>4xd4xd4xd', time)
					print 'Save file {:d} from {:s}:\t{:02.0f}:{:02.0f}:{:02.0f}'.format(file[1],file[0],h,m,s)
	except IOError:
		continue
