import copy
import argparse
import itertools
import re 

class wire:
    def __init__(self, name, type, operands, logic_value, logic_level, prob0, prob1, absprob,
                 fanout, mainout, tag, index):
        self.name = name
        self.type = type
        self.operands = operands
        self.logic_value = logic_value
        self.logic_level = logic_level
        self.prob0 = prob0
        self.prob1 = prob1
        self.absprob = absprob
        self.fanout = fanout
        self.mainout = mainout
        self.tag = tag
        self.index = index


def simple_read_bench(benchmark_address):
    wires = []
    temp = []
    bench_file = open(benchmark_address)
    index = 1

    for line in bench_file:
        if "#" in line:
            continue
        elif "INPUT" in line:
            wires.append(wire(line[line.find("(") + 1:line.find(")")], "inp", [], "1", 0, 0, 0, 0, 0, 0, 0, index))
        elif "OUTPUT" in line:
            wires.append(wire(line[line.find("(") + 1:line.find(")")], "out", [], "1", 0, 0, 0, 0, 0, 0, 0, index))
        elif " = " in line:
            gate_out = line[0: line.find(" =")]
            gate_type = line[line.find("= ") + 2: line.find("(")].lower()
            gate_list_inputs = line[line.find("(") + 1:line.find(")")]
            gate_oprs = gate_list_inputs.split(",")
            gate_oprs = [x.strip(' ') for x in gate_oprs]
            for i in range(0, len(gate_oprs)):
                found = False
                for j in range(0, len(wires)):
                    if wires[j].name == gate_oprs[i]:
                        found = True
                        temp.append(wires[j])
                        break
                if not found:
                    # print gate_out, gate_oprs[i]
                    temp.append(wire(gate_oprs[i], "dummy", [], "1", 0, 0, 0, 0, 0, 0, 0, 0))
            wires.append(wire(gate_out, gate_type, temp, "1", 0, 0, 0, 0, 0, 0, 0, index))
        else:
            continue

        temp = []
        index += 1

    bench_file.close()

    for i in range(0, len(wires)):
        for j in range(0, len(wires[i].operands)):
            if wires[i].operands[j].type == "dummy":
                found = False
                for k in range(0, len(wires)):
                    if wires[k].name == wires[i].operands[j].name:
                        found = True
                        wires[i].operands[j] = wires[k]
                        break
                if not found:
                    print(wires[i].operands[j].name)
                    print("ERROR1 in read_circuit()")
                    exit()

    # just to be sure!
    for i in range(len(wires)):
        if wires[i].name != wires[wires[i].index-1].name:
            print(wires[i].name)
            print("ERROR2 in read_circuit()")
            exit()

    return wires

######################### IO section ###############################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ISCAS-85 bench to CNF Converter.')
    parser.add_argument("-b", action="store", required=True, type=str, help="benchmark path")
    parser.add_argument("-c", action="store", required=True, type=str, help="cnf path")

    args = parser.parse_args()

    bench_address = args.b
    cnf_address = args.c 
    
    wires = simple_read_bench(bench_address)    
    cnf_variable_counts = len(wires)

cnf_addr_origin = bench_address.replace(".bench", '.cnf')

bench_addr_new = ""
for out in cnf_address[:-4]:
    bench_addr_new += out
bench_addr_new += "_bench.bench"
######################################################################

# Open new benchmark file:
bench_file = open(bench_addr_new, 'w')

# Reading from original benchmark file:
with open(bench_address, 'r') as f:
    lines = f.readlines()    
# Writing INPUT and OUTPUT from original to new file:
#for line in lines:
#    if line.strip().split(" ")[0] != "#":
#        bench_file.write(line)




indx = []
var_type = []
var_list = []
inpt = []
outpt = [] 
gate = []
operand = [] 
op_index = 0  

for i in range(0, len(wires)):
    indx.append(vars(wires[i]).get('index'))
    var_type.append(vars(wires[i]).get('type'))
    var_list.append(vars(wires[i]).get('name'))
    if var_type[i] == 'out' :
        output_pin = var_list[i]
    if var_type[i] == 'inp' :
        keyin_last = var_list[i]



# Writing INPUT and OUTPUT from original to new file:
        
for line in lines:
    if line.strip().split(" ")[0] != "#" :
        if line.strip().split(" ")[0] == output_pin:
            final_out = line
        else:
            bench_file.write(line)
   
a = final_out.strip().split(" ")[0]
b = re.findall('\d+', a)
c = int(b[0])+1
out_dummy = f"G{c}gat"
output_final = final_out.replace(a, out_dummy)

bench_file.write(output_final)
#####################################################            

inputs = 0 
outputs = 0
inverters = 0
for gate_type in var_type:
    if gate_type == 'inp':
        inputs += 1
    if gate_type == 'out':
        outputs += 1
    if gate_type == 'not':
        inverters += 1

cnf_file = open(cnf_address)
index = 1
        
#################### Reading New CNF file ###################### 

def parse_cnf_file(cnf_address):       
    with open(cnf_address, 'r') as f:
        lines = f.readlines()
    i = 0
    while lines[i].strip().split(" ")[0] == "c":
        i += 1
    header = lines[i].strip().split(" ")
    assert(header[0] == "p")
    iclauses = [[int(s) for s in line.strip().split(" ")[:-1]] for line in lines[i+1:]]
    return iclauses

iclauses = parse_cnf_file(cnf_address)

iclauses_old = parse_cnf_file(cnf_addr_origin)
#print(clause_index)
###########          Remove Duplicate #################################
clause_final = []
for word in iclauses:
    if word not in clause_final:
        clause_final.append(word)

#######################################################################

org_len = len(iclauses_old)-1

# Get Last Variable from the original CNF file:

def last_var_num(var_list):
    new_var_list = []
    for i in var_list:
        new_var_indx = re.findall('\d+', i)
        # removing [] from the response list: 
        new_var_indx = ", ".join(new_var_indx)
        # appending to a list
        new_var_list.append(new_var_indx)

    # removing empty string from list:
    while("" in new_var_list) : 
        new_var_list.remove("")
    
    # str to int: 
    new_var_list = list(map(int, new_var_list))
    
    #getting max term:
    last_var = max(new_var_list)
    
    return last_var


last_var = last_var_num(var_list)
add_var_list = []

for clause in iclauses:
    if iclauses.index(clause) <= org_len:

        continue # Escape
        gate_in = []
        if len(clause) > 2:
    #        print (clause)
            for lit in range(len(clause)):
                if lit == 0:
                    loop_index = abs(clause[lit])-1
                    gate_name = var_type[loop_index]
                    gate_out = var_list[loop_index]
                else:
                    loop_index = abs(clause[lit])-1
                    gate_in.append(int(var_list[loop_index]))
#            print(f"{gate_out} = {gate_name.upper()}{tuple(gate_in)}")
            old_1 = f"{gate_out} = {gate_name.upper()}{tuple(gate_in)}\n"
            bench_file.write(old_1)
        else:
            loop_index = abs(clause[0])-1
            gate_name = var_type[loop_index]
            gate_out = var_list[loop_index]
            if gate_name == 'not' or gate_name == 'buf' :
                loop_index = abs(clause[1])-1
                gate_in = (int(var_list[loop_index]))
#                print(f"{gate_out} = {gate_name.upper()}({gate_in})")
                old_2 = f"{gate_out} = {gate_name.upper()}({gate_in})\n"
    else:
        gate_out = []
#        last_var += 1;
        for lit in range(len(clause)):
            loop_index = clause[lit]-1
            if loop_index < 0:
                last_var += 1;
                loop_index = abs(clause[lit])-1
                gate_out_temp = var_list[loop_index]
                gate_out.append(f"G{last_var}gat")
#                print(f"G{last_var}gat = NOT({gate_out_temp})")
                new_1 = f"G{last_var}gat = NOT({gate_out_temp})\n"
                bench_file.write(new_1)
            else:
#                loop_index = abs(clause[lit])-1
#                gate_out.append(int(var_list[loop_index]))
                gate_out.append(var_list[loop_index])
#            gate_out.append(int(var_list[loop_index]))          
        # Conversion from List to tuple and remove ''
        gate_out = '(%s)' % ', '.join(map(str, gate_out))
        last_var += 1;
        add_var_list.append(f"G{last_var}gat")
#        print(f"G{last_var}gat = OR{gate_out}")
        new_2 = f"G{last_var}gat = OR{gate_out}\n"
        bench_file.write(new_2)

#  gate_out = '[%s]' % ', '.join(map(str, gate_out))

def break_and_list(add_var_list, last_var):
    out_AND_list = []
    and_final = [add_var_list[x:x+10] for x in range(0, len(add_var_list), 10)]
    for i in and_final:
       last_var += 1
       i_new = '(%s)' % ', '.join(map(str, i))
#       print (f"G{last_var}gat = AND{i_new}")
       and_write = (f"G{last_var}gat = AND{i_new}\n")
       bench_file.write(and_write)
       out_AND_list.append(f"G{last_var}gat")
    return out_AND_list, last_var

out_AND_list, last_var = break_and_list(add_var_list, last_var)

final_break, last_var = break_and_list(out_AND_list, last_var)

#last_var += 1;
#print(f"G{last_var}gat = AND({final_break[-1]}, {output_pin})") 
#and_out = f"G{last_var}gat = AND({final_break[-1]}, {output_pin})\n"
#bench_file.write(and_out)


keyin_final = int(re.findall('\d+', keyin_last)[0])+1


out_write = f"{output_pin} = XOR(G{last_var}gat$enc, {out_dummy})\n"
bench_file.write(out_write)
keyin_declare = f"INPUT(keyinput{keyin_final})\n"
bench_file.write(keyin_declare)
key_write = f"G{last_var}gat$enc = AND(G{last_var}gat, keyinput{keyin_final})\n"
bench_file.write(key_write)
print("CNF to Bench Conversion Done")
bench_file.close()       