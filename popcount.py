import requests

redmond = {}
bellevue = {}
king_county = {'for': 'county:033', 'in': 'state:53'}
washington = {'in': 'state:53'}

AGE_65_PLUS = 26
AGE_16_PLUS = 28
AGE_18_PLUS = 29


# https://api.census.gov/data/2019/pep/charagegroups.html
# https://github.com/owid/covid-19-data/tree/master/public/data/vaccinations
r = requests.get('https://api.census.gov/data/2019/pep/charagegroups?get=NAME,POP,AGEGROUP&for=state:*').json()
for row in r[1:]:
  name, pop, age_group, state = row


