# Implementation of Cargo
# See https://stackoverflow.com/questions/16801322/how-can-i-check-that-a-list-has-one-and-only-one-truthy-value
import string
from random import randint, choice
from pprint import pprint
import sys

import copy

board_log = open("board.log", "a")

def single_true(iterable):
    i = iter(iterable)
    return any(i) and not any(i)

nodes = []
node_locs = []
dests = [] # For gen_cargo purposes
dests_locs = []
sources = [] # Same as dests
sources_locs = []
points = [] # we've been through this
points_loc = []

X = 0
Y = 1

old_truck_object = [0, 0]

is_ai = False

def gen_cargo():
    cargo_points = []
    num_points = randint(1, 3)
    possible_points = points.copy()
    for _ in range(num_points):
        cargo_points.append(possible_points.pop(randint(0, len(possible_points) - 1))) # I am so sorry
    cargo_points.append(choice(dests))
    comes_from = choice(sources)
    return Cargo(from_=comes_from, must_go_to=cargo_points)
class Cargo:
    def __init__(self,from_="H", must_go_to=["A", 1]):
        self._been_to = [from_]
        self._left_to_go: list = must_go_to
    def is_valid_dest(self, node):
        if type(self._left_to_go[0]) == int:
            if node.is_dest:
                return True
        else:
            ltg = self._left_to_go.pop(0)
            return node.id == ltg
class Node:
    def __init__(self, is_source=True, is_dest=False, is_point=False, id="H", location=(0,0)):
        assert single_true([is_source, is_dest, is_point])
        assert location[0] <= 9 and location[0] <= 9
        assert node_locs.count(list(reversed(location))) == 0
        nodes.append(self)
        node_locs.append(list(reversed(location)))
        self._location = location
        if is_source:
            assert string.ascii_uppercase.index(id) >= string.ascii_uppercase.index("H")
            sources.append(id)
            sources_locs.append(list(reversed(location)))
        if is_point:
            assert string.ascii_uppercase.index(id) < string.ascii_uppercase.index("H")
            points.append(id)
            points_loc.append(list(reversed(location)))
        if is_dest:
            id = int(id)
            dests.append(id)
            dests_locs.append(list(reversed(location)))
        self.id = id
        self.is_source = is_source
        self.is_dest = is_dest
        self.is_point = is_point
        self._cargo = gen_cargo() if is_source else None
    def _regen_cargo(self):
        assert self.is_source
        self._cargo = gen_cargo()
    def take_cargo(self):
        assert self._cargo
        old_cargo = self._cargo
        if self.is_source:
            self._regen_cargo()
        return old_cargo
    def deliver_cargo(self, cargo):
        if cargo.is_valid_dest(self):
            self._cargo = cargo
            return True
        else:
            return False
class Truck:
    def __init__(self, starting_pos=(0,0)):
        self._cargo = None
        self.fuel = 100
        self.delivered = 0
        self.pos = list(starting_pos)
        self.fuel_out = False
        self.make_new = False
        self.game = None
    def move_up(self):
        new_pos = copy.copy(self.pos)
        new_pos[Y] -= 1
        return self.do_pos_stuff(new_pos)
    def move_down(self):
        new_pos = copy.copy(self.pos)
        new_pos[Y] += 1
        return self.do_pos_stuff(new_pos)
    def move_left(self):
        new_pos = copy.copy(self.pos)
        new_pos[X] -= 1
        return self.do_pos_stuff(new_pos)
    def move_right(self):
        new_pos = copy.copy(self.pos)
        new_pos[X] += 1
        return self.do_pos_stuff(new_pos)
    def do_pos_stuff(self, new_pos):
        global old_truck_object
        if self.fuel - 1 == 0:
            self.fuel_out = True
            return False
        if new_pos in node_locs:
            # Assume index of node in nodes == index of node_loc in node_locs
            node = nodes[node_locs.index(new_pos)]
            if node.is_source:
                if self._cargo:
                    if not is_ai:
                        print("You have cargo, and can not move onto this source.")
                    return False # We can't pick up new cargo without dropping ours
                else:
                    self._cargo = node.take_cargo()
            else:
                if self._cargo:
                    did_drop = node.deliver_cargo(self._cargo)
                    if node.is_dest and did_drop:
                        self.delivered += 1
                        self.make_new = True
                    if did_drop:
                        self._cargo = None
                        self.fuel -= 1
                        old_pos = copy.copy(self.pos)
                        old_truck_object = old_pos
                        self.pos = new_pos
                        if old_pos in node_locs:
                            self.game.on_node = True
                            self.game.board[old_pos[Y]][old_pos[X]] = nodes[node_locs.index(old_pos)]
                    else:
                        if not is_ai:
                            print("This is an invalid location for your cargo.")
                    return did_drop
                elif node.is_point and node._cargo:
                    # Take cargo from the node
                    self._cargo = node.take_cargo()
                else:
                    if not is_ai:
                        print("You need cargo to move to this node")
                    return False # We need to put cargo down to move onto this node
            self.fuel -= 1
            old_pos = copy.copy(self.pos)
            old_truck_object = old_pos
            self.pos = new_pos
            if old_pos in node_locs:
                self.game.on_node = True
                self.game.board[old_pos[Y]][old_pos[X]] = nodes[node_locs.index(old_pos)]
            return True
        elif (0 <= new_pos[X] <= 8) and (0 <= new_pos[Y] <= 8):
            self.fuel -= 1
            old_pos = copy.copy(self.pos)
            old_truck_object = copy.copy(old_pos)
            self.pos = new_pos
            if old_pos in node_locs:
                self.game.on_node = True
                self.game.board[old_pos[Y]][old_pos[X]] = nodes[node_locs.index(old_pos)]
            return True
        else:
            if not is_ai:
                print("Position is off the board", new_pos)
            return False
def generate_thingy(board):
    while True:
        x = randint(0, 8)   
        y = randint(0, 8)   
        print(x,y)
        print(node_locs)
        if not [y,x] in node_locs and not [x,y] == [0, 0]:
            return (x, y)

class Game:
    def __init__(self):
        self.truck = Truck()
        self.regen_board()
    def regen_board(self):
        nodes = []
        node_locs = []
        dests = []
        sources = []
        points = []
        self.truck.cargo = None
        self.truck.make_new = False
        self.on_node = False
        self.truck.pos = [0,0]
        self.truck.game = self
        self.board = [
            [self.truck, None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None]
        ]
        
        for _ in range(3):
            node_loc = generate_thingy(self.board)
            self.board[node_loc[X]][node_loc[Y]] = Node(is_point=True, is_source=False, location=node_loc, id=choice(string.ascii_uppercase[:6]))
        for _ in range(3):
            node_loc = generate_thingy(self.board)
            self.board[node_loc[X]][node_loc[Y]] = Node(is_dest=True, is_source=False, location=node_loc, id=randint(1,3))
            node_loc = generate_thingy(self.board)
            self.board[node_loc[X]][node_loc[Y]] = Node(is_source=True, location=node_loc, id=choice(string.ascii_uppercase[7:]))
    def update_board(self):
        # Moves the truck
        #line = 0
        #for lines in self.board:
            #try:
            #    truck_loc = lines.index(self.truck)
            #    oy, ox = line, truck_loc
            #    print("found the truck!")
            #    print(ox, oy)
            #    x, y = self.truck.pos
            #    break
            #except:
            #    print("Nope")
            #    pass # no truck on this line
            #line += 1
        ox, oy = old_truck_object
        x, y = self.truck.pos
        if not self.on_node:
            self.board[oy][ox] = None
        else:
            self.on_node = False
        self.board[y][x] = self.truck
if __name__ == "__main__":
    g = Game()
    while not g.truck.fuel_out:
        movement = {
            "u": g.truck.move_up,
            "d": g.truck.move_down,
            "l": g.truck.move_left,
            "r": g.truck.move_right
        }
        for line in g.board:
            print("|", end="")
            for item in line:
                if item == None:
                    print("-", end="")
                elif type(item) == Truck:
                    print("@", end="")
                else:
                    print(item.id, end="")
            print("|")
        print("-----------")
        print("Score:", g.truck.delivered)
        print("Fuel:", g.truck.fuel, "/ 100")
        if g.truck._cargo:
            print("Cargo:", g.truck._cargo._left_to_go)
        while True:
            try:
                direction = input("(U)p/(D)own/(L)eft/(R)ight").lower()[0]
            except IndexError:
                continue
            try:
                valid_move = movement[direction]()
            except KeyError:
                print("Invalid move. (KeyError)")
                continue
            if not valid_move:
                print("Invalid move.")
                continue
            g.update_board()
            if g.truck.make_new:
                print("GOOD GAME")
                g.regen_board()
            break
    

def log_board(board):
    global board_log # I am so sorry
    if board_log.closed:
        board_log = open("board.log", "a") # reopen log
    for line in board:
        board_log.write("|")
        for item in line:
            if item == None:
                board_log.write("-")
            elif type(item) == Truck:
                board_log.write("@")
            else:
                board_log.write(str(item.id))
        board_log.write("|\n")
    board_log.write("-----------\n")
    #print("Fuel:", g.truck.fuel, "/ 100")

def expiremental_board_print(board):
    clear = "\033[2J\033[H"
    print(clear, end="")
    for line in board:
        print("|", end="")
        for item in line:
            if item == None:
                print("-", end="")
            elif type(item) == Truck:
                print("@", end="")
            else:
                print(str(item.id), end="")
        print("|")


def gen_till_crash(stop_at):
    # For debugging purposes
    # Continually generates nodes
    # Until an error occurs
    global node_locs
    board = [
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None, None]
    ]
    for _ in range(stop_at):
        node_locs = []
        for _ in range(9 * 9):
            node_loc = generate_thingy(board)
            print(node_loc)
            board[node_loc[Y]][node_loc[X]] = Node(is_point=True, is_source=False, location=node_loc, id=choice(string.ascii_uppercase[:6]))