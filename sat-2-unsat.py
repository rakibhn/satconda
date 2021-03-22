import math
import numpy as np
import random
import argparse
import PyMiniSolvers.minisolvers as minisolvers


def parse_dimacs(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    i = 0
    while lines[i].strip().split(" ")[0] == "c":
        i += 1
    header = lines[i].strip().split(" ")
    assert(header[0] == "p")
    n_vars = int(header[2])
    iclauses = [[int(s) for s in line.strip().split(" ")[:-1]] for line in lines[i+1:]]
    iclauses_old = len(iclauses)
    return n_vars, iclauses, iclauses_old




#n_vars, iclauses = parse_dimacs("/home/hduser/OneDrive/satconda/dimacs/sat_2_unsat.dimacs")

def generate_k_iclause(n,k):
    vs = np.random.choice(n, size=min(n, k), replace=False)
#    vs = np.random.choice(n, size=n, replace=False)
    return [v + 1 if random.random() < 0.5 else -(v + 1) for v in vs]

#def gen_iclause_pair(n, iclauses, p_k_2, p_geo):
def gen_iclause_pair(n, iclauses, p_k_2, p_geo):
#    min_n = 10
#    max_n = min_n
#    n = random.randint(min_n, max_n)
#    n = n_vars

    solver = minisolvers.MinisatSolver()
    for i in range(n): 
        solver.new_var(dvar=True)

    for iclause in iclauses:
        solver.add_clause(iclause)
        
    is_sat = solver.solve()

    if is_sat:
        print("Converting SAT to unSAT")
        while True:
	        k_base = 1 if random.random() < p_k_2 else 2
	        k = k_base + np.random.geometric(p_geo) 
	        iclause = generate_k_iclause(n, k)
	        solver.add_clause(iclause)
	        is_sat = solver.solve()
	        if is_sat:
	            iclauses.append(iclause)
	        else:
                 print("Conversion Done")
                 break
        iclause_unsat = iclause
        iclauses.append(iclause_unsat)
    return n, iclauses, p_k_2, p_geo

def write_dimacs_to(n_vars, iclauses, out_filename):
    with open(out_filename, 'w') as f:
        f.write("p cnf %d %d\n" % (n_vars, len(iclauses)))
        for c in iclauses:
            for x in c:
                f.write("%d " % x)
            f.write("0\n")
     
#benchmark = ['c17', 'c432', 'c499', 'c880', 'c1355', 'c1908', 'c2670', 'c3540', 'c5315']
#p_k2 = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3]
#p_geo_2 = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ISCAS-85 SAT to unSAT Converter.')
    parser.add_argument("-c", action="store", required=True, type=str, help="cnf path")
    parser.add_argument("-pk2", action="store", required=True, type=float, help="pk_2")
    parser.add_argument("-pgeo", action="store", required=True, type=float, help="p_geo")
    args = parser.parse_args()

    input_cnf = args.c
    p_k_2 = args.pk2
    p_geo =  args.pgeo
    
#input_cnf = '/home/hduser/host15-logic-decryption/benchmarks/dac12/c880_enc05.cnf'
output_cnf = ""
for out in input_cnf[:-4]:
    output_cnf += out
n_vars, iclauses, iclauses_old = parse_dimacs(f"{input_cnf}")

n_vars, iclauses, p_k_2, p_geo = gen_iclause_pair(n_vars, iclauses, p_k_2, p_geo)

iclauses_new = len(iclauses)        
#out_filenames = f"{output_cnf}_unsat_{iclauses_old}_to_{iclauses_new}_p_k_2_{p_k_2}_geo_{p_geo}.cnf"        
out_filenames = f"{output_cnf}_unsat.cnf"     

write_dimacs_to(n_vars, iclauses, out_filenames)

#
#for cnf in benchmark:
#    for p_k_2 in p_k2:
#        for p_geo in p_geo_2:
#            for loop in range(10):
#                input_cnf = f'/home/hduser/OneDrive/satconda/dimacs/{cnf}.cnf'
#                output_cnf = ""
#                for out in input_cnf[:-4]:
#                    output_cnf += out
#                n_vars, iclauses, iclauses_old = parse_dimacs(f"{input_cnf}")
#                
#                n_vars, iclauses, p_k_2, p_geo = gen_iclause_pair(n_vars, iclauses, p_k_2, p_geo)
#            
#                iclauses_new = len(iclauses)        
#                out_filenames = f"{output_cnf}_unsat_{iclauses_old}_to_{iclauses_new}_p_k_2_{p_k_2}_geo_{p_geo}.cnf"        
#                    
#                write_dimacs_to(n_vars, iclauses, out_filenames)
