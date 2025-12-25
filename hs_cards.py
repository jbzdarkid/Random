from pathlib import Path
import json

try:
  cards_file = Path('cards.json')
  cardlist = json.load(cards_file.open('r', encoding='utf-8'))
  for k, v in list(cardlist.items()):
    del cardlist[k]
    cardlist[int(k)] = v # Json doesn't support integer keys but python does
except Exception as e:
  print(e)
  import requests
  r = requests.get('https://api.hearthstonejson.com/v1/latest/all/cards.collectible.json')
  j = r.json()
  with Path('cards.collectible.json').open('w', encoding='utf-8') as f:
    json.dump(j, f)
  
  cardlist = {}
  for card in j:
    cardlist[card['dbfId']] = card['name']['enUS']

  with cards_file.open('w', encoding='utf-8') as f:
    json.dump(cardlist, f)

# Done loading cards


# From https://github.com/fmoo/python-varint/blob/master/varint.py
def read_varint(stream):
    shift = 0
    result = 0
    while True:
        byte = stream.read(1)
        if byte in [None, b'']:
            break
        raw = ord(byte)
        result |= (raw & 0x7f) << shift
        shift += 7
        if not (raw & 0x80):
            break

    return result
    
def read_array(stream, element_size=1):
    length = read_varint(stream)
    array = []
    for i in range(length):
        if element_size == 1:
            element = read_varint(stream)
        else:
            element = tuple((read_varint(stream) for j in range(element_size)))
        array.append(element)
    return array

# From https://github.com/HearthSim/HearthDb/blob/master/HearthDb/Deckstrings/DeckSerializer.cs
def decode_decklist(decklist):
  import base64
  from io import BytesIO

  stream = BytesIO(base64.b64decode(decklist))
  read_varint(stream) # Unused
  read_varint(stream) # Encoding version (1)

  deck_format = read_varint(stream)

  heroes = read_array(stream)
  singletons = read_array(stream)
  doubletons = read_array(stream)
  multicards = read_array(stream) # TODO zero what these are, or if this even works

  has_sideboard = read_varint(stream)
  if has_sideboard == 1: # Sideboard cards are listed as (card, parent_card)
      sb_singletons = read_array(stream, element_size=2)
      singletons += [e[0] for e in sb_singletons]
      sb_doubletons = read_array(stream, element_size=2)
      doubletons += [e[0] for e in sb_doubletons]
      sb_multicards = read_array(stream, element_size=2)
      multicards += [e[0] for e in sb_multicards]
  
  cards = singletons + doubletons + doubletons
  normalized_cards = normalize_deck(cards)
  normalized_cards.sort()

  # for i, card in enumerate(normalized_cards):
  #   print(f'Card {i+1:<2}: {card:<5} {cardlist[card]}')

  return normalized_cards

# Simulate C++/C# truncation
def trunc(val, bits=64):
  val = val & (2 ** bits - 1) # Truncate high bits
  if val & (2 ** (bits - 1)): # Adjust for sign
    return val - (2 ** bits)
  return val

def normalize_deck(cards):
  normalized_cards = []
  for card in cards:
    card_variants = [k for k, v in cardlist.items() if v == cardlist[card]]
    normalized_cards.append(min(card_variants))

  normalized_cards.sort()
  return normalized_cards

def bad_hash(x, val=0):
  return x ^ trunc(val + 2654435769 + (x << 6) + (x >> 2))

def hash_deck(cards):
  hash = 0
  for card in cards:
    hash = trunc(bad_hash(hash, card))
  return hash

decklist = decode_decklist('AAEBAaoIDLSKBLaKBKyfBNugBOCgBJbUBKDUBKnUBPzbBMviBJakBfCuBQmf1ASo2QS12QT03ASz3QS14gSl5ATF7QTK7QQA')

print('Actual hash:  ', hash_deck(decklist))
print('Expected hash: -8433254302802380797')

unknown_hash = 4901740154402535512 # For the new deck code :)
decklist2024 = decode_decklist('AAEBAdT8BSiTB/kOjhDSEZAVt2z5rALDtAL2vwLdwgKD1AKM7wKTgAPRiQPEmAOhqQOFsQO6tgOTzQPq4QOR5APy6QOo7wPL+QOmgQSvjgS7rASStQS7zgSX7wSi7wSfpAX9xAWp5QWt6QXa+gXRnAaSngaeogbmqQYAAAEDhM4C/cQF97gD/cQF1JUG/cQFAAA=')

print('Actual hash:  ', hash_deck(decklist2024))
print('Expected hash:', unknown_hash)



def bits(x, bits=64):
  if x & (1 << (bits - 1)): # Adjust for sign
    x = x + (1 << bits)
  str = bin(x).replace('0b', '')[-bits:]
  return '0' * (bits - len(str)) + str


def reverse_hash(y, val, debug=False, x=None):
  # We don't have any real data about the first two bits, but usually they will trial-and-error away.
  for initial_guess in [0b00, 0b01, 0b10, 0b11]:
    guess = initial_guess
    for j in range(2, 64):
      mask = (1 << (j - 1)) - 1
      bit = 1 << j
      
      if (bad_hash(guess, val) & mask) == (y & mask):
        continue
      elif (bad_hash(guess | bit, val) & mask) == (y & mask):
        guess |= bit
        continue
      break
    # Double check in case we exited early (also verifies the high 2 bits)
    if bad_hash(trunc(guess), val) != y:
      if debug:
        print('For initial guess', initial_guess)
        print(bits(guess), guess, 'guess')
        print(bits(x), x, 'x')
        print(bits(y), y, 'y')
        print(bits(bad_hash(x, val)), bad_hash(x, val), 'hash')
      continue
    return guess
  return None


def test1():
  import random
  seed = random.randint(0, 1 << 64)
  print('seed =', seed)
  for i in range(100):
    x = random.randint(-1 << 63, 1 << 63)
    v = random.randint(1, 1000)
    y = bad_hash(x, v)
    guess = reverse_hash(y, v)
    if guess == None:
      reverse_hash(y, v, debug=True, x=x)
      assert False
      
  print('Test1 passed')

def test2():
  hash = 0
  cards = decode_decklist('AAEBAaoIDLSKBLaKBKyfBNugBOCgBJbUBKDUBKnUBPzbBMviBJakBfCuBQmf1ASo2QS12QT03ASz3QS14gSl5ATF7QTK7QQA')
  for card in cards:
    hash = bad_hash(hash, card)
    rhash = reverse_hash(hash, card)
    assert rhash is not None
    # rhash will not always exactly match hash
  print('Test2 passed')

if __name__ == '__main__':
  pass
  # test1()
  # test2()
  # test3()
  
