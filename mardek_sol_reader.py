from os import listdir, sep
from struct import unpack

save_file_dir = '/Users/joe/Library/Application Support/Google/Chrome/Default/Pepper Data/Shockwave Flash/WritableRoot/#SharedObjects/487NAFC7/localhost/'

def to_hex(byte):
	byte = ord(byte)
	digits = '0123456789ABCDEF'
	p1 = byte/16
	p2 = byte%16
	return digits[p1] + digits[p2]

signal = ['70', '6C', '61', '79', '74', '69', '6D', '65'] # playtime
signal += ['08', '00', '00', '00', '03'] # Array of length 3, according to AMF0 format

for i in range(70):
	try:
		f = open(save_file_dir+'MARDEKv3__sg_{:d}.sol'.format(i))
		data = []
		
		byte = f.read(1)
		while byte != '':
			data.append(to_hex(byte))
			byte = f.read(1)
		for j in range(len(data)-len(signal)):
			if data[j:j+len(signal)] == signal:
				hex = ''.join(data[j+len(signal):j+len(signal)+36]).decode('hex')
				h, m, s = unpack('>4xd4xd4xd', hex)
				print 'Time for save file {:d}:\t{:02.0f}:{:02.0f}:{:02.0f}'.format(i+1,h,m,s)
		f.close()
	except IOError:
		continue
