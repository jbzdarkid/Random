import sys
from collections import defaultdict
from pathlib import Path
from subprocess import run
from multiprocessing import Pool
from json import load
from pprint import PrettyPrinter as pp


def extract(args):
  input, output = args
  run(['UAssetGUI.exe', 'tojson', input, output, '4.27'], check=True)


def dump():
  # This assumes you've already extracted C:\Program Files (x86)\Steam\steamapps\common\People of Note\PeopleOfNote\Content\Paks\PeopleOfNote-WindowsNoEditor.pak
  # into a local folder named 'tmp'
  # Note: I had to download the latest nightly build from CI in order to make this work... sigh.

  root = Path('tmp/PeopleOfNote/Content/PeopleOfNote')

  with Pool() as pool:
    tasks = []

    for input in root.glob('Environments/**/*.uasset'):
      output = (Path('extract') / input.relative_to(root)).with_name(input.stem + '.json')
      output.parent.mkdir(exist_ok=True, parents=True)
      tasks.append((str(input), str(output)))

    pool.map(extract, tasks)

  print('All done')

def flatten(data, path=None):
  if not path:
    path = []

  try:
    if isinstance(data, list):
      new_data = []
      for i, d in enumerate(data):
        new_data.append(flatten(d, path + [i]))

      # A lot of the lists here seem to be lists of dictionaries with unique keys.
      # If it looks like we're dealing with that, flatten to a single dict.
      new_new_data = {}
      for entry in new_data:
        if not isinstance(entry, dict):
          return new_data # Bail out due to non-dict entry.

        keys_before = len(new_new_data)
        new_new_data |= entry
        keys_after = len(new_new_data)

        if keys_before + len(entry) != keys_after:
          return new_data # Bail out due to duplicate key

      return new_new_data

    elif isinstance(data, dict):
      key = data.get('Name')
      if not key:
        return data # Some weird weak reference without a name, just surface it raw

      if 'CultureInvariantString' in data:
        value = data['CultureInvariantString']
      else:
        value = flatten(data['Value'], path + [key])

      return {key: value}

    else:
      return data

  except SystemExit:
    raise
  except:
    print('Path:', path)
    print(data)
    sys.exit()


def search(data, text, results):
  found = False
  if isinstance(data, list):
    for i, entry in enumerate(data):
      if search(entry, text, results):
        results[-1] = [i] + results[-1]
        found = True

  elif isinstance(data, dict):
    for k, v in data.items():
      if search(v, text, results):
        results[-1] = [k] + results[-1]
        found = True

  else:
    if text in str(data):
      results.append([str(data)])
      found = True

  return found


def extract_dialog():
  with Path('extract/Data/DialogueData.json').open('r', encoding='utf-8') as f:
    raw_data = load(f)

    # search(raw_data, "have to find places for it", results)
    # ['Exports', 0, 'Table', 'Data', 147, 'Value', 0, 'Value', 0, 'Value', 0, 'Value', 0, 'Value', 2, 'CultureInvariantString']
    # I just...I hate having <Chaos>STUFF</>. You know? You have to find places for it, move it around...

    results = []
    search(raw_data, "<Emphasis>", results)
    for result in results:
      # text = results[-1]
      text = result.pop(-1)
      print(result)
      print(text)
      print()
    raise

    dialog = {}
    for entry in raw_data['Exports'][0]['Table']['Data']:
      dialog |= flatten(entry)

  return dialog


def extract_chests():
  with Path('extract/Data/MapData.json').open('r', encoding='utf-8') as f:
    raw_data = load(f)

    maps = {}
    for entry in raw_data['Exports'][0]['Table']['Data']:
      maps |= flatten(entry)

  with Path('extract/Data/GameFlagData.json').open('r', encoding='utf-8') as f:
    raw_data = load(f)

    flags = {}
    for entry in raw_data['Exports'][0]['Table']['Data']:
      flags |= flatten(entry)
      
  probable_chests = [key for key in flags if 'chest' in key.lower()]
  probable_chests.sort()
  for key in probable_chests:
    map_name = '_'.join(key.split('_')[:2])
    if map_name in maps:
      print(key.ljust(80), maps[map_name]['MapName'])
    else:
      print(key.ljust(80), 'invalid map')

def extract_enemies():
  with Path('extract/Data/EnemyData.json').open('r', encoding='utf-8') as f:
    raw_data = load(f)

    enemies = {}
    for entry in raw_data['Exports'][0]['Table']['Data']:
      enemies |= flatten(entry)
      
  for enemy_name, enemy in enemies.items():
    print(enemy_name.ljust(25), enemy['EnemyName'].ljust(25), end='')
    hp = round(enemy['Stats']['HP'])
    if enemy['bIsBoss']:
      print('HP:', hp)
    else:
      print('HP:', hp, 'to', round(hp * 4/3))

def extract_shops():
  with Path('extract/Data/ShopData.json').open('r', encoding='utf-8') as f:
    raw_data = load(f)
    shops = {}
    for entry in raw_data['Exports'][0]['Table']['Data']:
      shops |= flatten(entry)

  with Path('extract/Data/ItemData.json').open('r', encoding='utf-8') as f:
    raw_data = load(f)
    items = {}
    for entry in raw_data['Exports'][0]['Table']['Data']:
      items |= flatten(entry)

  for shop_id in sorted(shops.keys()):
    shop = shops[shop_id]
    is_vinyl_shop = '[Vinyl shop]' if shop['bVinylShop'] else ''
    print(shop['ShopName'], f'({shop_id})', is_vinyl_shop)
    for item in shop['ShopItems']:
      required_flag = item['ShopItems']['RequiredGameFlag'] or ' '
      if required_flag == 'Scene86':
        required_flag = '  [Post-Pyre]'
      elif required_flag == 'Scene118':
        required_flag = '  [Post-Octave Range]'
      elif required_flag == 'SteamDemo2':
        required_flag = '  [Only in steam demo]'

      item_id = item['ShopItems']['ItemID']
      if item_id not in items:
        print('  Unknown item:', item_id)
        continue
      item = items[item_id]
      if is_vinyl_shop:
        price = str(item['VinylPrice']) + ' Vinyls'
      else:
        price = str(item['ItemPrice']) + ' Groove'
      unique = '[Unique]' if item['UniqueRebuy'] else ''
      print(required_flag, item['ItemName'], f'({price})', unique)
    print()

def extract_items():
  with Path('extract/Data/ItemData.json').open('r', encoding='utf-8') as f:
    raw_data = load(f)
    items = {}
    for entry in raw_data['Exports'][0]['Table']['Data']:
      items |= flatten(entry)

  with Path('extract/Data/EquipmentData.json').open('r', encoding='utf-8') as f:
    raw_data = load(f)
    equipment = {}
    for entry in raw_data['Exports'][0]['Table']['Data']:
      equipment |= flatten(entry)

  items_per_type = defaultdict(list)
  for item_id in equipment:
    if equipment[item_id]['EquipmentType'] == 'EHeroEquipmentType::Instrument':
      items_per_type['weapon'].append(item_id)
    elif equipment[item_id]['EquipmentType'] == 'EHeroEquipmentType::Body':
      items_per_type['armor'].append(item_id)
    elif equipment[item_id]['EquipmentType'] == 'EHeroEquipmentType::Accessory':
      items_per_type['ring'].append(item_id)
    elif equipment[item_id]['EquipmentName'].endswith(' Vinyls'):
      pass
    elif item_id in items and items[item_id]['ItemType'] == 'EShopItemType::KeyItem':
      items_per_type['key'].append(item_id)

  print('== Weapons ==')
  def sort_key(item_id):
    price = items.get(item_id, {}).get('ItemPrice', 0)
    return equipment[item_id]['MusicType'], price
  prev_type = None
  for item_id in sorted(items_per_type['weapon'], key=sort_key):
    weapon = equipment[item_id]
    type, price = sort_key(item_id)
    if type != prev_type:
      print(f'=== {type} ===')
      prev_type = type
    print('-', weapon['EquipmentName'].ljust(30), 'ATK:', weapon['StatBonus_Offense'], 'Groove:', price)

  print('== Armor ==')
  def sort_key(item_id):
    return equipment[item_id]['StatBonus_Defense']
  for item_id in sorted(items_per_type['armor'], key=sort_key):
    armor = equipment[item_id]
    print('-', armor['EquipmentName'].ljust(30),
      'HP:', str(armor['StatBonus_HP']).ljust(2),
      'ATK:', armor['StatBonus_Offense'],
      'DEF:', armor['StatBonus_Defense'],
      'Groove:', items[item_id]['ItemPrice'])
  
  print('== Rings ==')
  def sort_key(item_id):
    return items.get(item_id, {}).get('ItemPrice', 0)
  for item_id in sorted(items_per_type['ring'], key=sort_key):
    ring = equipment[item_id]
    price = sort_key(item_id)
    if ring['SongstoneEffect'] != 'ECSongstoneType::None':
      notes = ring['SongstoneEffect'] + ' ' + str(ring['SongstoneEffectValue'])
    else:
      notes = []
      if ring['StatBonus_HP'] > 0:
        notes += ['HP:', ring['StatBonus_HP']]
      if ring['StatBonus_BP'] > 0:
        notes += ['BP:', ring['StatBonus_BP']]
      if ring['StatBonus_Offense'] > 0:
        notes += ['ATK:', ring['StatBonus_Offense']]
      if ring['StatBonus_Defense'] > 0:
        notes += ['DEF:', ring['StatBonus_Defense']]
      notes = ' '.join(map(str, notes))
    print('-', ring['EquipmentName'].ljust(30), str(price).ljust(7), notes)
  

def puzzle():
  with Path('extract/Data/PuzzleBattleData.json').open('r', encoding='utf-8') as f:
    raw_puzzle_data = load(f)
    battles = {}
    for entry in raw_puzzle_data['Exports'][0]['Table']['Data']:
      battles |= flatten(entry)

  dialog = extract_dialog()

  for battle_name, battle in battles.items():
    if battle['PartyAP'] > 0 or battle['PartyXP'] > 0:
      groove = battle['PartyGroove']
      ap = battle['PartyAP']
      xp = battle['PartyXP']
      rewards = f'{groove:5} groove, {ap:3} AP, {xp:4} XP'

      speaker_name = '(unknown)'
      dialog_lines = dialog[battle_name]['DialogueEvents'][0]['DialogueEvents']['Dialogue']
      if not isinstance(dialog_lines, list):
        dialog_lines = [dialog_lines] # Single lines are not kept as a list
      for e in dialog_lines:
        if e['Dialogue']['SpeakerID'] == battle_name:
          speaker_name = e['Dialogue']['DialogueSpeaker']
          break

      print('Battle', battle_name.ljust(25), speaker_name.ljust(25), 'provides', rewards, battle['VictoryCondition'].ljust(40), battle['VictoryParameter'])


if __name__ == '__main__':
  if len(sys.argv) > 1 and sys.argv[1] == 'puzzle':
    puzzle()
  elif len(sys.argv) > 1 and sys.argv[1] == 'dialog':
    extract_dialog()
  elif len(sys.argv) > 1 and sys.argv[1] == 'chest':
    extract_chests()
  elif len(sys.argv) > 1 and sys.argv[1] == 'enemy':
    extract_enemies()
  elif len(sys.argv) > 1 and sys.argv[1] == 'shop':
    extract_shops()
  elif len(sys.argv) > 1 and sys.argv[1] == 'item':
    extract_items()
  else:
    dump()
