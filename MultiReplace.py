# coding=utf-8

import re

def multiwordReplace(text, wordDic):
    """
    take a text and replace words that match a key in a dictionary with the associated value, return the changed text
    """
    rc = re.compile('|'.join(map(re.escape, wordDic)))
    def translate(match):
        return wordDic[match.group(0)]
    return rc.sub(translate, text)

str1 = \
"""

"""

# the dictionary has target_word : replacement_word pairs
wordDic = {
'Class nav text':'Common string',
'Class hat table header':'Common string',
'Map type':'Common string',
'Update name':'Common string',
'Map name':'Common string',
'Update name':'Common string',
'class nav text':'Common string',
'class hat table header':'Common string',
'map type':'Common string',
'update name':'Common string',
'map name':'Common string',
'update name':'Common string',
}

# call the function and get the changed text
str2 = multiwordReplace(str1, wordDic)

print str2
