from csp import Constraint, Variable, CSP
from constraints import *
from backtracking import bt_search
import sys
import argparse

def print_solution(s, size):
  solutions = []
  s_ = {}
  for (var, val) in s:
    s_[int(var.name())] = val
  for i in range(1, size-1):
    row = []
    for j in range(1, size-1):
      row.append(s_[-1-(i*size+j)])
    solutions.append(row)
  return solutions

#parse board and ships info
#file = open(sys.argv[1], 'r')
#b = file.read()
parser = argparse.ArgumentParser()
parser.add_argument(
  "--inputfile",
  type=str,
  required=True,
  help="The input file that contains the puzzles."
)
parser.add_argument(
  "--outputfile",
  type=str,
  required=True,
  help="The output file that contains the solution."
)
args = parser.parse_args()
file = open(args.inputfile, 'r')
b = file.read()
b2 = b.split()

ships = b2[2]

hints = []
for y in range (len(b2[0])):
  for x in range (len(b2[0])):
    if (b2[3:])[y][x] != '0':
      hints.append((y, x, (b2[3:])[y][x]))


size = len(b2[0])
size = size + 2
b3 = []
b3 += ['0' + b2[0] + '0']
b3 += ['0' + b2[1] + '0']
b3 += [b2[2] + ('0' if len(b2[2]) == 3 else '')]
b3 += ['0' * size]
for i in range(3, len(b2)):
  b3 += ['0' + b2[i] + '0']
b3 += ['0' * size]
board = "\n".join(b3)

varlist = []
varn = {}
conslist = []

#1/0 variables
for i in range(0,size):
  for j in range(0, size):
    v = None
    if i == 0 or i == size-1 or j == 0 or j == size-1:
      v = Variable(str(-1-(i*size+j)), [0])
    else:
      v = Variable(str(-1-(i*size+j)), [0,1])
    varlist.append(v)
    varn[str(-1-(i*size+j))] = v

#make 1/0 variables match board info
ii = 0
for i in board.split()[3:]:
  jj = 0
  for j in i:
    if j != '0' and j != '.':
      conslist.append(TableConstraint('boolean_match', [varn[str(-1-(ii*size+jj))]], [[1]]))
    elif j == '.':
      conslist.append(TableConstraint('boolean_match', [varn[str(-1-(ii*size+jj))]], [[0]]))
    jj += 1
  ii += 1

#row and column constraints on 1/0 variables
row_constraint = []
for i in board.split()[0]:
  row_constraint += [int(i)]

for row in range(0,size):
  conslist.append(NValuesConstraint('row', [varn[str(-1-(row*size+col))] for col in range(0,size)], [1], row_constraint[row], row_constraint[row]))

col_constraint = []
for i in board.split()[1]:
  col_constraint += [int(i)]

for col in range(0,size):
  conslist.append(NValuesConstraint('col', [varn[str(-1-(col+row*size))] for row in range(0,size)], [1], col_constraint[col], col_constraint[col]))

#diagonal constraints on 1/0 variables
for i in range(1, size-1):
    for j in range(1, size-1):
      for k in range(9):
        conslist.append(NValuesConstraint('diag', [varn[str(-1-(i*size+j))], varn[str(-1-((i-1)*size+(j-1)))]], [1], 0, 1))
        conslist.append(NValuesConstraint('diag', [varn[str(-1-(i*size+j))], varn[str(-1-((i-1)*size+(j+1)))]], [1], 0, 1))
  

# at least one in every 5 vertical/horizontal lines are a 0 (this didnt work)
#for i in range(1, size-5):
    #for j in range(1, size-5):
      #for k in range(9):
        #conslist.append(NValuesConstraint('vert', [varn[str(-1-(i*size+j))], varn[str(-1-((i+1)*size+j))], varn[str(-1-((i+2)*size+j))], varn[str(-1-((i+3)*size+j))], varn[str(-1-((i+4)*size+j))]], [0], 1, 5))
        #conslist.append(NValuesConstraint('hor', [varn[str(-1-(i*size+j))], varn[str(-1-(i*size+(j+1)))], varn[str(-1-(i+1*size+(j+2)))], varn[str(-1-(i*size+(j+3)))], varn[str(-1-(i*size+(j+4)))]], [0], 1, 5))

#./S/</>/v/^/M variables
#these would be added to the csp as well, before searching,
#along with other constraints

"""
for i in range(0, size):
  for j in range(0, size):
    v = Variable(str(i*size+j), ['.', 'S', '<', '^', 'v', 'M', '>'])
    varlist.append(v)
    varn[str(str(i*size+j))] = v
    #connect 1/0 variables to W/S/L/R/B/T/M variables
    conslist.append(TableConstraint('connect', [varn[str(-1-(i*size+j))], varn[str(i*size+j)]], [[0,'.'],[1,'S'],[1,'<'],[1,'^'],[1,'v'],[1,'M'],[1,'>']]))
    print(conslist)



#horizontal constraints on ./S/</>/v/^/M variables

for i in range(1, size-1):
  for j in range(1, size-1):
    varn[str(str(i*size+j))] = v
    # S
    conslist.append(TableConstraint('surrounding', [varn[str((i*size+j))], varn[str((i+1)*size+j)], varn[str(i*size+(j+1))], varn[str(i*size+(j-1))], varn[str((i-1)*size+j)]], ['S', '.', '.', '.', '.']))
    # <
    conslist.append(TableConstraint('surrounding', [varn[str((i*size+j))], varn[str((i+1)*size+j)], varn[str(i*size+(j+1))], varn[str(i*size+(j-1))], varn[str((i-1)*size+j)]], ['S', '.', '.', '.', '.']))


"""



def ship_constraints(board, ships, predetermined):
  count = 0
        
  for i, row in enumerate(board):
    for j, cell in enumerate(row):
      if cell == 1:
        if (i == 0 or board[i - 1][j] == 0) and\
          (j == 0 or board[i][j - 1] == 0):
          count += 1
                            
  if count != (int(ships[0]) + int(ships[1]) + int(ships[2]) + int(ships[3])):
    return False

  ship_count = {
    1: 0,
    2: 0,
    3: 0,
    4: 0
  }

  for i in range (len(board)):
    for j in range (len(board)):
      if board[i][j] == 0:
        board[i][j] = '.'
      if board[i][j] == 1:
        # traverse down
        if j == len(board) - 1 or board[i][j+1] == 0:
          temp_i = i
          while board[temp_i][j] == 1:
            temp_i += 1
            
            if temp_i-i > 4:
              return False
            
            if temp_i == len(board):
              break
            
          
          if temp_i-i == 1:
            board[i][j] = 'S'
          elif temp_i-i == 2:
            board[i][j] = '^'
            board[i+1][j] = 'v'
          elif temp_i-i == 3:
            board[i][j] = '^'
            board[i+1][j] = 'M'
            board[i+2][j] = 'v'
          else:
            board[i][j] = '^'
            board[i+1][j] = 'M'
            board[i+2][j] = 'M'
            board[i+3][j] = 'v'
    
          ship_count[temp_i-i] += 1
        else:
          # traverse right
          temp_j = j
          while board[i][temp_j] == 1:
            temp_j += 1

            if temp_j - j > 4:
              return False

            if temp_j == len(board):
              break
          
          if temp_j-j == 1:
            board[i][j] = 'S'
          elif temp_j-j == 2:
            board[i][j] = '<'
            board[i][j+1] = '>'
          elif temp_j-j == 3:
            board[i][j] = '<'
            board[i][j+1] = 'M'
            board[i][j+2] = '>'
          else:
            board[i][j] = '<'
            board[i][j+1] = 'M'
            board[i][j+2] = 'M'
            board[i][j+3] = '>'

          ship_count[temp_j-j]  += 1

  for coord in predetermined:
    if board[coord[0]][coord[1]] != coord[2]:
      return False
  
  return list(ship_count.values()) == [int(ship) for ship in ships]
              

#find all solutions and check which one has right ship #'s
csp = CSP('battleship', varlist, conslist)
"""
solutions, num_nodes = bt_search('GAC', csp, 'mrv', True, False)
sys.stdout = open(args.outputfile, 'w')
for i in range(len(solutions)):
    board = print_solution(solutions[i], size)
    if count_ships(board, ships, hints):
      for row in board:
        print(''.join(row))
      break
"""


solutions, num_nodes = bt_search('shipGAC', csp, 'mrv', True, False, ships, hints, size)
sys.stdout = open(args.outputfile, 'w')
for i in range(len(solutions)):
    board = print_solution(solutions[i], size)
    if ship_constraints(board, ships, hints):
      for row in board:
        print(''.join(row))
      break
      

