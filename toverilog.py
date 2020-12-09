def rewrite(word):
    word = word.replace('x_x', '/')
    word = word.replace('s_s', '\\')
    word = word.replace('b_b', '[')
    word = word.replace('c_c', ']')
    word = word.replace('__[', '  [')
    word = word.replace('_[', ' [')
    return word.strip()


def traverse_1(ip_file):
    for line in ip_file:
        if "INPUT" in line:
            st = line
            operand = st[ st.find("(") + 1:st.rfind(")") ]
            operand = rewrite(operand)
            operand = "G" + str(operand)
            wires[ operand ].append(operand)
            wires[ operand ].append("input")
            wires[ operand ].append(0)
            wires[ operand ].append('None')
            wires[ operand ].append([ ])
            input.append(operand)

        elif "OUTPUT" in line:
            st = line
            operand = st[ st.find("(") + 1:st.rfind(")") ]
            operand = rewrite(operand)
            operand = "G" + str(operand)

            if '$' in operand:
                operand = operand.replace('$', '_')
            output.append(operand)

        elif "#" in line:
            pass

        elif "=" in line:
            tokens = re.split('\s*=\s*', line)
            operation = re.split('\(', tokens[ -1 ])[ 0 ]
            st = tokens[ -1 ]
            operands = re.split('\s*,\s*', st[ st.find("(") + 1:st.rfind(")") ])
            tokens[ 0 ] = "G" + tokens[ 0 ]
            if '$' in tokens[ 0 ]:
                tokens[ 0 ] = rewrite(tokens[ 0 ])
                tokens[ 0 ] = tokens[ 0 ].replace('$', '_')

            for i in range(len(operands)):
                operands[ i ] = rewrite(operands[ i ])
                operands[ i ] = "G" + str(operands[ i ])

                if '$' in operands[ i ]:
                    operands[ i ] = operands[ i ].replace('$', '_')

                if ('TRUE_enc') in operands[ i ]:
                    operands[ i ] = operands[ i ].replace('TRUE_enc', "1'b1")

                elif ('FALSE_enc') in operands[ i ]:
                    operands[ i ] = operands[ i ].replace('FALSE_enc', "1'b0")

                elif 'FALSE' in operands[ i ]:
                    operands[ i ] = operands[ i ].replace('FALSE', "1'b0")

                elif 'TRUE' in operands[ i ]:
                    operands[ i ] = operands[ i ].replace('TRUE', "1'b1")

            if tokens[ 0 ] not in wires:
                wires[ tokens[ 0 ] ].append(tokens[ 0 ])
                wires[ tokens[ 0 ] ].append(operation)
                wires[ tokens[ 0 ] ].append(0)
                wires[ tokens[ 0 ] ].append(operands)
                wires[ tokens[ 0 ] ].append([ ])

def combinational():
    first_line = "module " + design_name + "( "
    module = [ ]
    module.extend(input)
    module.extend(output)
    module = set(module)
    module_write = ', '.join(module)
    op_file.writelines(first_line)
    op_file.writelines(textwrap.fill(module_write, 90, break_long_words=False, subsequent_indent='        \t'))
    op_file.writelines(");\n")

    input_write = ', '.join(input)
    output_write = ', '.join(output)
    op_file.writelines("  input ")
    op_file.writelines(textwrap.fill(input_write, 90, break_long_words=False, subsequent_indent='        \t'))
    op_file.writelines(" ;\n  output ")
    op_file.writelines(textwrap.fill(output_write, 90, break_long_words=False, subsequent_indent='        \t'))
    op_file.writelines(" ;\n  wire ")

    wire_write = [ ]
    for wire in wires.items():
        if wire[ 0 ] not in input and wire[ 0 ] not in output:
            wire_write.append(wire[ 0 ])

    wires_write = ', '.join(wire_write)
    op_file.writelines(textwrap.fill(wires_write, 90, break_long_words=False, subsequent_indent='        \t'))
    op_file.writelines(" ;\n")

    lines_write = [ ]
    count = len(wires)
    for name, wire in wires.items():
        wire[1] = wire[1].lower()
        count += 1

        if wire[ 1 ] == 'buf' or wire[ 1 ] == 'BUFF' or wire[ 1 ] == 'buff':
            temp_line = '  assign ' + wire[ 0 ] + ' = ' + wire[ 3 ][ 0 ] + " ;\n"
            op_file.writelines(temp_line)

        elif wire[ 1 ] == 'mux':
            temp_line = "GTECH_MUX2" + " U" + str(count) + " ( .A(" + rewrite(wire[ 3 ][ 1 ]) + ") ," + ".B(" + rewrite(
                wire[ 3 ][ 2 ]) + ") ," + ".S(" + rewrite(wire[ 3 ][ 0 ]) + "), " + ".Z(" + rewrite(
                wire[ 0 ]) + ") );\n"
            lines_write.append(temp_line)

        elif wire[ 1 ] != "input":
            temp_line = "GTECH_" + wire[ 1 ].upper()
            if wire[ 1 ] != 'not':
                temp_line += str(len(wire[ 3 ])) + " U" + str(count) + " ( "
            else:
                temp_line += " U" + str(count) + " ( "
            temp_operand = [ ]
            for alphabet, operand in zip(ascii_uppercase, wire[ 3 ]):
                operand_verilog = "." + alphabet + "(" + operand + ") "
                temp_operand.append(operand_verilog)
                if alphabet == 'z':
                    print ("Error: Too much fan-in")
                    exit()
            operand_verilog = ".Z(" + rewrite(wire[ 0 ]) + ") "
            temp_operand.append(operand_verilog)
            temp_line += ', '.join(temp_operand) + " );\n"
            lines_write.append(temp_line)

    op_file.writelines('\n')
    for line in lines_write:
        op_file.writelines("  ")
        op_file.writelines(line)
    op_file.writelines('endmodule\n')

if __name__ == "__main__":
    import os
    import argparse
    parser = argparse.ArgumentParser(description='ISCAS-85 bench to Verilog Converter.')
    parser.add_argument("-b", action="store", required=True, type=str, help="benchmark path")
    args = parser.parse_args()
    bench_address = args.b
    
    for filename in os.listdir(f"{bench_address}/"):
        if filename.endswith(".bench"):
            import re, textwrap, sys
            from collections import defaultdict
            from string import ascii_uppercase
            wires = defaultdict(list)  # store status
            contribution = defaultdict(list)
            temp = defaultdict(list)  # store status
            output = [ ]
            input = [ ]

            orig_inp_log = [ ]
            orig_out_log = [ ]
            strpd_inp_log = [ ]
            strpd_out_log = [ ]
            strpd_dff = [ ]

            q = [ ]
            q_bar = [ ]

            removed_ip = [ ]
            removed_op = [ ]
            removed_nodes = [ ]

            final_inputs = [ ]
            final_outputs = [ ]
            verfile_name = f"{bench_address}/" + filename
            bench_name = verfile_name[ 0:verfile_name.find(".bench") ]
            ip_file = open(verfile_name, 'r')
            design_name = "bench_design"

            traverse_1(ip_file)
            ip_file.close()
            op_file_name = bench_name + ".v"
            op_file = open(op_file_name, 'w')
            combinational()

#            print ("\033[92mOutput Saved to: %s\033[0m\n") % op_file_name

