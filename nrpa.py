import time
from base import *
from colorama import Fore, Style
from prettytable import PrettyTable
from tqdm import tqdm

class Policy:
    def __init__(self):
        self.policy = np.zeros(MAX_GRID_SIZE * MAX_GRID_SIZE * 4)


def nrpa(level, node, strategy, log_file, iterations, alpha):
    if level == 0:
        return playout(node, strategy, log_file)
    else:
        best_grid = Grid()
        best_grid.move_history_count = 0
        start_time = time.time()
        bar = tqdm(range(iterations), desc=f"Level {level}", leave=False, postfix={"Moves": best_grid.move_history_count})
        for i in bar:
            result = nrpa(level - 1, node.copy(), strategy, log_file, iterations, alpha)
            if result.move_history_count >= best_grid.move_history_count:
                best_grid = result.copy()
                strategy = adapt(strategy, node, best_grid, log_file, alpha)
            bar.set_postfix({"Moves": best_grid.move_history_count})
        total_time_elapsed = time.time() - start_time
        logging.info(
            Fore.GREEN +
            f"COMPLETED LEVEL {level} // TOTAL MOVES: {best_grid.move_history_count} // TIME: {total_time_elapsed:.2f}s // SIGNATURE: {sign_grid(best_grid):010d} \n"
            + Style.RESET_ALL
        )
        return best_grid


def playout(grid, policy, log_file):
    current_grid = grid.copy()
    temp_grid = Grid()
    search_moves(current_grid)

    while current_grid.move_count > 0:
        move = select_move(current_grid, policy, log_file)
        play_move(current_grid, temp_grid, move)
        search_moves_optimized(current_grid, temp_grid, move)

        if temp_grid.move_count > 0:
            move = select_move(temp_grid, policy, log_file)
            play_move(temp_grid, current_grid, move)
            search_moves_optimized(temp_grid, current_grid, move)
        else:
            current_grid = temp_grid.copy()

    return current_grid


def select_move(grid, strategy, log_file):
    total_weight = 0.0
    generate(grid, log_file)

    for i in range(grid.move_count):
        weight = np.exp(strategy.policy[grid.code[i]])
        if grid.priority[i] == 1000:
            total_weight += weight / 1000
        elif grid.priority[i] == 1005:
            total_weight += weight / 34
        else:
            total_weight += weight

    rand_num = np.random.rand()
    cumulative_prob = 0.0

    for i in range(grid.move_count):
        weight = np.exp(strategy.policy[grid.code[i]])
        if grid.priority[i] == 1000:
            cumulative_prob += weight / 1000 / total_weight
        elif grid.priority[i] == 1005:
            cumulative_prob += weight / 34 / total_weight
        else:
            cumulative_prob += weight / total_weight

        if cumulative_prob >= rand_num:
            return i

    logging.error(f"Problem in move selection. Random number: {rand_num:.6f}")
    for i in range(grid.move_count):
        logging.error(
            f"Move {i:02d} Priority: {grid.priority[i]} Code: {grid.code[i]} Weight: {np.exp(strategy.policy[grid.code[i]]) / total_weight:.6f}")
    exit(1)


def adapt(strategy, root, best_grid, log_file, alpha):
    start_time = time.time()
    new_strategy = Policy()
    new_strategy.policy = strategy.policy.copy()
    node = root.copy()
    search_moves(node)

    for i in range(node.move_history_count, best_grid.move_history_count):
        generate(node, log_file)
        total_weight = 0.0
        target_move_index = -1

        for j in range(node.move_count):
            total_weight += np.exp(strategy.policy[node.code[j]])
            if node.moves[j] == best_grid.history[i]:
                target_move_index = j
                new_strategy.policy[node.code[j]] += alpha

        if target_move_index == -1:
            logging.error(f"Move from best grid {i} not found. Something is wrong")
            log_file.write(f"Move from best grid {i} not found. Something is wrong\n")
            log_file.write("BEST\n")
            display_game(best_grid, log_file)
            log_file.write("NODE\n")
            display_game(node, log_file)
            log_file.close()
            exit(1)

        for j in range(node.move_count):
            new_strategy.policy[node.code[j]] -= alpha * np.exp(strategy.policy[node.code[j]]) / total_weight
        play_move(node, node, target_move_index)
        search_moves(node)
    logging.info(
        f"ADAPTED STRATEGY # ALPHA: {alpha} # ADAPTED MOVES: {node.move_history_count - root.move_history_count} "
        f"# PREV.SIG: {sign_grid(root):010d} # NEW.SIG: {sign_grid(node):010d} # TIME: {time.time() - start_time:.2f}s")
    return new_strategy


def generate(grid, log_file):
    dirX = [0, 1, 1, 1]
    dirY = [1, 1, 0, -1]
    dirD = [2, 4, 8, 16]
    dirO = [32, 64, 128, 256]
    dirDO = [34, 68, 136, 272]

    for i in range(grid.move_count):
        move_x = unpack_x(grid.moves[i])
        move_y = unpack_y(grid.moves[i])
        move_d = unpack_direction(grid.moves[i])
        move_k = unpack_k(grid.moves[i])

        end_x1 = move_x + move_k * dirX[move_d]
        end_y1 = move_y + move_k * dirY[move_d]
        start_x2 = move_x + (move_k - 4) * dirX[move_d]
        start_y2 = move_y + (move_k - 4) * dirY[move_d]

        n1 = (MAX_GRID_SIZE - 1) * end_y1 + end_x1
        n2 = (MAX_GRID_SIZE - 1) * start_y2 + start_x2

        if n1 < n2:
            grid_code = 4 * n1
            if end_x1 < start_x2:
                grid_code += 0
            elif end_x1 == start_x2:
                grid_code += 1
            else:
                if end_y1 > start_y2:
                    grid_code += 2
                else:
                    grid_code += 3
        else:
            grid_code = 4 * n2
            if start_x2 < end_x1:
                grid_code += 0
            elif start_x2 == end_x1:
                grid_code += 1
            else:
                if start_y2 > end_y1:
                    grid_code += 2
                else:
                    grid_code += 3

        for direction in range(4):
            if move_d == direction:
                if (grid.grid[end_y1, end_x1] & dirD[direction]) or (grid.grid[start_y2, start_x2] & dirD[direction]):
                    grid_code += dirDO[direction]
                if (grid.grid[end_y1, end_x1] & dirO[direction]) or (grid.grid[start_y2, start_x2] & dirO[direction]):
                    grid_code += dirD[direction]
        grid.code[i] = grid_code


def display_policy(strategy, log_file):
    log_file.write("STRATEGY\n")
    for index in range(MAX_GRID_SIZE * MAX_GRID_SIZE * 4):
        if strategy.policy[index] != 0:
            log_file.write(
                f"exp(policy)={np.exp(strategy.policy[index])} policy={strategy.policy[index]} code={index:05d}\n")


def sign_grid(grid):
    signature = 0
    for i in range(MAX_GRID_SIZE):
        for j in range(MAX_GRID_SIZE):
            signature += grid.grid[i, j] * i * j
    return signature
