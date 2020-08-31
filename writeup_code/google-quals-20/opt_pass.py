import re

# load formats
with open("formats.txt") as f:
    formats = eval(f.read())

# len-pc mapping
s = 0 
mapping = {}
for i in range(len(formats)):
    mapping[s] = i 
    f = formats[i]
    s += len(f) + 1
mapping[0xfffe] = 0xfffe
#print(mapping)

def pass1(content):
    # A2 is always 0
    new_content = content.replace(' + (1 if A2 else 0)', '')
    return new_content

def pass2(content):
    # translate "set A3" to PC
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        res = re.match(f"A3 = (0x\w+)", line)
        if res:
            l = int(res.group(1), 16)
            pc = (mapping[l])
            line = "PC = %d" % pc
            line = line.ljust(40)
            comment = "# A3 = %d" % l
            line += comment
        new_lines.append(line)
    return '\n'.join(new_lines)

def pass3(content):
    # replace duplicates
    # e.g. A7 is the write and A6 is the read to the same location
    for i in range(8, 24, 2):
        read_tag = "A%d" % i
        write_tag = "A%d" % (i+1)
        content = content.replace(write_tag, read_tag)
    return content

def pass4(content):
    # in fact, max(x, A1) is actually just Ax
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        while True:
            res = re.search(f"max\((A\d+), A1\)", line)
            if not res:
                break
            line = line.replace(res.group(0), res.group(1))
        new_lines.append(line)
    return '\n'.join(new_lines)

def pass5(content):
    new_content = content.replace("A6", "*ptr")
    new_content = new_content.replace("A5", "*ptr")
    new_content = new_content.replace("A7", "ptr")
    return new_content

def pass6(content):
    # handle conditional jump
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        res = re.match(f"A3 = COND_JUMP_(A\d+) \+ (0x\w+) \+ 1 \+ A4 \+ (0x\w+)", line)
        if res:
            guard = res.group(1)
            base = int(res.group(3), 16) + 1
            switcher = int(res.group(2), 16) + 1
            br1 = (base + switcher) & 0xffff
            br2 = (base + switcher*2) & 0xffff
            assert br1 in mapping and br2 in mapping
            line = "PC = %d if %s == 0 else %d" % (mapping[br1], guard, mapping[br2])
            line = line.ljust(40)
            comment = "# A3 = %d if %s == 0 else %d" % (br1, guard, br2)
            line += comment
        new_lines.append(line)
    return '\n'.join(new_lines)

def pass7(content):
    # A1 is just 0
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        res = re.search(f"A1$", line)
        if res:
            line = '0x0'.join(line.rsplit('A1', 1))
        new_lines.append(line)
    return '\n'.join(new_lines)

with open("assembly") as f:
    content = f.read()

content = pass1(content)
content = pass2(content)
content = pass3(content)
content = pass4(content)
content = pass5(content)
content = pass6(content)
content = pass7(content)
print(content)

