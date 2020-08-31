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

class Format:
    def __init__(self, string):
        arg_num = None
        len_arg_num = None
        con_len = None
        formatter = None

        self._parse(string)

    def _parse(self, string):
        res = re.match(f"(\d+)\$(.+\$)?(\d*)(\w+)", string)
        assert res is not None, string

        arg_num = int(res.group(1))
        var_len = res.group(2)
        con_len = res.group(3)
        formatter = res.group(4)
        len_arg_num = None

        # transform the things a little bit
        if not con_len or int(con_len) == 0: con_len = None
        if con_len: con_len = int(con_len)

        # sanity checks
        assert con_len is None or var_len is None

        # parse variable length argument number
        if var_len:
            res = re.match(f"\*(\d+)\$", var_len)
            assert res is not None, var_len
            len_arg_num = int(res.group(1))

        self.arg_num = arg_num
        self.len_arg_num = len_arg_num
        self.con_len = con_len
        self.formatter = formatter

def f2action(sub_fs):
    prev_idx = 0
    for i in range(len(sub_fs)):
        sub_f = sub_fs[i]

        # hn indicates the end of an action
        if sub_f.formatter != 'hn':
            continue

        # take out all formats that belongs to one action
        action_fs = sub_fs[prev_idx:i+2]
        prev_idx = i+2
        if action_fs[-1].con_len and action_fs[-1].con_len > 60000:
            action_fs = action_fs[:-1]
        assert action_fs[-1].formatter == 'hn'

        #print([x.__dict__ for x in action_fs])

        output = 'A%d =' % (action_fs[-1].arg_num)
        first = 1
        for action_f in action_fs[:-1]:
            if first:
                first = 0
            else:
                output += ' +'
            if action_f.formatter == 's' and action_f.con_len:
                #val = min(action_f.con_len, 0x10000 - action_f.con_len)
                #sign = '+' if val == action_f.con_len else '-'
                #if sign == '-':
                #    output += ' %s%d' % (sign, val)
                #else:
                #    output += ' %d' % (val)
                output += ' %#x' % (action_f.con_len)
                continue

            if action_f.formatter == 's' and not action_f.len_arg_num:
                output += ' A%d' % action_f.arg_num
                continue

            if action_f.formatter == 's' and action_f.len_arg_num:
                output += ' max(A%d, A%d)' % (action_f.len_arg_num, action_f.arg_num)
                continue

            if action_f.formatter == 'c' and action_f.len_arg_num is None:
                #output += ' (1 if A%d else 0)' % (action_f.arg_num)
                if action_f.arg_num == 2:
                    output += ' 1'
                else:
                    output += ' COND_JUMP_A%d' % (action_f.arg_num)
                continue

            print(action_f.__dict__)

        print(output)
        continue

        print([x.__dict__ for x in action_fs])


# try to parse formats
for i in range(len(formats)):
    f = formats[i]
    stuff = [x for x in f.split('%') if x]
    sub_fs = [Format(sub_f_s) for sub_f_s in stuff]
    print('---- %d ----' % i)
    actions = f2action(sub_fs)
    print('-------------')
    print('')
