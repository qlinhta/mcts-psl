import numpy as np
import logging

MAX_GRID_SIZE = 64
MAX_HISTORY_SIZE = 1000
MAX_LEGAL_MOVES = 1000
MAX_POLICY_SIZE = 7000


class Grid:
    def __init__(self):
        self.move_history_count = 0
        self.grid = np.zeros((MAX_GRID_SIZE, MAX_GRID_SIZE), dtype=int)
        self.history = np.zeros(MAX_HISTORY_SIZE, dtype=int)
        self.move_count = 0
        self.moves = np.zeros(MAX_LEGAL_MOVES, dtype=int)
        self.priority = np.zeros(MAX_LEGAL_MOVES, dtype=int)
        self.dominator = np.full(MAX_LEGAL_MOVES, 999, dtype=int)
        self.code = np.zeros(MAX_LEGAL_MOVES, dtype=int)

    def copy(self):
        new_grid = Grid()
        new_grid.move_history_count = self.move_history_count
        new_grid.grid = self.grid.copy()
        new_grid.history = self.history.copy()
        new_grid.move_count = self.move_count
        new_grid.moves = self.moves.copy()
        new_grid.priority = self.priority.copy()
        new_grid.dominator = self.dominator.copy()
        new_grid.code = self.code.copy()
        return new_grid


def initialize_game(grid):
    logging.info("Initializing game")
    grid.move_history_count = 0
    grid.grid.fill(0)
    grid.grid[31, 34:38] = 1
    grid.grid[32, [34, 37]] = 1
    grid.grid[33, [34, 37]] = 1
    grid.grid[34, [31, 32, 33, 34, 37, 38, 39, 40]] = 1
    grid.grid[35, [31, 40]] = 1
    grid.grid[36, [31, 40]] = 1
    grid.grid[37, [31, 32, 33, 34, 37, 38, 39, 40]] = 1
    grid.grid[38, [34, 37]] = 1
    grid.grid[39, [34, 37]] = 1
    grid.grid[40, 34:38] = 1

    delta = (MAX_GRID_SIZE - 30) // 2
    for i in range(MAX_GRID_SIZE):
        for j in range(MAX_GRID_SIZE):
            if i > delta and j > delta:
                grid.grid[i - delta, j - delta] = grid.grid[i, j]
                grid.grid[i, j] = 0
    logging.info("Game initialized")
    return 0


def display_game(grid, file):
    logging.info("Displaying game")
    total = 0
    min_x, max_x = MAX_GRID_SIZE, 0
    min_y, max_y = MAX_GRID_SIZE, 0
    for i in range(1, MAX_GRID_SIZE):
        for j in range(1, MAX_GRID_SIZE):
            if grid.grid[i, j] not in [0, 512]:
                total += 1
                if i > max_x:
                    max_x = i
                if i < min_x:
                    min_x = i
                if j > max_y:
                    max_y = j
                if j < min_y:
                    min_y = j
    file.write(f"Grid total score ={total}\n")
    file.write(f"xMin={min_x} xMax={max_x} yMin={min_y} yMax={max_y}\n")
    file.write("Move history\n")
    for i in range(grid.move_history_count):
        file.write(
            f"move {i + 1:02d} {grid.history[i]} x={unpack_x(grid.history[i])} y={unpack_y(grid.history[i])} d={unpack_direction(grid.history[i])} k={unpack_k(grid.history[i])} \n")
    file.write("List of possible moves from this position\n")
    for i in range(grid.move_count):
        file.write(
            f"move {i:02d} {grid.moves[i]} x={unpack_x(grid.moves[i])} y={unpack_y(grid.moves[i])} d={unpack_direction(grid.moves[i])} k={unpack_k(grid.moves[i])} d={grid.dominator[i]:03d} p={grid.priority[i]} c={grid.code[i]}\n")
    for jj in range(MAX_GRID_SIZE - max_y - 1, MAX_GRID_SIZE - min_y - 1 + 1):
        j = MAX_GRID_SIZE - jj - 1
        line1, line2, line3, line4, line5 = "    | ", "    | ", f"{j:03d} | ", "    | ", "    | "
        for i in range(min_x, max_x + 1):
            if grid.grid[i, j] & 256:
                line1 += "\\ "
                line2 += " \\"
            else:
                line1 += "  "
                line2 += "  "
            if grid.grid[i, j] & 2:
                line1 += "|"
                line2 += "|"
            else:
                line1 += " "
                line2 += " "
            if grid.grid[i, j] & 4:
                line1 += " /"
                line2 += "/ "
            else:
                line1 += "  "
                line2 += "  "
            line3 += "-" if grid.grid[i, j] & 128 else " "
            value = " ? " if grid.grid[i, j] % 2 == 0 and grid.grid[i, j] > 0 else "   "
            if grid.grid[i, j] % 2 == 1:
                value = "xxx"
                for ii in range(grid.move_history_count):
                    if i == unpack_x(grid.history[ii]) and j == unpack_y(grid.history[ii]):
                        value = f"{ii + 1:03d}"
                if value == "xxx":
                    value = " + "
            line3 += value
            line3 += "-" if grid.grid[i, j] & 8 else " "
            if grid.grid[i, j] & 64:
                line4 += " /"
                line5 += "/ "
            else:
                line4 += "  "
                line5 += "  "
            if grid.grid[i, j] & 32:
                line4 += "|"
                line5 += "|"
            else:
                line4 += " "
                line5 += " "
            if grid.grid[i, j] & 16:
                line4 += "\\ "
                line5 += " \\"
            else:
                line4 += "  "
                line5 += "  "
        file.write(f"{line1}\n{line2}\n{line3}\n{line4}\n{line5}\n")
    line1 = "----+-"
    for i in range(min_x, max_x + 1):
        line1 += f"-{i:03d}-"
    file.write(f"{line1}\n")
    logging.info("Game displayed")


def unpack_x(value):
    return value // 10000


def unpack_y(value):
    return (value % 10000) // 100


def unpack_direction(value):
    return (value % 100) // 10


def unpack_k(value):
    return value % 10


def pack_move(x, y, direction, k):
    return 10000 * x + 100 * y + 10 * direction + k


def update_dominator(grid):
    if grid.move_count > 0:
        for i in range(grid.move_count):
            if grid.priority[i] == 1010:
                x1 = unpack_x(grid.moves[i])
                y1 = unpack_y(grid.moves[i])
                direction1 = unpack_direction(grid.moves[i])
                for j in range(grid.move_count):
                    if i != j and grid.priority[j] != 1010:
                        x2 = unpack_x(grid.moves[j])
                        y2 = unpack_y(grid.moves[j])
                        direction2 = unpack_direction(grid.moves[j])
                        if x1 == x2 and y1 == y2 and direction1 == direction2:
                            grid.dominator[j] = i


def play_move(source_grid, target_grid, move_index):
    dirX = [0, 1, 1, 1]
    dirY = [1, 1, 0, -1]
    dirD = [2, 4, 8, 16]
    dirO = [32, 64, 128, 256]
    dirDO = [34, 68, 136, 272]

    if source_grid != target_grid:
        target_grid.grid = np.copy(source_grid.grid)
        target_grid.move_history_count = source_grid.move_history_count
        target_grid.history[:target_grid.move_history_count] = source_grid.history[:target_grid.move_history_count]

    if source_grid.dominator[move_index] != 999:
        move_index = source_grid.dominator[move_index]

    target_grid.history[target_grid.move_history_count] = source_grid.moves[move_index]
    target_grid.move_history_count += 1

    if target_grid.move_history_count > MAX_HISTORY_SIZE:
        raise ValueError("Move history storage table too small")

    if target_grid.grid[unpack_x(source_grid.moves[move_index]), unpack_y(source_grid.moves[move_index])] != 0:
        raise ValueError("Grid contains something at the played point")

    moveX = unpack_x(source_grid.moves[move_index])
    moveY = unpack_y(source_grid.moves[move_index])
    moveDirection = unpack_direction(source_grid.moves[move_index])
    moveK = unpack_k(source_grid.moves[move_index])
    target_grid.grid[moveX, moveY] = 1
    for uu in range(-4, 1):
        alpha = moveK + uu
        ii = moveX + (alpha * dirX[moveDirection])
        jj = moveY + (alpha * dirY[moveDirection])
        if target_grid.grid[ii, jj] % 2 != 1:
            raise ValueError("Grid is empty on a point supporting an alignment")
        if uu == -4:
            target_grid.grid[ii, jj] += dirD[moveDirection]
        if uu == 0:
            target_grid.grid[ii, jj] += dirO[moveDirection]
        if uu in [-3, -2, -1]:
            target_grid.grid[ii, jj] += dirDO[moveDirection]


def search_moves(grid):
    dirX = [0, 1, 1, 1]
    dirY = [1, 1, 0, -1]
    dirD = [2, 4, 8, 16]
    dirO = [32, 64, 128, 256]
    dirDO = [34, 68, 136, 272]

    grid.move_count = 0
    for i in range(1, MAX_GRID_SIZE - 1):
        for j in range(1, MAX_GRID_SIZE - 1):
            if grid.grid[i, j] == 0:
                if (grid.grid[i - 1, j - 1] + grid.grid[i - 1, j] + grid.grid[i - 1, j + 1] + grid.grid[i, j - 1] +
                    grid.grid[i, j + 1] + grid.grid[i + 1, j - 1] + grid.grid[i + 1, j] + grid.grid[i + 1, j + 1]) != 0:
                    for direction in range(4):
                        if grid.grid[i + dirX[direction], j + dirY[direction]] != 0 or grid.grid[
                            i - dirX[direction], j - dirY[direction]] != 0:
                            tab = [1023] * 15
                            for k in range(-7, 8):
                                ii = i + k * dirX[direction]
                                jj = j + k * dirY[direction]
                                if 0 <= ii < MAX_GRID_SIZE and 0 <= jj < MAX_GRID_SIZE:
                                    tab[k + 7] = grid.grid[ii, jj]
                            for k in range(3, 8):
                                total = 0
                                if not (tab[k] & dirD[direction]):
                                    total += 1
                                if not (tab[k + 1] & dirDO[direction]):
                                    total += 1
                                if not (tab[k + 2] & dirDO[direction]):
                                    total += 1
                                if not (tab[k + 3] & dirDO[direction]):
                                    total += 1
                                if not (tab[k + 4] & dirO[direction]):
                                    total += 1
                                for kk in range(5):
                                    if k + kk != 7 and (tab[k + kk] & 1):
                                        total += 1
                                if total == 9:
                                    moveX = i
                                    moveY = j
                                    moveDirection = direction
                                    moveK = k - 3
                                    grid.priority[grid.move_count] = 1005
                                    for kk in range(3, 8):
                                        if kk == k and ((tab[k] & dirO[direction]) == dirO[direction] or (
                                                tab[k + 4] & dirD[direction]) == dirD[direction]):
                                            grid.priority[grid.move_count] = 1010
                                    if grid.priority[grid.move_count] == 1005:
                                        for kk in range(3, 8):
                                            if (tab[k - 1] & dirO[direction]) == dirO[direction] or (
                                                    tab[k - 2] & dirO[direction]) == dirO[direction] or (
                                                    tab[k - 3] & dirO[direction]) == dirO[direction] or (
                                                    tab[k + 5] & dirD[direction]) == dirD[direction] or (
                                                    tab[k + 6] & dirD[direction]) == dirD[direction] or (
                                                    tab[k + 7] & dirD[direction]) == dirD[direction]:
                                                grid.priority[grid.move_count] = 1000
                                    grid.moves[grid.move_count] = pack_move(moveX, moveY, moveDirection, moveK)
                                    grid.dominator[grid.move_count] = 999
                                    grid.move_count += 1
                                    if grid.move_count > MAX_HISTORY_SIZE:
                                        raise ValueError("Move table too small")
                                    if i in [1, MAX_GRID_SIZE - 1] or j in [1, MAX_GRID_SIZE - 1]:
                                        raise ValueError("Grid too small: move found on edge")
    update_dominator(grid)


def search_moves_optimized(grid_a, grid_b, played_move):
    dirX = [0, 1, 1, 1]
    dirY = [1, 1, 0, -1]
    dirD = [2, 4, 8, 16]
    dirO = [32, 64, 128, 256]
    dirDO = [34, 68, 136, 272]

    grid_b.move_count = 0
    for i in range(grid_a.move_count):
        moveX_p = unpack_x(grid_a.moves[i])
        moveY_p = unpack_y(grid_a.moves[i])
        moveDirection_p = unpack_direction(grid_a.moves[i])
        moveK_p = unpack_k(grid_a.moves[i])
        if grid_b.grid[moveX_p, moveY_p] == 0:
            total = 0
            priority = 0
            bad_move = 0
            for kk in range(-3, 8):
                ii = moveX_p + (moveK_p + kk - 4) * dirX[moveDirection_p]
                jj = moveY_p + (moveK_p + kk - 4) * dirY[moveDirection_p]
                if kk == 0 and not (grid_b.grid[ii, jj] & dirD[moveDirection_p]):
                    total += 1
                if kk == 1 and not (grid_b.grid[ii, jj] & dirDO[moveDirection_p]):
                    total += 1
                if kk == 2 and not (grid_b.grid[ii, jj] & dirDO[moveDirection_p]):
                    total += 1
                if kk == 3 and not (grid_b.grid[ii, jj] & dirDO[moveDirection_p]):
                    total += 1
                if kk == 4 and not (grid_b.grid[ii, jj] & dirO[moveDirection_p]):
                    total += 1
                if kk == 4 and (grid_b.grid[ii, jj] & dirD[moveDirection_p]) == dirD[moveDirection_p]:
                    priority = 1
                if kk == 0 and (grid_b.grid[ii, jj] & dirO[moveDirection_p]) == dirO[moveDirection_p]:
                    priority = 1
                if kk == -1 and (grid_b.grid[ii, jj] & dirO[moveDirection_p]) == dirO[moveDirection_p]:
                    bad_move = 1
                if kk == -2 and (grid_b.grid[ii, jj] & dirO[moveDirection_p]) == dirO[moveDirection_p]:
                    bad_move = 1
                if kk == -3 and (grid_b.grid[ii, jj] & dirO[moveDirection_p]) == dirO[moveDirection_p]:
                    bad_move = 1
                if kk == 5 and (grid_b.grid[ii, jj] & dirD[moveDirection_p]) == dirD[moveDirection_p]:
                    bad_move = 1
                if kk == 6 and (grid_b.grid[ii, jj] & dirD[moveDirection_p]) == dirD[moveDirection_p]:
                    bad_move = 1
                if kk == 7 and (grid_b.grid[ii, jj] & dirD[moveDirection_p]) == dirD[moveDirection_p]:
                    bad_move = 1
            if total == 5:
                grid_b.priority[grid_b.move_count] = 1005
                if priority > 0:
                    grid_b.priority[grid_b.move_count] = 1010
                if bad_move > 0 and grid_b.priority[grid_b.move_count] == 1005:
                    grid_b.priority[grid_b.move_count] = 1000
                grid_b.moves[grid_b.move_count] = pack_move(moveX_p, moveY_p, moveDirection_p, moveK_p)
                grid_b.dominator[grid_b.move_count] = 999
                grid_b.move_count += 1

    moveX = unpack_x(grid_a.moves[played_move])
    moveY = unpack_y(grid_a.moves[played_move])
    for i in range(moveX - 4, moveX + 5):
        for j in range(moveY - 4, moveY + 5):
            if grid_b.grid[i, j] == 0 and i > 0 and j > 0 and i < MAX_GRID_SIZE and j < MAX_GRID_SIZE:
                if grid_b.grid[i - 1, j - 1] + grid_b.grid[i - 1, j] + grid_b.grid[i - 1, j + 1] + grid_b.grid[
                    i, j - 1] + grid_b.grid[i, j + 1] + grid_b.grid[i + 1, j - 1] + grid_b.grid[i + 1, j] + grid_b.grid[
                    i + 1, j + 1] != 0:
                    for direction in range(4):
                        if grid_b.grid[i + dirX[direction], j + dirY[direction]] != 0 or grid_b.grid[
                            i - dirX[direction], j - dirY[direction]] != 0:
                            tab = [1023] * 15
                            for k in range(-7, 8):
                                ii = i + k * dirX[direction]
                                jj = j + k * dirY[direction]
                                if 0 <= ii < MAX_GRID_SIZE and 0 <= jj < MAX_GRID_SIZE:
                                    tab[k + 7] = grid_b.grid[ii, jj]
                            for k in range(3, 8):
                                total = 0
                                if not (tab[k] & dirD[direction]):
                                    total += 1
                                if not (tab[k + 1] & dirDO[direction]):
                                    total += 1
                                if not (tab[k + 2] & dirDO[direction]):
                                    total += 1
                                if not (tab[k + 3] & dirDO[direction]):
                                    total += 1
                                if not (tab[k + 4] & dirO[direction]):
                                    total += 1
                                for kk in range(5):
                                    if k + kk != 7 and (tab[k + kk] & 1):
                                        total += 1
                                if total == 9:
                                    res = 0
                                    for xx in range(grid_b.move_count):
                                        moveX = unpack_x(grid_b.moves[xx])
                                        moveY = unpack_y(grid_b.moves[xx])
                                        moveDirection = unpack_direction(grid_b.moves[xx])
                                        moveK = unpack_k(grid_b.moves[xx])
                                        if moveX == i and moveY == j and moveDirection == direction and moveK == k - 3:
                                            res = 1
                                    if res == 0:
                                        moveX = i
                                        moveY = j
                                        moveDirection = direction
                                        moveK = k - 3
                                        grid_b.priority[grid_b.move_count] = 1005
                                        for kk in range(3, 8):
                                            if kk == k and ((tab[k] & dirO[direction]) == dirO[direction] or (
                                                    tab[k + 4] & dirD[direction]) == dirD[direction]):
                                                grid_b.priority[grid_b.move_count] = 1010
                                        if grid_b.priority[grid_b.move_count] == 1005:
                                            for kk in range(3, 8):
                                                if (tab[k - 1] & dirO[direction]) == dirO[direction] or (
                                                        tab[k - 2] & dirO[direction]) == dirO[direction] or (
                                                        tab[k - 3] & dirO[direction]) == dirO[direction] or (
                                                        tab[k + 5] & dirD[direction]) == dirD[direction] or (
                                                        tab[k + 6] & dirD[direction]) == dirD[direction] or (
                                                        tab[k + 7] & dirD[direction]) == dirD[direction]:
                                                    grid_b.priority[grid_b.move_count] = 1000
                                        grid_b.moves[grid_b.move_count] = pack_move(moveX, moveY, moveDirection, moveK)
                                        grid_b.dominator[grid_b.move_count] = 999
                                        grid_b.move_count += 1
                                        if grid_b.move_count > MAX_HISTORY_SIZE:
                                            raise ValueError("Move table too small")
                                        if i in [1, MAX_GRID_SIZE - 1] or j in [1, MAX_GRID_SIZE - 1]:
                                            raise ValueError("Grid too small: move found on edge")
    update_dominator(grid_b)


def construct_game(max_grid, init_grid, level, file):
    node = init_grid.copy()
    for i in range(level):
        search_moves(node)
        j0 = 999
        for j in range(node.move_count):
            if node.moves[j] == max_grid.history[i]:
                j0 = j
        if j0 == 999:
            logging.error(f"Move from max_grid {i} not found. Something is wrong")
            file.write("BEST\n")
            display_game(max_grid, file)
            file.write("NODE\n")
            display_game(node, file)
            file.close()
            exit(1)
        play_move(node, node, j0)
    return node


def move_to_index(move):
    x = unpack_x(move)
    y = unpack_y(move)
    direction = unpack_direction(move)
    k = unpack_k(move)
    return x * MAX_GRID_SIZE * MAX_GRID_SIZE * MAX_GRID_SIZE + y * MAX_GRID_SIZE * MAX_GRID_SIZE + direction * MAX_GRID_SIZE + k

