from random import shuffle, randint, choice
from functools import reduce

SYM_TO_F = {
    "+": sum,
    "-": lambda l: reduce(lambda a, b: a-b, l, 0),
    "/": lambda l: reduce(lambda a, b: a/b, l, 1),
    "*": lambda l: reduce(lambda a, b: a*b, l, 1)
}

class Cell:

    def __init__(self, value, cage=None):
        self.value = value
        if cage is not None:
            self.in_cage = in_cage[0]
            self.cage = in_cage[1]
        else:
            self.in_cage = False
            self.cage = -1

    def update(self, new_val):
        self.value = new_val

    def encage(self, cage):
        self.in_cage = True
        self.cage = cage

    def __str__(self):
        return str(self.value)

class Cage:

    def __init__(self, down=0, left=0, right=0, up=0, hinge=None, b=None):
        self.down = down
        self.up = up
        self.left = left
        self.right = right
        self.hinge = hinge
        row, col = hinge
        elems = [b.cells[row][col].value]
        for i in range(1, self.left):
            elems.append(b.cells[row][col - i].value)
        for i in range(1, self.right):
            elems.append(b.cells[row][col + i].value)
        for i in range(1, self.up):
            elems.append(b.cells[row - i][col].value)
        for i in range(1, self.right):
            elems.append(b.cells[row + i][col].value)
        self.elems = elems
        if sum([left, right, up, down]) == 1:
            self.op = choice(['+', '-', '*', '/'])
            if self.op == '/' or self.op == '-':
                self.elems.sort()
                self.elems.reverse()
            self.result = SYM_TO_F[self.op](elems)
        elif sum([left, right, up, down]) > 1:
            self.op = choice(['+', '*'])
            self.result = SYM_TO_F[self.op](elems)
        else:
            self.op = None
            self.result = elems[0]

    def __str__(self):
        if self.op is not None:
            return "{}:\t{} {}".format(str(self.elems), self.op, self.result)
        return "{}:\t{}".format(str(self.elems), self.result)

class Board:

    def __init__(self, dim=3):
        assert dim >= 3
        self.cells = [[Cell(0) for i in range(dim)] for i in range(dim)]
        self.dim = dim
        self.fill()
        self.cages = self.generate_cages()

    def get_row_vals(self, r):
        return [cell.value for cell in self.cells[r]]

    def get_column_vals(self, c):
        return [row[c].value for row in self.cells]

    def is_valid(self):
        for i in range(self.dim):
            row = self.get_row_vals(i)
            col = self.get_row_vals(i)
            for val in range(1, self.dim + 1):
                valid_row = row.count(val) <= 1
                valid_col = col.count(val) <= 1
                if (not valid_row) or (not valid_col):
                    return False
        return True

    def fill(self, cell_num=0):
        if not self.is_valid():
            return False
        if cell_num >= self.dim ** 2:
            return True
        r = int(cell_num / self.dim)
        c = cell_num % self.dim
        vals = list(range(1, self.dim + 1))
        shuffle(vals)
        for val in vals:
            self.cells[r][c].update(val)
            next_sol = self.fill(cell_num + 1)
            if next_sol is True:
                return True
        return False

    def random_cell(self):
        return (randint(0, self.dim - 1), randint(0, self.dim - 1))

    def are_all_encaged(self):
        f = lambda c: c.value
        all_caged = [[True for i in range(self.dim)] for i in range(self.dim)]
        return [list(map(f, row)) for row in self.cells] == all_caged

    def possible_cages_with_hinge(self, hinge):
        row, col = hinge
        max_up = 0
        for i in range(row, 0, -1):
            if self.cells[i][col].in_cage:
                break
            max_up += 1
        max_down = 0
        for i in range(row, self.dim):
            if self.cells[i][col].in_cage:
                break
            max_down += 1
        max_left = 0
        for i in range(col, 0, -1):
            if self.cells[row][i].in_cage:
                break
            max_left += 1
        max_right = 1
        for i in range(col, self.dim):
            if self.cells[row][i].in_cage:
                break
            max_left += 1
        possible = []
        up, down, left, right = 1, 1, 1, 1
        while up < max_up:
            if up <= max_left:
                possible.append(Cage(up=up, left=up, hinge=hinge, b=self))
            if up <= max_right:
                possible.append(Cage(up=up, right=up, hinge=hinge, b=self))
            possible.append(Cage(up=up, hinge=hinge, b=self))
            up += 1
        while down < max_down:
            if down <= max_left:
                possible.append(Cage(down=down, left=down, hinge=hinge, b=self))
            if down <= max_right:
                possible.append(Cage(down=down, right=down, hinge=hinge, b=self))
            possible.append(Cage(down=down, hinge=hinge, b=self))
            down += 1
        while left < max_left:
            if left <= max_up:
                possible.append(Cage(left=left, up=left, hinge=hinge, b=self))
            if left <= max_down:
                possible.append(Cage(left=left, down=left, hinge=hinge, b=self))
            possible.append(Cage(left=left, hinge=hinge, b=self))
            left += 1
        while right < max_right:
            if right <= max_up:
                possible.append(Cage(right=right, up=right, hinge=hinge, b=self))
            if right <= max_down:
                possible.append(Cage(left=right, down=right, hinge=hinge, b=self))
            possible.append(Cage(right=right, hinge=hinge, b=self))
            right += 1
        possible.append(Cage(hinge=hinge, b=self))
        return possible

    def encage_with(self, cage, counter):
        row, col = cage.hinge
        self.cells[row][col].encage(counter)
        left, right, up, down = 1, 1, 1, 1
        while left < cage.left:
            self.cells[row][col - left].encage(counter)
            left += 1
        while right < cage.right:
            self.cells[row][col + right].encage(counter)
            right += 1
        while up < cage.up:
            self.cells[row + up][col].encage(counter)
            up += 1
        while down < cage.down:
            self.cells[row - down][col].encage(counter)
            down += 1

    def generate_cages(self):
        cages = []
        counter = 0
        for row in range(self.dim):
            for col in range(self.dim):
                cell = self.cells[row][col]
                if not cell.in_cage:
                    # get all possible cages you can place
                    possible = self.possible_cages_with_hinge((row, col))
                    # pick a random one
                    rand = choice(possible)
                    # place it
                    cages.append(rand)
                    self.encage_with(rand, counter)
                    counter += 1
        return cages

    def __str__(self):
        return str([list(map(str, row)) for row in self.cells])

b = Board(dim=10)
print(list(map(str, b.cages)))
