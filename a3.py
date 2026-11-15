#imports
from fractions import Fraction
import random
from scipy.optimize import linprog
random.seed(1234)


### PART A ###

def simplex(c, A, b, rule="bland"):
    if any(value < 0 for value in b):
        raise ValueError("all values of b must be non-negative")
    #rewrite inequalities using equals signs and input slack vars
    # maximize    30·x1 + 20·x2          ← c = [30, 20]
    # subject to  1·x1 +  1·x2 ≤ 4      ← A[0] = [1,1],  b[0] = 4
    #             1·x1 +  3·x2 ≤ 9      ← A[1] = [1,3],  b[1] = 9
    #             1·x1 +  0·x2 ≤ 3      ← A[2] = [1,0],  b[2] = 3
    #             x1, xz2 ≥ 0
    n = len(c)
    m = len(A)
    rhs_col=n+m
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
    #for each simplex iteration (while there is a negative in the profit row)
        #take min of row m from col 0 to n+m-1,
        # if min < 0, choose pivot column j by min's column
            # if there are no positive entries in the pivot column, the problem is unbounded: return unbounded
            # for each row 0<=i<=m-1, if tab[i][j] > 0, compute ratio tab[i][n+m]/tab[i][j]
            # select pivot element tab[i][j] where ratio of above is minimum
            # update tableau for row of pivot element by dividing all elements in that row by the pivot
            # update all other rows by subtracting their pivot-column coefficient times the pivot row (to zero out the pivot column)
            #basis[pivot_row] = pivot_col
            #pivots = pivots + 1
        # else end
    if rule=="dantzig":
        while min(tab[m][0:rhs_col])<0:
            # choose pivot column by the most negative ele in the profit row
            piv_col=min(range(rhs_col),key=lambda col:tab[m][col])
            if all(tab[row][piv_col]<=0 for row in range(m)): return ("unbounded",None,None,None,pivots) #pivot column must have a positive ele or the problem is unbounded
            # use the min ratio test (piv_col_ele/rhs_ele) to pick the pivot row
            piv_row=None
            min_ratio=None
            for row in range(m):
                if tab[row][piv_col]>0:
                    ratio=tab[row][rhs_col]/tab[row][piv_col]
                    if min_ratio is None or ratio<min_ratio:
                        min_ratio=ratio
                        piv_row=row
            # normalize pivot row by dividing by the pivot element
            piv_ele=tab[piv_row][piv_col]
            tab[piv_row]=[ele/piv_ele for ele in tab[piv_row]]
            # subtract a multiple of the pivot row from every other row to zero out the pivot column
            for row in range(m+1):
                if row==piv_row: continue
                multiple=tab[row][piv_col]
                tab[row]=[ele-multiple*piv_row_ele for ele,piv_row_ele in zip(tab[row],tab[piv_row])]
            basis[piv_row]=piv_col
            pivots+=1
# elif rule="bland"
    #for each simplex iteration (while neighbor vertices are better)
        #take first negative entry in row m from col 0 to n+m-1,
        # if neg found, choose pivot column j by neg's column
            # if there are no positive entries in the pivot column, the problem is unbounded: return unbounded
            # for each row 0<=i<=m-1, if tab[i][j] > 0, compute ratio tab[i][n+m]/tab[i][j]
            #if two rows tie on the ratio, choose the row with the smallest basis variable index basis[i]
            # select pivot element tab[i][j] where ratio of above is minimum
            # update tableau for row of pivot element by dividing all elements in that row by the pivot
            # update all other rows by subtracting their pivot-column coefficient times the pivot row (to zero out the pivot column)
            #basis[pivot_row] = pivot_col
            #pivots = pivots + 1
        # else end
    elif rule=="bland":
        while min(tab[m][0:rhs_col])<0:
            # choose pivot column by the first negative ele in the profit row
            piv_col = None
            for col in range(rhs_col):
                if tab[m][col] < 0:
                    piv_col = col
                    break
            if all(tab[row][piv_col]<=0 for row in range(m)): return ("unbounded",None,None,None,pivots) #pivot column must have a positive ele or the problem is unbounded
            # use the min ratio test (piv_col_ele/rhs_ele) to pick the pivot row
            piv_row=None
            min_ratio=None
            for row in range(m):
                if tab[row][piv_col]>0:
                    ratio=tab[row][rhs_col]/tab[row][piv_col]
                    if min_ratio is None or ratio<=min_ratio:
                        if(ratio == min_ratio):
                            if basis[row] < basis[piv_row]: piv_row = row
                        else:
                            min_ratio=ratio
                            piv_row=row
            # normalize pivot row by dividing by the pivot element
            piv_ele=tab[piv_row][piv_col]
            tab[piv_row]=[ele/piv_ele for ele in tab[piv_row]]
            # subtract a multiple of the pivot row from every other row to zero out the pivot column
            for row in range(m+1):
                if row==piv_row: continue
                multiple=tab[row][piv_col]
                tab[row]=[ele-multiple*piv_row_ele for ele,piv_row_ele in zip(tab[row],tab[piv_row])]
            basis[piv_row]=piv_col
            pivots+=1
    else:
        raise ValueError("Unknown Rule")   

    x=[Fraction(0)]*n
    for row in range(m):
        if basis[row]<n: x[basis[row]]=tab[row][rhs_col]
    # optimal sol'n value
    z=tab[m][rhs_col]
    # the dual values are the profit row entries under the slack columns
    y=tab[m][n:n+m]
    return ("optimal",x,z,y,pivots)

def check_certificate(c, A, b, x, y):
    if x is None or y is None: return False
    num_constraints, num_vars = len(A), len(c)

    #primal feasible
    for var_index in range(num_vars):
        if x[var_index] < 0: return False
    for constraint_index in range(num_constraints):
        row_total = 0
        for var_index in range(num_vars):
            row_total += A[constraint_index][var_index] * x[var_index]
        if row_total > b[constraint_index]: return False

    #dual feasible
    for constraint_index in range(num_constraints):
        if y[constraint_index] < 0: return False
    for var_index in range(num_vars):
        column_total = 0
        for constraint_index in range(num_constraints):
            column_total += A[constraint_index][var_index] * y[constraint_index]
        if column_total < c[var_index]: return False

    #strong duality
    primal_obj = 0
    dual_obj = 0
    for var_index in range(num_vars):
        primal_obj += c[var_index]*x[var_index]
    for constraint_index in range(num_constraints):
            dual_obj += b[constraint_index]*y[constraint_index]
    if primal_obj != dual_obj: return False

    return True

def klee_minty(n):
    c = [2**(n-j) for j in range(1, n+1)]
    A = []
    for i in range(1, n+1):
        row = []
        for j in range(1, n+1):
            if j < i:   row.append(2 * 2**(i-j))
            elif j == i: row.append(1)
            else:        row.append(0)
        A.append(row)
    b = [5**i for i in range(1, n+1)]
    return c, A, b

def test_simplex():
    #A1 5 TESTS
    print("")
    rules = ["bland","dantzig"]
    #bakery
    c = [30,20]
    A = [[1,1],[1,3],[1,0]]
    b = [4,9,3]
    exp_z = 110
    exp_x = (3,1)
    exp_y = (20,0,10)
    print("\nBakery Results")
    for rule in rules:
        res = simplex(c,A,b,rule)
        cert_res = check_certificate(c,A,b,res[1],res[3])
        assert cert_res
        assert (res[0],tuple(res[1]),res[2],tuple(res[3])) == ("optimal",exp_x,exp_z,exp_y)
        print(f"({rule}): \nStatus:{res[0]} | Expected: {"optimal"} \nZ:{res[2]} | Expected: {exp_z}\nX:{res[1]} | Expected: {exp_x}\nY:{res[3]} | Expected: {exp_y}\nPivots:{res[4]}\nCertificate Check: {cert_res}")
        print(f"X: ({', '.join(str(val) for val in res[1])})") #handle fractions
        print(f"Y: ({', '.join(str(val) for val in res[3])})\n") #handle fractions

    #print shop
    c = [5,4]
    A = [[6,4],[1,2]]
    b = [24,6]
    exp_z = 21
    exp_x = (3,Fraction(3,2))
    exp_y = (Fraction(3,4),Fraction(1,2))
    print("\nPrint Shop Results")
    for rule in rules:
        res = simplex(c,A,b,rule)
        cert_res = check_certificate(c,A,b,res[1],res[3])
        assert cert_res
        assert (res[0],tuple(res[1]),res[2],tuple(res[3])) == ("optimal",exp_x,exp_z,exp_y)
        print(f"({rule}): \nStatus:{res[0]} | Expected: {"optimal"} \nZ:{res[2]} | Expected: {exp_z}\nX:{res[1]} | Expected: {exp_x}\nY:{res[3]} | Expected: {exp_y}\nPivots:{res[4]}\nCertificate Check: {cert_res}")
        print(f"X: ({', '.join(str(val) for val in res[1])})") #handle fractions
        print(f"Y: ({', '.join(str(val) for val in res[3])})\n") #handle fractions
    
    #example B
    c = [3,5]
    A = [[1,0],[0,2],[3,2]]
    b = [4,12,18]
    exp_z = 36
    exp_x = (2,6)
    exp_y = None  # not given in the assignment
    print("\nExample B Results")
    for rule in rules:
        res = simplex(c,A,b,rule)
        cert_res = check_certificate(c,A,b,res[1],res[3])
        assert cert_res
        assert (res[0],tuple(res[1]),res[2]) == ("optimal",exp_x,exp_z)
        print(f"Example B Result ({rule}): \nStatus:{res[0]} | Expected: {"optimal"} \nZ:{res[2]} | Expected: {exp_z}\nX:{res[1]} | Expected: {exp_x}\nY:{res[3]} | Expected: {exp_y}\nPivots:{res[4]}\nCertificate Check: {cert_res}")
        print(f"X: ({', '.join(str(val) for val in res[1])})") #handle fractions
        print(f"Y: ({', '.join(str(val) for val in res[3])})\n") #handle fractions

    #degenerate
    c = [30,20]
    A = [[1,1],[1,3],[1,0]]
    b = [4,6,3]
    exp_z = 110
    exp_x = None  # not given in the assignment (ratio-test tie)
    exp_y = None  # not given in the assignment
    print("\nDegenerate Case Results")
    for rule in rules:
        res = simplex(c,A,b,rule)
        cert_res = check_certificate(c,A,b,res[1],res[3])
        assert cert_res
        assert (res[0],res[2]) == ("optimal",exp_z)
        print(f"({rule}): \nStatus:{res[0]} | Expected: {"optimal"} \nZ:{res[2]} | Expected: {exp_z}\nX:{res[1]} | Expected: {exp_x}\nY:{res[3]} | Expected: {exp_y}\nPivots:{res[4]}\nCertificate Check: {cert_res}")
        print(f"X: ({', '.join(str(val) for val in res[1])})") #handle fractions
        print(f"Y: ({', '.join(str(val) for val in res[3])})\n") #handle fractions

    #unbounded
    c = [1,1]
    A = [[1,-1]]
    b = [1]
    exp_status = "unbounded"
    exp_z = None
    exp_x = None
    exp_y = None
    print("\nUnbounded Results")
    for rule in rules:
        res = simplex(c,A,b,rule)
        assert (res[0]) == ("unbounded")
        print(f"({rule}): \nStatus:{res[0]} | Expected: {"unbounded"} \nZ:{res[2]} | Expected: {exp_z}\nX:{res[1]} | Expected: {exp_x}\nY:{res[3]} | Expected: {exp_y}\nPivots:{res[4]}\n")

    successes = 0
    for _ in range(20):
        passes = True
        n = random.randint(2, 6)
        m = random.randint(2, 6)
        A = [[random.randint(1, 9) for _ in range(n)] for _ in range(m)]
        b = [random.randint(10, 50) for _ in range(m)]
        c = [random.randint(1, 20) for _ in range(n)]
        neg_c = [-ele for ele in c]
        ref = linprog(neg_c, A, b) #pass -c and use -ref.fun (z) later because linprog minimizes
        res_dat= simplex(c, A, b, rule="dantzig")
        res_bland = simplex(c, A, b, rule="bland")
        if ref.status == 0: # 0 means optimal
            if res_dat[0] != "optimal": passes = False
            if res_bland[0] != "optimal": passes = False
            if res_dat[2] != res_bland[2]: passes = False
            if abs(float(res_dat[2]) - (-ref.fun)) >  1e-9 : passes = False #ensure z is ~equal among all results
            if abs(float(res_bland[2]) - (-ref.fun)) >  1e-9: passes = False #ensure z is ~equal among all results
            if not check_certificate(c, A, b, res_dat[1], res_dat[3]): passes = False
            if not check_certificate(c, A, b, res_bland[1], res_bland[3]): passes = False
        else:
            if res_dat[0] != "unbounded": passes = False
            if res_bland[0] != "unbounded": passes = False
            if ref.status != 3: passes = False         
        if passes: successes += 1
    print(f"{successes} random tests passed for a success rate of: {100*successes/20}%\n")
    assert successes == 20
    

### PART B ###

## B1. ##

def test_b1():
    print("\nTEST B1")
    A=[[3,1,2],[4,3,4],[1,4,2]] #constraints
    c=[5,8,6] #profit
    b=[24,48,20] #rhs
    status,x,z,y,pivots = simplex(c,A,b)
    print(f"status: {status}\nx: ({', '.join(str(val) for val in x)})\ny: ({', '.join(str(val) for val in y)})\nz: {z}\npivots: {pivots}")
    # B1.5: verify strong duality with cert
    primal_obj = sum(c[j]*x[j] for j in range(len(c)))
    dual_obj = sum(b[i]*y[i] for i in range(len(b)))
    cert = check_certificate(c, A, b, x, y)
    print(f"primal objective: {primal_obj}\ndual objective: {dual_obj}\ncertificate check: {cert}")
    assert cert and primal_obj == dual_obj == 64



def test_b2():
    print("\nTEST B2")
    c, A, b = klee_minty(3)
    assert (c, A, b) == ([4, 2, 1], [[1, 0, 0], [4, 1, 0], [8, 4, 1]], [5, 25, 125])
    results = []
    for n in range(2, 9):
        c, A, b = klee_minty(n)
        dan = simplex(c, A, b, rule="dantzig")
        bla = simplex(c, A, b, rule="bland")
        assert dan[2] == bla[2] == 5**n
        assert dan[4] == 2**n - 1
        results.append((n, dan[4], bla[4], dan[2]))

    print(f"{'n':>2} | {'Dantzig':>7} | {'Bland':>5} | {'z*':>7}")
    for n, pd, pb, z in results:
        print(f"{n:>2} | {pd:>7} | {pb:>5} | {z:>7}")

    print("\nn,Dantzig,Bland")
    for n, pd, pb, z in results:
        print(f"{n},{pd},{pb}")