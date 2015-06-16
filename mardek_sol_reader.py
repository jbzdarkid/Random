from os import listdir, sep
from struct import unpack

save_file_dir = '/Users/joe/Library/Application Support/Google/Chrome/Default/Pepper Data/Shockwave Flash/WritableRoot/#SharedObjects/487NAFC7/localhost/'

def to_hex(byte):
	byte = ord(byte)
	digits = '0123456789ABCDEF'
	p1 = byte/16
	p2 = byte%16
	return digits[p1] + digits[p2]

signal = 'playtime\x08\x00\x00\x00\x03'

for i in range(70):
	try:
		f = open(save_file_dir+'MARDEKv3__sg_{:d}.sol'.format(i))
		file = f.read()
		f.close()

		for j in range(len(file)-len(signal)):
			if file[j:j+len(signal)] == signal:
				time = ''.join(file[j+len(signal):j+len(signal)+36])
				h, m, s = unpack('>4xd4xd4xd', time)
				print 'Time for save file {:d}:\t{:02.0f}:{:02.0f}:{:02.0f}'.format(i+1,h,m,s)
	except IOError:
		continue
