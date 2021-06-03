import re
import requests
import sys
import webbrowser

if len(sys.argv) > 1:
  year = int(sys.argv[1])
else:
  year = int(input('Enter year:'))
url = f'https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_number_ones_of_{year}'
r = requests.get(url)

start = r.text.index('#EDEAE0')
end = r.text.index('</table>', start)

songs = []
for cell in re.finditer('<td align="center".*?>(.*?)</td>', r.text[start:end], flags=re.DOTALL):
  link = re.search('<a.*?>(.*?)</a>', cell.group(0))
  if link:
    songs.append(link.group(1))

for i in range(0, len(songs), 2):
  print(f'Next hit: {songs[i]} by {songs[i+1]}')
  confirm = input('>')
  if confirm.lower() in ['no', 'skip', 'n', 's']:
    continue
  url = f'https://www.youtube.com/results?search_query=%22{songs[i]}%22+%22{songs[i+1]}%22'
  webbrowser.open_new_tab(url)
