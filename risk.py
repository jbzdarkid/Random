import itertools

def roll_dice(num_dice):
  return itertools.product(range(1, 7), repeat=num_dice)

def risk_battle(num_atk, num_def, ammo_shortage=False, fortified=False):
  outcomes = [0] * (num_def + 1)
  for dice in roll_dice(num_atk + num_def):
    atk_dice = sorted(dice[0:num_atk], reverse=True)
    def_dice = sorted(dice[-num_def:], reverse=True)
    if ammo_shortage:
      def_dice[0] -= 1
      def_dice.sort()
    if fortified:
      atk_dice[0] += 1
      atk_dice.sort()

    outcome = 0
    if atk_dice[0] > def_dice[0]:
      outcome += 1
    if num_atk > 1 and num_def > 1 and atk_dice[1] > def_dice[1]:
      outcome += 1

    outcomes[outcome] += 1

  return outcomes

def to_percent(odds):
  rounded_odds = str(round(100  * odds, 2))
  if odds < 0.1:
    rounded_odds = ' ' + rounded_odds
  return rounded_odds.ljust(5, '0') + '%'

def risk_war(rounds, num_atk, num_def, ammo_shortage=False, fortified=False):
  outcomes = risk_battle(num_atk, num_def, ammo_shortage, fortified)
  outcomes_product = [0] * ((len(outcomes)-1) * rounds + 1)

  for i in range(rounds):
    for j in range(len(outcomes)):
      outcomes_product[i+j] += outcomes[i] * outcomes[j]

  print(f'Odds in a {num_atk}v{num_def}', end='')
  if rounds > 1:
    print(f' (with {rounds} rounds)', end='')
  print(':')

  ev = 0
  for i, outcome in enumerate(outcomes_product):
    odds = outcome / sum(outcomes_product)
    ev += i * odds
    if i == 1:
      print(f'{i} defender dies: {to_percent(odds)}')
    else:
      print(f'{i} defenders die: {to_percent(odds)}')
  print(f'Expected defender deaths: {round(ev, 2)}')

#risk_battle(1, 1)
#risk_battle(1, 2)
#risk_battle(2, 1)
#risk_battle(2, 2)
risk_war(2, 3, 1)
risk_war(1, 3, 2)
risk_war(2, 3, 1, fortified=True)
risk_war(1, 3, 2, fortified=True)
