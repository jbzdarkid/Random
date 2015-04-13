import urllib2, re
output = '\n\n'
url = '76273009-wereling-wounded-on-hold-prologue'
page = 1
title = None
while(True):
	text = urllib2.urlopen('http://www.wattpad.com/'+url+'/page/'+str(page)).read()
	new_title = re.search('<title>(.*?)</title>', text).group(1)
	if new_title == title: # Reached page limit
		page = 1
		next_url = re.search('<a class="on-navigate next-up.*?href="(.*?)"', text)
		if next_url is None:
			break
		url = next_url.group(1)
		output += '\n\n\t'+title+'\n'
		continue
	else: # New page
		print new_title, len(text)
		page += 1
		title = new_title
	
	for i in range(len(text)):
		if text[i:i+7] == '<p data':
			i += 48
			while (text[i:i+4] != '</p>'):
				output += text[i]
				i += 1
			output += '\n'
f = open('out.txt', 'wb')
f.write(output)
f.close()