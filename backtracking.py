from csp import Constraint, Variable, CSP
from constraints import *

import random


# ADDED

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

def ship_constraints(board, ships, hints):
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

  for coord in hints:
    if board[coord[0]][coord[1]] != coord[2]:
      return False
  
  return list(ship_count.values()) == [int(ship) for ship in ships]
              


class UnassignedVars:
    '''class for holding the unassigned variables of a CSP. We can extract
       from, re-initialize it, and return variables to it.  Object is
       initialized by passing a select_criteria (to determine the
       order variables are extracted) and the CSP object.

       select_criteria = ['random', 'fixed', 'mrv'] with
       'random' == select a random unassigned variable
       'fixed'  == follow the ordering of the CSP variables (i.e.,
                   csp.variables()[0] before csp.variables()[1]
       'mrv'    == select the variable with minimum values in its current domain
                   break ties by the ordering in the CSP variables.
    '''
    def __init__(self, select_criteria, csp):
        if select_criteria not in ['random', 'fixed', 'mrv']:
            pass #print "Error UnassignedVars given an illegal selection criteria {}. Must be one of 'random', 'stack', 'queue', or 'mrv'".format(select_criteria)
        self.unassigned = list(csp.variables())
        self.csp = csp
        self._select = select_criteria
        if select_criteria == 'fixed':
            #reverse unassigned list so that we can add and extract from the back
            self.unassigned.reverse()

    def extract(self):
        if not self.unassigned:
            pass #print "Warning, extracting from empty unassigned list"
            return None
        if self._select == 'random':
            i = random.randint(0,len(self.unassigned)-1)
            nxtvar = self.unassigned[i]
            self.unassigned[i] = self.unassigned[-1]
            self.unassigned.pop()
            return nxtvar
        if self._select == 'fixed':
            return self.unassigned.pop()
        if self._select == 'mrv':
            nxtvar = min(self.unassigned, key=lambda v: v.curDomainSize())
            self.unassigned.remove(nxtvar)
            return nxtvar

    def empty(self):
        return len(self.unassigned) == 0

    def insert(self, var):
        if not var in self.csp.variables():
            pass #print "Error, trying to insert variable {} in unassigned that is not in the CSP problem".format(var.name())
        else:
            self.unassigned.append(var)

def bt_search(algo, csp, variableHeuristic, allSolutions, trace, ships=None, hints=None, size=0):
    '''Main interface routine for calling different forms of backtracking search
       algorithm is one of ['BT', 'FC', 'GAC']
       csp is a CSP object specifying the csp problem to solve
       variableHeuristic is one of ['random', 'fixed', 'mrv']
       allSolutions True or False. True means we want to find all solutions.
       trace True of False. True means turn on tracing of the algorithm

       bt_search returns a list of solutions. Each solution is itself a list
       of pairs (var, value). Where var is a Variable object, and value is
       a value from its domain.
    '''
    varHeuristics = ['random', 'fixed', 'mrv']
    algorithms = ['BT', 'FC', 'GAC']

    #statistics
    bt_search.nodesExplored = 0

    if variableHeuristic not in varHeuristics:
        pass #print "Error. Unknown variable heursitics {}. Must be one of {}.".format(
            #variableHeuristic, varHeuristics)
    if algo not in algorithms:
        pass #print "Error. Unknown algorithm heursitics {}. Must be one of {}.".format(
            #algo, algorithms)

    uv = UnassignedVars(variableHeuristic,csp)
    Variable.clearUndoDict()
    for v in csp.variables():
        v.reset()
    if algo == 'BT':
         solutions = BT(uv, csp, allSolutions, trace)

    elif algo == 'GAC':
        GacEnforce(csp.constraints(), csp, None, None) #GAC at the root
        solutions = GAC(uv, csp, allSolutions, trace)

    elif algo == 'shipGAC':
        GacEnforce(csp.constraints(), csp, None, None) #GAC at the root
        solutions = shipGAC(uv, csp, allSolutions, trace, ships, hints, size)
    """
    elif algo == 'FC':
        for cnstr in csp.constraints():
            if cnstr.arity() == 1:
                FCCheck(cnstr, None, None)  #FC with unary constraints at the root
        solutions = FC(uv, csp, allSolutions, trace)
    """

    return solutions, bt_search.nodesExplored

def BT(unAssignedVars, csp, allSolutions, trace):
    '''Backtracking Search. unAssignedVars is the current set of
       unassigned variables.  csp is the csp problem, allSolutions is
       True if you want all solutionss trace if you want some tracing
       of variable assignments tried and constraints failed. Returns
       the set of solutions found.

      To handle finding 'allSolutions', at every stage we collect
      up the solutions returned by the recursive  calls, and
      then return a list of all of them.

      If we are only looking for one solution we stop trying
      further values of the variable currently being tried as
      soon as one of the recursive calls returns some solutions.
    '''
    if unAssignedVars.empty():
        if trace: pass #print "{} Solution Found".format(csp.name())
        soln = []
        for v in csp.variables():
            soln.append((v, v.getValue()))
        return [soln]  #each call returns a list of solutions found
    bt_search.nodesExplored += 1
    solns = []         #so far we have no solutions recursive calls
    nxtvar = unAssignedVars.extract()
    if trace: pass #print "==>Trying {}".format(nxtvar.name())
    for val in nxtvar.domain():
        if trace: pass #print "==> {} = {}".format(nxtvar.name(), val)
        nxtvar.setValue(val)
        constraintsOK = True
        for cnstr in csp.constraintsOf(nxtvar):
            if cnstr.numUnassigned() == 0:
                if not cnstr.check():
                    constraintsOK = False
                    if trace: pass #print "<==falsified constraint\n"
                    break
        if constraintsOK:
            new_solns = BT(unAssignedVars, csp, allSolutions, trace)
            if new_solns:
                solns.extend(new_solns)
            if len(solns) > 0 and not allSolutions:
                break  #don't bother with other values of nxtvar
                       #as we found a soln.
    nxtvar.unAssign()
    unAssignedVars.insert(nxtvar)
    return solns


def GacEnforce(cnstrs, csp, assignedvar, assignedval):
    #cnstrs is a collection of constraints not known GAC
    #establish GAC on them and on all affected constraints
    while cnstrs:
        cnstr = cnstrs.pop(0) 
        for var in cnstr.scope():
            for val in var.curDomain():
                if not cnstr.hasSupport(var, val):
                    var.pruneValue(val, assignedvar, assignedval)
                    if var.curDomainSize() == 0:
                        return "DWO" #domain wipe out
                    for recheck in csp.constraintsOf(var):
                        if recheck != cnstr and recheck not in cnstrs:
                            cnstrs.append(recheck)
    return "OK"


def GAC(unAssignedVars, csp, allSolutions, trace): #search while maintaining GAC
    
    if unAssignedVars.empty():
        if trace: pass
        soln = []
        for v in csp.variables():
            soln.append((v, v.getValue()))
        return [soln]


    solns = []
    nxtvar = unAssignedVars.extract()
    if trace: pass
    for val in nxtvar.curDomain():
        if trace: pass
        nxtvar.setValue(val)
        noDWO = True
        if GacEnforce(csp.constraintsOf(nxtvar), csp, nxtvar, val) == "DWO":
            noDWO = False
        if noDWO:
            new_solns = GAC(unAssignedVars, csp, allSolutions, trace)
            if new_solns:
                solns.extend(new_solns)
            if len(solns) > 0 and not allSolutions:
                break
        Variable.restoreValues(nxtvar, val)
    nxtvar.setValue(None)
    unAssignedVars.insert(nxtvar)
    return solns


def shipGAC(unAssignedVars, csp, allSolutions, trace, ships, hints, size): #search while maintaining GAC
    
    if unAssignedVars.empty():
        soln = []
        for v in csp.variables():
            soln.append((v, v.getValue()))
        board = print_solution(soln, size)
        if ship_constraints(board, ships, hints) and allSolutions:
            return [soln]
        else:
            return []

    solns = []
    nxtvar = unAssignedVars.extract()
    for val in nxtvar.curDomain():
        nxtvar.setValue(val)
        noDWO = True
        if GacEnforce(csp.constraintsOf(nxtvar), csp, nxtvar, val) == "DWO":
            noDWO = False
        if noDWO:
            new_solns = shipGAC(unAssignedVars, csp, allSolutions, trace, ships, hints, size)
            if new_solns:
                return new_solns
            if len(solns) > 0 and not allSolutions:
                break
        Variable.restoreValues(nxtvar, val)
    nxtvar.setValue(None)
    unAssignedVars.insert(nxtvar)
    return solns
