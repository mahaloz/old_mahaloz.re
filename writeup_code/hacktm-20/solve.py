import hashlib
import binascii
import random
import string
import logging
import time
def get_grid(X, Y):
    """Return a dictionary of grid positions to random letters"""
    return {(x, y): random.choice(string.ascii_lowercase) for x in range(X) for y in range(Y)}
def get_neighbours(X, Y, grid):
    """Return a dictionary with all the neighbours surrounding a particular position"""
    neighbours = {}
    for position in grid:
        x, y = position
        positions = [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1), (x + 1, y),
                     (x + 1, y + 1), (x, y + 1), (x - 1, y + 1), (x - 1, y)]
        neighbours[position] = [p for p in positions if 0 <= p[0] < X and 0 <= p[1] < Y]
    return neighbours
def path_to_word(path, grid):
    """Convert a list of grid positions to a word"""
    return ''.join([grid[p] for p in path])
def search(path, paths, stems, dictionary, neighbours, grid):
    """Recursively search the grid for words"""
    word = path_to_word(path, grid)
    # logging.debug('%s: %s' % (path, word))
    if word not in stems:
        return
    if word in dictionary:
        paths.append(path)
    for next_pos in neighbours[path[-1]]:
        if next_pos not in path:
            search(path + [next_pos], paths, stems, dictionary, neighbours, grid)
        else:
            logging.debug('skipping %s because in path', grid[next_pos])
def get_dictionary():
    """Return a list of uppercase english words, including word stems"""
    stems, dictionary = set(), set()
    with open('hacktm.hdex', "rb") as f:
        data = f.read()
    lines = data.split(b"\n")
    for line in lines:
        if not line.strip():
            continue
        word = line[ : line.find(b"<br>")].decode("ascii")
        word = word.strip().lower()
        dictionary.add(word)
        for i in range(len(word)):
            stems.add(word[:i + 1])
    return dictionary, stems

def get_words(grid, paths, stems, dictionary, neighbours):
    """Search each grid position and return all the words found"""
    for position in grid:
        print('searching %s' % str(position))
        search([position], paths, stems, dictionary, neighbours, grid)
    return [path_to_word(p, grid) for p in paths]

def print_grid(X, Y, grid):
    """Print the grid as a readable string"""
    s = ''
    for y in range(Y):
        for x in range(X):
            s += grid[x, y] + ' '
        s += '\n'
    print(s)


BOARDS = {
    0: ["zel", "ann", "rig"],
    1: ["tkl", "bui", "nrf"],
    2: ["fri", "pen", "uad"],
    3: ["emz", "bna", "xeh", "wtv"],
    4: ["evo", "rux", "com", "gni"],
    5: ["plz", "asi", "son"],
}
B = {
    0: [],
    1: [],
    2: [],
    3: [],
    4: [],
    5: [],
}
def sha256sum(s):
    sha256 = hashlib.sha256()
    sha256.update(s.encode("ascii"))
    return sha256.digest()
def main():
    # ===== GENERATE BOGGLE WORDS ===== #
    for i in range(6):
        board = BOARDS[i]
        X = len(board[0])
        Y = len(board)
        grid = {}
        for x in range(X):
            for y in range(Y):
                grid[(x, y)] = board[y][x]
        neighbours = get_neighbours(X, Y, grid)
        dictionary, stems = get_dictionary()
        paths = []
        print_grid(X, Y, grid)
        words = get_words(grid, paths, stems, dictionary, neighbours)
        B[i] = [ w for w in words if len(w) > 1 ]
    
    # ===== FILTER WORDS ===== #
    with open("hacktm.hdex", "rb") as f:
        data = f.read()
    lines = data.split(b"\n")
    words = set()
    for line in lines:
        if not line.strip():
            continue
        word = line[ : line.find(b"<br>")]
        words.add(word.decode("ascii"))
    for i in range(6):
        print(len(B[i]), "...")
        B[i] = list(set(B[i]).intersection(words))
        print(len(B[i]))
    target = binascii.unhexlify("F550BAA8068D9C17669E140626A9D7BF13EF0A66662AEB5910FC406BE196A287")
    
    # ===== FIND THE HASH ====== #
    for word_0 in B[0]:
        print(word_0 + "...")
        for word_1 in B[1]:
            for word_2 in B[2]:
                for word_3 in B[3]:
                    for word_4 in B[4]:
                        for word_5 in B[5]:
                            s = word_0 + word_1 + word_2 + word_3 + word_4 + word_5
                            if len(s) <= 31:
                                continue
                            h = sha256sum(s)
                            if h == target:
                                print(h, word_0, word_1, word_2, word_3, word_4, word_5)
if __name__ == "__main__":
    main()
