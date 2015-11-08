__author__ = 'Sean'

# Sihan Chen
# Project Part 2 : Comparison of CSP and Search Algorithms
# Problem : KenKen

import sys
import functools
import queue
from functools import reduce
from testRead import *
# The primary problem set-up consists of "variables" and "constraints":
#   "variables" are a dictionary of constraint variables (of type ConstraintVar), example variables['A1']
#   "constraints" are a set of binary constraints (of type BinaryConstraint)

# First, Node Consistency is achieved by passing each UnaryConstraint of each variable to nodeConsistent().
# Arc Consistency is achieved by passing "constraints" to Revise().
# AC3 is not fully implemented, Revise() needs to be repeatedly called until all domains are reduced to a single value

class ConstraintVar:
    # instantiation example: ConstraintVar( [1,2,3],'A1' )
    # MISSING filling in neighbors to make it easy to determine what to add to queue when revise() modifies domain
    def __init__( self, d, n ):
        self.domain = [ v for v in d ]
        self.name = n
        self.neighbors = []

class UnaryConstraint:
    # v1 is of class ConstraintVar
    # fn is the lambda expression for the constraint
    # instantiation example: UnaryConstraint( variables['A1'], lambda x: x <= 2 )
    def __init__( self, v, fn ):
        self.var = v
        self.func = fn

class BinaryConstraint:
    # v1 and v2 should be of class ConstraintVar
    # fn is the lambda expression for the constraint
    # instantiate example: BinaryConstraint( A1, A2, lambda x,y: x != y )
    def __init__(self, v1, v2, fn):
        self.var1 = v1
        self.var2 = v2
        self.func = fn

class TernaryConstraint:
    # v1, v2 and v3 should be of class ConstraintVar
    # fn is the lambda expression for the constraint
    # instantiate example: BinaryConstraint( A1, A2, A3 lambda x,y,z: x != y != z )
    def __init__(self, v1, v2, v3, fn):
        self.var1 = v1
        self.var2 = v2
        self.var3 = v3
        self.func = fn

def allDiff( constraints, v ):
    # generate a list of constraints that implement the allDiff constraint for all variable combinations in v
    # constraints is a preconstructed list. v is a list of ConstraintVar instances.
    # call example: allDiff( constraints, [A1,A2,A3] ) will generate BinaryConstraint instances for [[A1,A2],[A2,A1],[A1,A3] ...
    fn = lambda x,y: x != y
    for i in range( len( v ) ):
        for j in range( len( v ) ):
            if ( i != j ) :
                constraints.append( BinaryConstraint( v[ i ], v[ j ], fn ) )

def setUpCrypt(variables, constraints, words, letters, op):
    domain = [i for i in range(10)]

    for l in letters:
        variables[l] = ConstraintVar(domain, l)

    allCons = []
    for k in variables.keys():
        allCons.append( variables[k] )

    # Constrain all letters to different digits
    allDiff( constraints, allCons )

    # Set max word length, constrain all first letters to not 0
    maxWordLength = 0
    maxVarLength = 0
    for w in range(len(words)):
        allCons.append([0])
        constraints.append(UnaryConstraint( variables[words[w][0]], lambda x: x != 0 ))

        if len(words[w]) > maxWordLength:
            maxWordLength = len(words[w])
        if len(words[w]) > maxVarLength and w < len(words)-1:
            maxVarLength = len(words[w])

    # Constrain columns to add up
    for i in range(maxWordLength):
        varLetters = {}

        # Count number of times each letter appears in column
        for j in range(len(words)-1):
            index = len(words[j]) - i - 1
            if i < len(words[j]):
                vlKeys = list(varLetters.keys())
                if (vlKeys.count(words[j][index]) == 0):
                    varLetters[words[j][index]] = 1
                else:
                    varLetters[words[j][index]] += 1

        # Take the letters in solution to account
        j = len(words)-1
        index = len(words[j]) - i - 1
        if i < len(words[j]):
            vlKeys = list(varLetters.keys())
            if (vlKeys.count(words[j][index]) == 0):
                if len(vlKeys) == 0:
                    constraints.append(UnaryConstraint( variables[words[j][index]], lambda x: x < len(words)-1 ))
                else:
                    varLetters[words[j][index]] = -1
            else:
                varLetters[words[j][index]] -= 1
        print(varLetters)

        vlKeys = list(varLetters.keys())

        if maxVarLength - i - 1 == 0:
            if maxVarLength == maxWordLength:

                if len(vlKeys) == 3:
                    constraints.append(TernaryConstraint( variables[vlKeys[0]], variables[vlKeys[1]], variables[vlKeys[2]],
                                        lambda x,y,z,xv=varLetters[vlKeys[0]],yv=varLetters[vlKeys[1]],zv=varLetters[vlKeys[2]]:
                                                      (x*xv + y*yv + z*zv) == 0 or
                                                      (x*xv + y*yv + z*zv) == -(len(words)-2)))
                    constraints.append(TernaryConstraint( variables[vlKeys[2]], variables[vlKeys[1]], variables[vlKeys[0]],
                                        lambda x,y,z,xv=varLetters[vlKeys[2]],yv=varLetters[vlKeys[1]],zv=varLetters[vlKeys[0]]:
                                                      (x*xv + y*yv + z*zv) == 0 or
                                                      (x*xv + y*yv + z*zv) == -(len(words)-2)))
                    constraints.append(TernaryConstraint( variables[vlKeys[1]], variables[vlKeys[0]], variables[vlKeys[2]],
                                        lambda x,y,z,xv=varLetters[vlKeys[1]],yv=varLetters[vlKeys[0]],zv=varLetters[vlKeys[2]]:
                                                      (x*xv + y*yv + z*zv) == 0 or
                                                      (x*xv + y*yv + z*zv) == -(len(words)-2)))
                elif len(vlKeys) == 2:
                    constraints.append(BinaryConstraint( variables[vlKeys[0]], variables[vlKeys[1]],
                                        lambda x,y,xv=varLetters[vlKeys[0]],yv=varLetters[vlKeys[1]]:
                                                      (x*xv + y*yv) == 0 or
                                                      (x*xv + y*yv) == -(len(words)-2)))
                    constraints.append(BinaryConstraint( variables[vlKeys[1]], variables[vlKeys[0]],
                                        lambda x,y,xv=varLetters[vlKeys[1]],yv=varLetters[vlKeys[0]]:
                                                      (x*xv + y*yv) == 0 or
                                                      (x*xv + y*yv) == -(len(words)-2)))
                elif len(vlKeys) == 1:
                    constraints.append(UnaryConstraint( variables[vlKeys[0]],
                                        lambda x,xv=varLetters[vlKeys[0]]:
                                                      (x*xv) == 0 or
                                                      (x*xv) == -(len(words)-2)))

            else:
                if len(vlKeys) == 3:
                    constraints.append(TernaryConstraint( variables[vlKeys[0]], variables[vlKeys[1]], variables[vlKeys[2]],
                                        lambda x,y,z,xv=varLetters[vlKeys[0]],yv=varLetters[vlKeys[1]],zv=varLetters[vlKeys[2]]:
                                                      ((x*xv + y*yv)%10 == 0 or
                                                      (x*xv + y*yv)%10 == -(len(words)-2) or
                                                      (x*xv + y*yv)%10 == 10-(len(words)-2)) and
                                                      (x*xv + y*yv + z*zv)    >= 9))
                    constraints.append(TernaryConstraint( variables[vlKeys[2]], variables[vlKeys[1]], variables[vlKeys[0]],
                                        lambda x,y,z,xv=varLetters[vlKeys[2]],yv=varLetters[vlKeys[1]],zv=varLetters[vlKeys[0]]:
                                                      ((x*xv + y*yv)%10 == 0 or
                                                      (x*xv + y*yv)%10 == -(len(words)-2) or
                                                      (x*xv + y*yv)%10 == 10-(len(words)-2)) and
                                                      (x*xv + y*yv + z*zv)    >= 9))
                    constraints.append(TernaryConstraint( variables[vlKeys[1]], variables[vlKeys[0]], variables[vlKeys[2]],
                                        lambda x,y,z,xv=varLetters[vlKeys[1]],yv=varLetters[vlKeys[0]],zv=varLetters[vlKeys[2]]:
                                                      ((x*xv + y*yv)%10 == 0 or
                                                      (x*xv + y*yv)%10 == -(len(words)-2) or
                                                      (x*xv + y*yv)%10 == 10-(len(words)-2)) and
                                                      (x*xv + y*yv + z*zv)    >= 9))
                elif len(vlKeys) == 2:
                    constraints.append(BinaryConstraint( variables[vlKeys[0]], variables[vlKeys[1]],
                                        lambda x,y,xv=varLetters[vlKeys[0]],yv=varLetters[vlKeys[1]]:
                                                      ((x*xv + y*yv)%10 == 0 or
                                                      (x*xv + y*yv)%10 == -(len(words)-2) or
                                                      (x*xv + y*yv)%10 == 10-(len(words)-2)) and
                                                      (x*xv + y*yv)/9    >= 1))
                    constraints.append(BinaryConstraint( variables[vlKeys[1]], variables[vlKeys[0]],
                                        lambda x,y,xv=varLetters[vlKeys[1]],yv=varLetters[vlKeys[0]]:
                                                      ((x*xv + y*yv)%10 == 0 or
                                                      (x*xv + y*yv)%10 == -(len(words)-2) or
                                                      (x*xv + y*yv)%10 == 10-(len(words)-2)) and
                                                      (x*xv + y*yv)/9    >= 1))
                elif len(vlKeys) == 1:
                    constraints.append(UnaryConstraint( variables[vlKeys[0]],
                                        lambda x,xv=varLetters[vlKeys[0]]:
                                                      ((x*xv)%10 == 0 or
                                                      (x*xv)%10 == -(len(words)-2) or
                                                      (x*xv)%10 == 10-(len(words)-2)) and
                                                      (x*xv)/9    >= 1))
        elif i == 0:
            if len(vlKeys) == 3:
                constraints.append(TernaryConstraint( variables[vlKeys[0]], variables[vlKeys[1]], variables[vlKeys[2]],
                                    lambda x,y,z,xv=varLetters[vlKeys[0]],yv=varLetters[vlKeys[1]],zv=varLetters[vlKeys[2]]:
                                                  (x*xv + y*yv + z*zv)%10 == 0))
                constraints.append(TernaryConstraint( variables[vlKeys[2]], variables[vlKeys[1]], variables[vlKeys[0]],
                                    lambda x,y,z,xv=varLetters[vlKeys[2]],yv=varLetters[vlKeys[1]],zv=varLetters[vlKeys[0]]:
                                                  (x*xv + y*yv + z*zv)%10 == 0))
                constraints.append(TernaryConstraint( variables[vlKeys[1]], variables[vlKeys[0]], variables[vlKeys[2]],
                                    lambda x,y,z,xv=varLetters[vlKeys[1]],yv=varLetters[vlKeys[0]],zv=varLetters[vlKeys[2]]:
                                                  (x*xv + y*yv + z*zv)%10 == 0))
            elif len(vlKeys) == 2:
                constraints.append(BinaryConstraint( variables[vlKeys[0]], variables[vlKeys[1]],
                                    lambda x,y,xv=varLetters[vlKeys[0]],yv=varLetters[vlKeys[1]]:
                                                  (x*xv + y*yv)%10 == 0))
                constraints.append(BinaryConstraint( variables[vlKeys[1]], variables[vlKeys[0]],
                                    lambda x,y,xv=varLetters[vlKeys[1]],yv=varLetters[vlKeys[0]]:
                                                  (x*xv + y*yv)%10 == 0))
            elif len(vlKeys) == 1:
                constraints.append(UnaryConstraint( variables[vlKeys[0]],
                                    lambda x,xv=varLetters[vlKeys[0]]:
                                                  (x*xv)%10 == 0))
        else:
            if len(vlKeys) == 3:
                constraints.append(TernaryConstraint( variables[vlKeys[0]], variables[vlKeys[1]], variables[vlKeys[2]],
                                    lambda x,y,z,xv=varLetters[vlKeys[0]],yv=varLetters[vlKeys[1]],zv=varLetters[vlKeys[2]]:
                                                  (x*xv + y*yv + z*zv)%10 == 0 or
                                                  (x*xv + y*yv + z*zv)%10 == -(len(words)-2) or
                                                  (x*xv + y*yv + z*zv)%10 == 10-(len(words)-2)))
                constraints.append(TernaryConstraint( variables[vlKeys[2]], variables[vlKeys[1]], variables[vlKeys[0]],
                                    lambda x,y,z,xv=varLetters[vlKeys[2]],yv=varLetters[vlKeys[1]],zv=varLetters[vlKeys[0]]:
                                                  (x*xv + y*yv + z*zv)%10 == 0 or
                                                  (x*xv + y*yv + z*zv)%10 == -(len(words)-2) or
                                                  (x*xv + y*yv + z*zv)%10 == 10-(len(words)-2)))
                constraints.append(TernaryConstraint( variables[vlKeys[1]], variables[vlKeys[0]], variables[vlKeys[2]],
                                    lambda x,y,z,xv=varLetters[vlKeys[1]],yv=varLetters[vlKeys[0]],zv=varLetters[vlKeys[2]]:
                                                  (x*xv + y*yv + z*zv)%10 == 0 or
                                                  (x*xv + y*yv + z*zv)%10 == -(len(words)-2) or
                                                  (x*xv + y*yv + z*zv)%10 == 10-(len(words)-2)))
            elif len(vlKeys) == 2:
                constraints.append(BinaryConstraint( variables[vlKeys[0]], variables[vlKeys[1]],
                                    lambda x,y,xv=varLetters[vlKeys[0]],yv=varLetters[vlKeys[1]]:
                                                  (x*xv + y*yv)%10 == 0 or
                                                  (x*xv + y*yv)%10 == -(len(words)-2) or
                                                  (x*xv + y*yv)%10 == 10-(len(words)-2)))
                constraints.append(BinaryConstraint( variables[vlKeys[1]], variables[vlKeys[0]],
                                    lambda x,y,xv=varLetters[vlKeys[1]],yv=varLetters[vlKeys[0]]:
                                                  (x*xv + y*yv)%10 == 0 or
                                                  (x*xv + y*yv)%10 == -(len(words)-2) or
                                                  (x*xv + y*yv)%10 == 10-(len(words)-2)))
            elif len(vlKeys) == 1:
                constraints.append(UnaryConstraint( variables[vlKeys[0]],
                                    lambda x,xv=varLetters[vlKeys[0]]:
                                                  (x*xv)%10 == 0 or
                                                  (x*xv)%10 == -(len(words)-2) or
                                                  (x*xv)%10 == 10-(len(words)-2)))






def setUpKenKen( variables, constraints, size ):
    rows = []
    cols = []
    doma = []
    for c in ( chr( i ) for i in range( 65, 65 + size ) ):
        rows.append( c )

    for i in range( 1, size+1 ):
        cols.append( str( i ) )

    for i in range( 1, size+1 ):
        doma.append( i )

    varNames = [ x+y for x in rows for y in cols ]
    for var in varNames:
        variables[var] = ConstraintVar( doma, var )

    # varname is a 2 dimensional list used in setUpNeighbor function
    varname = []
    k = 0
    for i in range( 0, size ):
        new = []
        for j in range( 0, size ):
            new.append( varNames[ k ] )
            k = k + 1
        varname.append( new )


    setUpNeighbor( varname, variables, size )
    # establish the allDiff constraint for each column and each row
    # for AC3, all constraints would be added to the queue

    # for example, for rows A,B,C, generate constraints A1!=A2!=A3, B1!=B2...
    for r in rows:
        aRow = []
        for k in variables.keys():
            if ( str(k).startswith(r) ):
        #accumulate all ConstraintVars contained in row 'r'
                aRow.append( variables[k] )
    #add the allDiff constraints among those row elements
        allDiff( constraints, aRow )

    # for example, for cols 1,2,3 (with keys A1,B1,C1 ...) generate A1!=B1!=C1, A2!=B2 ...
    for c in cols:
        aCol = []
        for k in variables.keys():
            key = str(k)
            # the column is indicated in the 2nd character of the key string
            if ( key[1] == c ):
        # accumulate all ConstraintVars contained in column 'c'
                aCol.append( variables[k] )
        allDiff( constraints, aCol )


def setUpNeighbor( varname, variables, size ):
    # Add other elements in one element's row to its neighbor
    for i in range( 0, size ):
        for j in range( 0, size ):
            for k in range( 0, size ):
                if k != j:
                    variables[ varname[ i ][ j ] ].neighbors.append( variables[ varname[ i ][ k ] ] )

    # Add other elements in one element's column to its neighbor
    for j in range( 0, size ):
        for i in range( 0, size ):
            for k in range( 0, size ):
                if k != i:
                    variables[ varname[ i ][ j ] ].neighbors.append( variables[ varname[ k ][ j ] ])

def Revise( cv ):
    revised = False
    domain_list = []
    if ( type( cv ) == TernaryConstraint ):

        if not ( cv.var2 in cv.var1.neighbors ):
            cv.var1.neighbors.append( cv.var2 )
        if not ( cv.var3 in cv.var1.neighbors ):
            cv.var1.neighbors.append( cv.var3 )
        if not ( cv.var1 in cv.var2.neighbors ):
            cv.var1.neighbors.append( cv.var1 )
        if not ( cv.var3 in cv.var2.neighbors ):
            cv.var1.neighbors.append( cv.var3 )
        if not ( cv.var1 in cv.var3.neighbors ):
            cv.var1.neighbors.append( cv.var1 )
        if not ( cv.var2 in cv.var3.neighbors ):
            cv.var1.neighbors.append( cv.var2 )

        dom1 = list( cv.var1.domain )
        dom2 = list( cv.var2.domain )
        dom3 = list( cv.var3.domain )
        # for each value in the domain of variable 1
        for x in dom1:
            check = 0
            # for each value in the domain of variable 2
            for y in dom2:
                # for each value in the domain of variable 3
                for z in dom3:
                # if nothing in domain of variable2 satisfies the constraint when variable1==x, remove x
                    if ( cv.func( x, y, z ) == False ):
                        check += 1
                    if ( check == len( dom2 ) * len( dom3 ) ):
                        cv.var1.domain.remove( x )
                        revised = True

    elif ( type( cv ) == BinaryConstraint ):
        if not ( cv.var2 in cv.var1.neighbors ):
            cv.var1.neighbors.append( cv.var2 )
        if not ( cv.var1 in cv.var2.neighbors ):
            cv.var1.neighbors.append( cv.var1 )

        dom1 = list( cv.var1.domain )
        dom2 = list( cv.var2.domain )
        # for each value in the domain of variable 1
        for x in dom1:
            check = 0
            # for each value in the domain of variable 2
            for y in dom2:
            # if nothing in domain of variable2 satisfies the constraint when variable1==x, remove x
               if ( cv.func( x, y ) == False):
                   check += 1
               if ( check == len( dom2 ) ):
                   cv.var1.domain.remove( x )
                   revised = True

    elif ( type( cv ) == UnaryConstraint ):
        dom = list( cv.var.domain )
        # for each value in the domain of variable
        for x in dom:
            if ( cv.func( x ) == False ):
                cv.var.domain.remove( x )
                revised = True

    return revised

def nodeConsistent( uc ):
    domain = list(uc.var.domain)
    for x in domain:
        if ( False == uc.func(x) ):
            uc.var.domain.remove(x)

def printDomains( vars, n=3 ):
    count = 0
    for k in sorted(vars.keys()):
        print( k,'{',vars[k].domain,'}, ',end="" )
        count = count+1
        if ( 0 == count % n ):
            print(' ')

def transferConstraint( cons, constraints, variables ):
    for c in cons:
        num_var = c.nvars
        if num_var == 1:
            uc = UnaryConstraint( variables[ c.vlist[ 0 ] ], c.fn )
            constraints.append( uc )
        elif num_var == 2:
            bc = BinaryConstraint( variables[ c.vlist[ 0 ] ], variables[ c.vlist[ 1 ] ], c.fn )
            constraints.append( bc )
        elif num_var == 3:
            tc = TernaryConstraint( variables[ c.vlist[ 0 ] ], variables[ c.vlist[ 1 ] ], variables[ c.vlist[ 2 ] ], c.fn )
            constraints.append( tc )

def AC3():
    # create a dictionary of ConstraintVars keyed by names in VarNames.
    variables = dict()
    constraints = []
    cons = []
    op, words, letters = readCrypt()

    setUpCrypt(variables, cons, words, letters, op)
    print("initial domains")
    printDomains( variables )

    #transferConstraint( cons, constraints, variables )
    que = queue.LifoQueue()

    # Initialize the queue by putting all the constraint variables in the queue
    for c in cons:
        que.put(c)

    while not( que.empty() ):
        constr = que.get()
        if Revise( constr ):
            que.put(constr)

    print("\n Final Domains")
    printDomains( variables )




AC3()






