# -*- coding: utf-8 -*-
from wikitools.api import APIRequest
from wikitools.wiki import Wiki
from wikitools.page import Page
pairs = [
  ['"', '"'],
  ['(', ')'],
  ['[', ']'],
  ['{', '}'],
  ['<!--', '-->'],
  ['<', '>'],
  ['<includeonly>', '</includeonly>'],
  ['<noinclude>', '</noinclude>'],
  ['<onlyinclude>', '</onlyinclude>'],
  ['<small>', '</small>'],
  ['<table>', '</table>'],
  ['<td>', '</td>'],
  ['<tr>', '</tr>'],
]

wiki = Wiki('http://wiki.teamfortress.com/w/api.php')

# Returns a list of unmatched element indices.
def find_mismatch(text, pair):
  problems = []
  for i, char in enumerate(text):
    if char == pair[0]:
      problems.append(i)
    if char == pair[1]:
      try:
        problems.pop()
      except IndexError:
        return [i]
  return problems

params = {
  'action': 'query',
  'list': 'allpages',
  'apfilterredir': 'nonredirects',
  'aplimit': '500',
}
titles = set()
req = APIRequest(wiki, params)
for result in req.queryGen():
  for article in result['query']['allpages']:
    titles.add(article['title'])
titles = list(titles)
titles.sort()
print 'Found', len(titles), 'pages'

for title in titles:
  page = Page(wiki, title)
  page.getWikiText()
  text = page.getWikiText()
  for pair in pairs:
    if text.count(pair[0]) != text.count(pair[1]):
      indices = find_mismatch(text, pair)
      for index in indices:
        print '-'*80
        print pair, title
        print '-'*80
        print text[index-100:index+100]
        print '='*80
