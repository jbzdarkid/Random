# If you really want to do this, be a bit more aware of context:
# - Track commented text separately (incl comment identifiers)
# - Track words (maybe at 5ch or less)
# - Lowercase (at least in the ascii range)
# - Remove space, tab, CR, LF.


from pathlib import Path

root = Path('.')

asciitable = [0]*128
nonascii = 0

for path in root.glob('**/*.cs'):
  with path.open('rb') as f:
    contents = f.read()
  for c in contents:
    if c < 128:
      asciitable[c] += 1
    else:
      nonascii += 1

print(nonascii)
exit()

print(asciitable)
sortable = [(asciitable[i], i) for i in range(128)]
sortable.sort(reverse=True)
print(sortable)
for count, c in sortable:
  print(chr(c), count)
