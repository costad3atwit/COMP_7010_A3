#imports
import math
from fractions import Fraction
import scipy
from scipy.optimize import linprog



### PART A ###

def simplex(c, A, b, rule="bland"):
    if any(value < 0 for value in b):
        return ("infeasible", None, None, 0)
    #rewrite inequalities using equals signs and input slack vars
    # maximize    30·x1 + 20·x2          ← c = [30, 20]
    # subject to  1·x1 +  1·x2 ≤ 4      ← A[0] = [1,1],  b[0] = 4
    #             1·x1 +  3·x2 ≤ 9      ← A[1] = [1,3],  b[1] = 9
    #             1·x1 +  0·x2 ≤ 3      ← A[2] = [1,0],  b[2] = 3
    #             x1, xz2 ≥ 0
    n = len(c)
    m = len(A)
    tab = [[Fraction(0)] * (n + m + 1) for _ in range(m + 1)] #set tableau size
    #set cols 0->n-1
    for i in range(m):
        for j in range(n):
            tab[i][j] = Fraction(A[i][j])
    #set cols n->n+m-1 (slacks)
    for i in range(m):
        tab[i][n + i] = Fraction(1)
    #set RHS
    for i in range(m):
        tab[i][n + m] = Fraction(b[i])
    #set profit row
    for j in range(n):
        tab[m][j] = Fraction(-c[j])
    #set basis variables (starts as slacks)
    basis = [n + i for i in range(m)]
    pivots = 0
#if rule="dantzig"
    #for each simplex iteration (while neighbor vertices are better)
        #take min of row m from col 0 to n+m-1,
        # if min < 0, choose pivot column j by min's column
            # if there are no positive entries in the pivot column, the problem is unbounded: return unbounded
            # for each row 0<i<m-1, if tab[i][j] > 0, compute ratio tab[i][n+m]/tab[i][j]
            # select pivot element tab[i][j] where ratio of above is minimum
            # update tableau for row of pivot element by dividing all elements in that row by the pivot
            # update all other rows by subtracting their pivot-column coefficient times the pivot row (to zero out the pivot column)
            #basis[pivot_row] = pivot_col
            #pivots = pivots + 1
        # else end
# elif rule="bland"
    #for each simplex iteration (while neighbor vertices are better)
        #take first negative entry in row m from col 0 to n+m-1,
        # if neg found, choose pivot column j by neg's column
            # if there are no positive entries in the pivot column, the problem is unbounded: return unbounded
            # for each row 0<i<m-1, if tab[i][j] > 0, compute ratio tab[i][n+m]/tab[i][j]
            #if two rows tie on the ratio, choose the row with the smallest basis variable index basis[i]
            # select pivot element tab[i][j] where ratio of above is minimum
            # update tableau for row of pivot element by dividing all elements in that row by the pivot
            # update all other rows by subtracting their pivot-column coefficient times the pivot row (to zero out the pivot column)
            #basis[pivot_row] = pivot_col
            #pivots = pivots + 1
        # else end
# else exception unknown rule    
        
    #basis variables are the vars that have a 1 in one of their rows and a 0 in all other rows. The basic vars are set to the RHS values, while the nonbasic vars are set to 0.
    z = tab[m][n + m]
    y = tab[m][n:n + m]
    x = [Fraction(0)] * n
    for i in range(m):
        if basis[i] < n:
            x[basis[i]] = tab[i][n + m]
    status = "optimal"
    return (status,x,z,y,pivots)

def test_simplex():
    #bakery
    c = [30,20]
    A = [[1,1],[1,3],[1,0]]
    b = [4,9,3]
    exp_z = 110
    exp_x = (3,1)
    exp_y = (20,0,10)
    #print shop
    c = [5,4]
    A = [[6,4],[1,2]]
    b = [24,6]
    exp_z = 21
    exp_x = (3,Fraction(3,2))
    exp_y = (Fraction(3,4),Fraction(1,2))
    #example B
    c = [3,5]
    A = [[1,0],[0,2],[3,2]]
    b = [4,12,18]
    exp_z = 36
    exp_x = (2,6)
    exp_y = None  # not given in the assignment
    #degenerate
    c = [30,20]
    A = [[1,1],[1,3],[1,0]]
    b = [4,6,3]
    exp_z = 110
    exp_x = None  # not given in the assignment (ratio-test tie)
    exp_y = None  # not given in the assignment
    #unbounded
    c = [1,1]
    A = [[1,-1]]
    b = [1]
    exp_status = "unbounded"
    exp_z = None
    exp_x = None
    exp_y = None
    pass

def check_certificate(c, A, b, x, y):
    return False



### PART B ###

