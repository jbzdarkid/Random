from struct import unpack
from os import walk, sep
from os.path import expanduser
from re import search

shared_objects_dirs = [
	'Library/Application Support/Google/Chrome/Default/Pepper Data/Shockwave Flash/WritableRoot/#SharedObjects',
	'Library/Preferences/Macromedia/Flash Player/#SharedObjects',
	'AppData\Local\Google\Chrome',
	'AppData\Macromedia\Flash Player\#SharedObjects',
]

savefiles = []
for shared_objects_dir in shared_objects_dirs:
	for root, dirs, files in walk(expanduser('~')+sep+shared_objects_dir):
		for filename in files:
			if filename[:13] == 'MARDEKv3__sg_':
				savefiles.append([root.split(sep)[-1], int(filename[13:-4]), root+sep+filename])

for file in sorted(savefiles):
		f = open(file[2]).read()
		# 8 represents array, 0003 means 3 elements
		m = search('playtime\x08\x00\x00\x00\x03(.{36})', f)
		print 'Save file %d from %s:' % (file[1], file[0]),
		print '\t%d:%02.0f:%02.0f' % unpack('>4xd4xd4xd', m.group(1))
