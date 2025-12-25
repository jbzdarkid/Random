"""
I was looking into the odds of rolling windfury on Galvadon, and I'm coming up with at-best an 86% chance, although I don't think that's the best strategy.

There's essentially 5 categories of adaptations: +3 attack, +1/1, Windfury, [Other keyword adapts], [All other adapts].
Notably, if you pick any keyword ability, you won't be offered it again, so this increases the chances of other good adaptations.

I was able to come up with 6 strategies, assuming that:
- You always pick +3 attack over +1/1
- You always pick windfury over any other keyword
- You stop picking keyword abilities once you have windfury

The naming convention is a bit concise, but you can decode it like so:
"windfury_keyword_3_1" means
Prioritize Windfury > Other keywords > +3 attack > +1/1 > everything else


Strategy             | % Windfury | +Attack | Base 5 | Base 8 | Base 9 | Base 12
---------------------+------------+---------+--------+--------+--------+---------
windfury_keyword_3_1 | 86.28      | 3.3363  | 15.69  | 21.28  | 23.14  | 28.73
windfury_3_keyword_1 | 84.28      | 4.6842  | 17.69  | 23.22  | 25.06  | 30.59
windfury_3_1_keyword | 82.70      | 5.0116  | 18.06  | 23.54  | 25.37  | 30.85
3_windfury_keyword_1 | 73.81      | 5.1403  | 17.31  | 22.53  | 24.27  | 29.48
3_windfury_1_keyword | 72.81      | 5.4869  | 17.73  | 22.91  | 24.64  | 29.82
3_1_windfury_keyword | 61.18      | 5.6243  | 16.70  | 21.54  | 23.15  | 27.99


Unsurprisingly, the later in priority you pick windfury, the less chance you have of it.
However, picking keywords only slightly raises the chance of finding windfury, and it costs a significant amount of attack.
I ran some numbers for some of the common base attack values of Galvadon (with +4 location and/or Crystal Core),
at least the average values seem to show a clear winner -- prioritize windfury > +3 attack > +1/1 > any other keyword.

Obviously it's not that cut-and-dried, though. In any given scenario, you aren't just trying to "maximize attack", you have a particular target value you're aiming for.
However, it is still correct to pick +3 attack when offered -- unless you can reach your target with *only* windfury.
In general: Pick windfury, pick +3 attack, and if neither are offered, count your damage.
If you don't have windfury yet, determine if you need an additional +3 attack (or multiple).
- If you strictly need +3 attack (or have enough once you hit windfury), pick keywords to improve the windfury odds.
- If you can get by with +1/1 instead of +3 attack, pick that and then prioritize keywords over any further attack buffs.
"""

from random import choices


all_adapts = 'divine_shield, 3_attack, windfury, elusive, deathrattle, taunt, poisonous, 3_health, stealth, plus_1_1'.split(', ')
keyword_adapts = 'divine_shield, windfury, elusive, taunt, poisonous, stealth'.split(', ')


def strat_windfury_keyword_3_1(adapts, has_windfury):
  if 'windfury' in adapts:
    return 'windfury'
  elif not has_windfury and set(keyword_adapts).intersection(adapts):
    return next((a for a in adapts if a in keyword_adapts))
  elif '3_attack' in adapts:
    return '3_attack'
  elif 'plus_1_1' in adapts:
    return 'plus_1_1'
  return adapts[0]

def strat_windfury_3_keyword_1(adapts, has_windfury):
  if 'windfury' in adapts:
    return 'windfury'
  elif '3_attack' in adapts:
    return '3_attack'
  elif not has_windfury and set(keyword_adapts).intersection(adapts):
    return next((a for a in adapts if a in keyword_adapts))
  elif 'plus_1_1' in adapts:
    return 'plus_1_1'
  return adapts[0]

def strat_windfury_3_1_keyword(adapts, has_windfury):
  if 'windfury' in adapts:
    return 'windfury'
  elif '3_attack' in adapts:
    return '3_attack'
  elif 'plus_1_1' in adapts:
    return 'plus_1_1'
  elif not has_windfury and set(keyword_adapts).intersection(adapts):
    return next((a for a in adapts if a in keyword_adapts))
  return adapts[0]

def strat_3_windfury_keyword_1(adapts, has_windfury):
  if '3_attack' in adapts:
    return '3_attack'
  elif 'windfury' in adapts:
    return 'windfury'
  elif not has_windfury and set(keyword_adapts).intersection(adapts):
    return next((a for a in adapts if a in keyword_adapts))
  elif 'plus_1_1' in adapts:
    return 'plus_1_1'
  return adapts[0]

def strat_3_windfury_1_keyword(adapts, has_windfury):
  if '3_attack' in adapts:
    return '3_attack'
  elif 'windfury' in adapts:
    return 'windfury'
  elif 'plus_1_1' in adapts:
    return 'plus_1_1'
  elif not has_windfury and set(keyword_adapts).intersection(adapts):
    return next((a for a in adapts if a in keyword_adapts))
  return adapts[0]

def strat_3_1_windfury_keyword(adapts, has_windfury):
  if '3_attack' in adapts:
    return '3_attack'
  elif 'plus_1_1' in adapts:
    return 'plus_1_1'
  elif 'windfury' in adapts:
    return 'windfury'
  elif not has_windfury and set(keyword_adapts).intersection(adapts):
    return next((a for a in adapts if a in keyword_adapts))
  return adapts[0]


def adapt_with_strategy(strategy, total_adapts=5):
  available_adapts = list(all_adapts)
  adapts = []
  for i in range(total_adapts):
    adapt_options = choices(available_adapts, k=3)
    selected_adapt = strategy(adapt_options, 'windfury' in adapts)
    assert selected_adapt in adapt_options # Make sure the strategy doesn't accidentially cheat
    if selected_adapt in keyword_adapts:
      available_adapts = [a for a in available_adapts if a != selected_adapt]
    adapts.append(selected_adapt)
  return adapts


def summarize(adapts):
  output = {'windfury': 0.0, 'attack': 0.0}
  for adapt in adapts:
    if adapt == '3_attack':
      output['attack'] += 3
    elif adapt == 'plus_1_1':
      output['attack'] += 1
    elif adapt == 'windfury':
      output['windfury'] = 1.0
  return output


N = 1_000_000 # Random trials, for now
RANGE = (13, 48)
BASE = 12
strategies = [strat_windfury_keyword_3_1, strat_windfury_3_keyword_1, strat_windfury_3_1_keyword, strat_3_windfury_keyword_1, strat_3_windfury_1_keyword, strat_3_1_windfury_keyword]
longest_name = max([len(s.__name__) for s in strategies])
print('Strategy name'.ljust(longest_name) + ' | % Windfury | +Attack |')
print('-'*longest_name                    + '-+------------+---------+')

damage_odds = [{} for s in strategies] # These will need to go into a separate table.
for i, strategy in enumerate(strategies):
  outcomes = [summarize(adapt_with_strategy(strategy)) for _ in range(N)]

  windfury_avg = round(100.0 * sum([o['windfury'] for o in outcomes]) / N, 2)
  attack_avg = round(sum([o['attack'] for o in outcomes]) / N, 4)
  print(f'{strategy.__name__} | {windfury_avg:<10} | {attack_avg:<7} |')

  damages = [((BASE + o['attack']) * (2 if o['windfury'] else 1)) for o in outcomes]
  for target in range(*RANGE):
    damage_odds[i][target] = sum((d >= target for d in damages))

# Find the winning strategy for each attack value
best_odds = {}
for target in range(*RANGE):
  best_odds[target] = max((d[target] for d in damage_odds))

# Now format the output
print('Strategy|', end='')
for target in range(*RANGE):
  print(f' {target:<3}|', end='')
print()
print('--------+', end='')
for target in range(*RANGE):
  print(f'----+', end='')
print()
for i, strategy in enumerate(strategies):
  strat_name = '_'.join([w[0] for w in strategy.__name__.split('_')[1:]])
  print(f'{strat_name} |', end='')
  for target in range(*RANGE):
    if best_odds[target] == damage_odds[i][target]:
      perc = 100.0 * best_odds[target] / N
      if round(perc, 0) < 10.0:
        print(f'{perc:0.02f}|', end='')
      else:
        print(f'{perc:0.01f}|', end='')
    else:
      delta = 100.0 * (best_odds[target] - damage_odds[i][target]) / N
      if round(delta, 0) >= 10.0:
        print(f'<-10|', end='')
      else:
        print(f'-{delta:0.01f}|', end='')
  print()


# 21 attack (from a base of 8):
# +13 (no windfury) -or- +3, windfury.
# 20 attack is just +12, which is *very hard* but still possible, somewhat. If you start taking windfury over +3, this becomes dangerous.
# 31 attack is the threshold where you need to stop picking windfury first.