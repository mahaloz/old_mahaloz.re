import re
from pwn import *
context.arch = 'amd64'

vr_map ={}
vr_map['A8'] = "di"
vr_map['A10'] = "si"
vr_map['A22'] = "dx"
vr_map['A14'] = "r8w"
vr_map['A16'] = "r9w"
vr_map['ptr'] = "rax"
vr_map['A12'] = "r10w"
vr_map['A18'] = "r11w"
vr_map['tmp'] = "rbx"


def val_to_op(var):
    # if it is a number, just return it
    if re.match(r'0x[0-f]+', var):
        return var
    if re.match(r'(ptr)|(A\d+)', var):
        return vr_map[var]
    if re.match(r'\*ptr', var):
        return "word ptr [%s]" % vr_map[var[1:]]

    raise

def pass1(content):
    # emit x64 assembly code
    pc_line = None
    output = ""

    # process basic blocks
    for bb in content.split('-------------'):
        lines = bb.splitlines()
        output += '\n'
        for line in lines:
            if not line:
                continue
            res = re.match(r'^---- (\d+) ----$', line)
            if res:
                label = "label%s" % res.group(1)
                output += label+":\n"
                continue

            if 'PC' in line:
                pc_line = line.split('#')[0].strip()
                continue

            res = re.match(r'^([\*\w]+) = ([\*\w]+)$', line)
            if res:
                op1 = val_to_op(res.group(1))
                op2 = val_to_op(res.group(2))
                output += "mov %s, %s\n" % (op1, op2)
                continue

            res = re.match(r'^([\*\w]+) = ([\*\w]+) \+ ([\*\w]+)$', line)
            if res:
                op1 = val_to_op(res.group(1))
                op2 = val_to_op(res.group(2))
                op3 = val_to_op(res.group(3))
                #print(op1, op2, op3)
                output += "xor rbx, rbx\nmov bx, %s\nadd bx, %s\nmov %s, bx\n" % (op3, op2, op1)
                continue

            print(line)
            raise

        # process control flow
        res = re.match(r'^PC = (\d+)$', pc_line)
        if res:
            output += "jmp label%s\n" % res.group(1)
            continue
        res = re.match(r'^PC = (\d+) if (A\d+) == 0 else (\d+)$', pc_line)
        if res:
            guard = res.group(2)
            br1 = res.group(1)
            br2 = res.group(3)
            op = val_to_op(guard)
            # fix:
            if 'w' in op:
                op = op.replace('w', 'b')
            else:
                op += 'l'
            output += "test %s, %s\njz label%s\njmp label%s\n" % (op, op, br1, br2)
            #import IPython;IPython.embed()
            #print('------')
            continue
        print([pc_line])
        raise
    return output

def pass2(content):
    # fix the broken assembly
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        if 'rax' in line and 'word ptr' not in line:
            line = line.replace('rax', 'ax')
        new_lines.append(line)
    return '\n'.join(new_lines)

def pass3(content):
    # add exit label
    content += "\n\nlabel65534:\nmov rax, 60\nsyscall\nret\n"
    return content

def pass4(content):
    # strip uncessary label so hopefully IDA can analyze it
    # FIXME: this pass is broken

    # gather necessary labels first
    good_labels = set()
    lines = content.splitlines()
    for i in range(len(lines)):
        line = lines[i]
        if 'jz' in line:
            good_labels.add(line.split()[1])
            good_labels.add(lines[i+1].split()[1])
    good_labels.add('label65534')
    print(good_labels)

    # strip labels that are unncessary
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        if 'label' in line:
            res = re.match('^(label\d+):$', line)
            if res:
                label = res.group(1)
                if label not in good_labels:
                    continue
            res = re.match('^jmp (label\d+)$', line)
            if res:
                label = res.group(1)
                if label not in good_labels:
                    continue
        new_lines.append(line)
    #return None
    return '\n'.join(new_lines)

def pass5(content):
    # add init code
    content = shellcraft.linux.mmap(0, 0x10000, 3, 50, -1, 0) + shellcraft.linux.read(0, 0xe000, 0x100) + shellcraft.setregs({'rax':1, 'rbx':'0', 'rdi': '0', 'rsi': '0', 'rdx': '0', 'r8': '0', 'r9':'0', 'r10':'0'}) + content
    return content

with open("opt_assembly") as f:
    content = f.read()

content = pass1(content)
content = pass2(content)
content = pass3(content)
#content = pass4(content)
content = pass5(content)
print(content)
e = ELF.from_assembly(content)
e.save('unpacked')

