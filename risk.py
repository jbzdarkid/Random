import itertools

def roll_dice(num_dice):
  return itertools.product(range(1, 7), repeat=num_dice)

def risk_battle(num_atk, num_def):
  outcomes = [0] * (num_def + 1)
  for dice in roll_dice(num_atk + num_def):
    atk_dice = sorted(dice[0:num_atk], reverse=True)
    def_dice = sorted(dice[-num_def:], reverse=True)

    outcome = 0
    if atk_dice[0] > def_dice[0]:
      outcome += 1
    if num_atk > 1 and num_def > 1 and atk_dice[1] > def_dice[1]:
      outcome += 1

    outcomes[outcome] += 1

  print(f'Odds in a {num_atk}v{num_def}:')
  print(f'0 defenders die: {outcomes[0] / sum(outcomes)}')
  print(f'1 defender dies: {outcomes[1] / sum(outcomes)}')
  if num_def > 1:
    print(f'2 defenders die: {outcomes[2] / sum(outcomes)}')


risk_battle(1, 1)
risk_battle(1, 2)
risk_battle(2, 1)
risk_battle(2, 2)
risk_battle(3, 1)
risk_battle(3, 2)
