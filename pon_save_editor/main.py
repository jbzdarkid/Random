from json import load, dump
from pathlib import Path
from re import search
from subprocess import run

input_file = Path('C:/Users/joblac/AppData/Local/PeopleOfNote/Saved/SaveGames/ManifestSave.sav')
output_file = Path('out.json')
run(['uesave.exe', 'to-json', '--input', input_file, '--output', output_file, '--no-warn'])

with output_file.open('r', encoding='utf-8') as f:
  manifest_save = load(f)

# This property doesn't re-serialize properly.
manifest_save['root']['properties']['SaveProfile_0'].pop('LastKeyModification_0', None)

saves = manifest_save['root']['properties']['SaveSlotsManifest_0']
while 1:
  print('Select a save file:')
  for i, save in enumerate(saves):
    print(i, save['key'])
  index = int(input('>'))

  choice = input('(R)ename, (C)opy, (M)ove, (D)elete, (Q)uit: ')
  if choice.lower() == 'r':
    name = input('New name: ')
    saves[index]['key'] = name
  elif choice.lower() == 'c':
    new_name = saves[index]['key']
    while any((save['key'] == new_name for save in saves)):
      new_name += ' (Copy)'
    saves.append({'key': new_name, 'value': saves[index]['value']})
  elif choice.lower() == 'm':
    new_index = int(input('Move before entry #: '))
    entry = saves.pop(index)
    saves.insert(new_index, entry)
  elif choice.lower() == 'd':
    confirm = input('Are you sure (Y/N)? ')
    if confirm.lower() == 'y':
      saves.pop(index)
  elif choice.lower() == 'q':
    break

with output_file.open('w', encoding='utf-8') as f:
  dump(manifest_save, f, indent=2)

output = run(['uesave.exe', 'from-json', '--input', output_file, '--output', input_file], capture_output=True, text=True)
if output.returncode != 0:
  m = search(r'line (\d+) column (\d+)\n', output.stderr)
  line = int(m.group(1))
  with output_file.open('r', encoding='utf-8') as f:
    print(output.stderr)
    print('\n'.join(f.read().splitlines()[line-2:line+2]))
