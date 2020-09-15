
import itertools


def phash(bits):
    h = 0
    for i, b in enumerate(bits):
        if b:
            h ^= i + 1
    return h

def test_n(n):
    res = {}
    for values in itertools.product((0, 1), repeat=n):
        count = sum(values)
        h = phash(values)
        key = (count, h)
        if key not in res:
            res[key] = [values]
        else:
            res[key].append(values)
    return res

def recover_board(counts, hashes):
    def get_val(l, s, r):
        return l[s * 5 + r]
    def get_count(s, r):
        return get_val(counts, s, r)
    def get_hash(s, r):
        return get_val(hashes, s, r)
    NROWS = 5
    NCOLS = 12
    NSECTIONS = 4
    SECTION_WIDTH = NCOLS / NSECTIONS
    board = tuple([] for _ in range(NROWS))
    possibilities = test_n(3)
    for section in range(NSECTIONS):
        for row in range(NROWS):
            key = (get_count(section, row), get_hash(section, row))
            board[row].extend(possibilities[key][0])
    return board

check_1_values = [3,2,3,2,2,0,1,3,1,0,0,2,2,2,2,0,3,0,1,0,0,0,0,0]
check_1_counts = [2,2,2,2,2,3,1,2,1,3,3,1,1,1,1,3,1,3,1,3,0,0,0,0]
for row in recover_board(check_1_counts, check_1_values):
    print(row) 
