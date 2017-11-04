puzzleMaps = [[
  [1,1,3,1],
  [3,2,0,0],
  [1,0,1,3]
],[
  [0,1,1,3],
  [3,1,2,2],
  [2,0,0,2]
],[
  [2,1,3,2],
  [0,3,0,1],
  [2,2,3,1]
],[
  [3,0,3,2],
  [1,2,0,1],
  [1,3,2,0]
],[
  [2,2,0,1],
  [3,0,0,1],
  [3,1,2,0]
]]

for puzzleMap in puzzleMaps:
  minRotation = 999
  minBuffer = ''
  for i in range(4):
    for j in range(3):
      buffer = ''
      grabMap = [
        [0,0,0,0],
        [0,0,0,0],
        [0,0,0,0],
      ]
      grabMap[j][i] = 1
      currRotation = puzzleMap[j][i]
      buffer += 'Grab piece ' + str(i) + ' ' + str(j)+'\n'
      totalRotation = 0
      while 1:
        grabbedPiece = False
        puzzleComplete = True
        for x in range(4):
          for y in range(3):
            if grabMap[y][x] == 0:
              puzzleComplete = False
              if puzzleMap[y][x] == currRotation:
                if ((x > 0 and grabMap[y][x-1] == 1)
                  or (x < 3 and grabMap[y][x+1] == 1)
                  or (y > 0 and grabMap[y-1][x] == 1)
                  or (y < 2 and grabMap[y+1][x] == 1)):
                  buffer += 'Grab piece ' + str(x) + ' ' + str(y)+'\n'
                  grabMap[y][x] = 1
                  grabbedPiece = True
        if grabbedPiece:
          continue
        if not puzzleComplete or currRotation != 0:
          totalRotation += 1
          buffer += 'Rotate\n'
          currRotation -= 1
          currRotation %= 4
          continue
        break
      if totalRotation < minRotation:
        minBuffer = buffer
        minRotation = totalRotation
  print puzzleMap
  print minBuffer
