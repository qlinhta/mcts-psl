import colorlog
from base import *
import numpy as np
import logging
import time


class Policy:
    def __init__(self):
        self.policy = np.zeros(MAX_GRID_SIZE * MAX_GRID_SIZE * 4)


def NRPA(level, node, strategy, log_file, iterations, alpha):
    if level == 0:
        return NRPA_playout(node, strategy, log_file)
    else:
        best_grid = Grid()
        best_grid.move_history_count = 0
        start_time = time.time()

        for i in range(iterations):
            iter_start_time = time.time()
            result = NRPA(level - 1, node, strategy, log_file, iterations, alpha)
            iter_time_elapsed = time.time() - iter_start_time

            if result.move_history_count >= best_grid.move_history_count:
                best_grid = result.copy()
                strategy = NRPA_adapt(strategy, node, best_grid, log_file, alpha)

            """logging.info(
                f"Iteration {i + 1}/{iterations} | Level: {level} | Moves: {best_grid.move_history_count} | "
                f"Iteration Time: {iter_time_elapsed:.2f}s | Total Time: {time.time() - start_time:.2f}s | "
                f"% Complete: {(i + 1) / iterations * 100:.2f}%")"""

        total_time_elapsed = time.time() - start_time
        logger = colorlog.getLogger()
        logger.info(
            f"COMPLETED LEVEL {level} # TOTAL MOVES: {best_grid.move_history_count} # SIGNATURE: {sign_grid(best_grid):010d} | "
            f"Total Time: {total_time_elapsed:.2f}s",
            extra={'color': 'cyan'})
        return best_grid


def NRPA_playout(grid, policy, log_file):
    current_grid = grid.copy()
    temp_grid = Grid()
    search_moves(current_grid)
    move_counter = 0

    while current_grid.move_count > 0:
        move = NRPA_select_move(current_grid, policy, log_file)
        move_counter += 1
        play_move(current_grid, temp_grid, move)
        search_moves_optimized(current_grid, temp_grid, move)

        if temp_grid.move_count > 0:
            move = NRPA_select_move(temp_grid, policy, log_file)
            move_counter += 1
            play_move(temp_grid, current_grid, move)
            search_moves_optimized(temp_grid, current_grid, move)
        else:
            current_grid = temp_grid.copy()

    return current_grid


def NRPA_select_move(grid, strategy, log_file):
    total_weight = 0.0
    NRPA_generate_code(grid, log_file)

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


def NRPA_adapt(strategy, root, best_grid, log_file, alpha):
    start_time = time.time()
    new_strategy = Policy()
    new_strategy.policy = strategy.policy.copy()
    node = root.copy()
    search_moves(node)

    for i in range(node.move_history_count, best_grid.move_history_count):
        NRPA_generate_code(node, log_file)
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
    logger = colorlog.getLogger()
    logger.info(
        f"ADAPTED STRATEGY # ALPHA: {alpha} # ADAPTED MOVES: {node.move_history_count - root.move_history_count} "
        f"# PREV.SIG: {sign_grid(root):010d} # NEW.SIG: {sign_grid(node):010d} # TIME: {time.time() - start_time:.2f}s",
        extra={'color': 'green'})
    return new_strategy


def NRPA_generate_code(grid, log_file):
    directions_x = [0, 1, 1, 1]
    directions_y = [1, 1, 0, -1]
    directions_d = [2, 4, 8, 16]
    directions_o = [32, 64, 128, 256]
    directions_do = [34, 68, 136, 272]

    for i in range(grid.move_count):
        move_x = unpack_x(grid.moves[i])
        move_y = unpack_y(grid.moves[i])
        move_d = unpack_direction(grid.moves[i])
        move_k = unpack_k(grid.moves[i])

        end_x1 = move_x + move_k * directions_x[move_d]
        end_y1 = move_y + move_k * directions_y[move_d]
        start_x2 = move_x + (move_k - 4) * directions_x[move_d]
        start_y2 = move_y + (move_k - 4) * directions_y[move_d]

        n1 = (MAX_GRID_SIZE - 1) * end_y1 + end_x1
        n2 = (MAX_GRID_SIZE - 1) * start_y2 + start_x2

        if n1 < n2:
            grid_code = 4 * n1 + 0 if end_x1 < start_x2 else 1 if end_x1 == start_x2 else 2 if end_y1 > start_y2 else 3
        else:
            grid_code = 4 * n2 + 0 if start_x2 < end_x1 else 1 if start_x2 == end_x1 else 2 if start_y2 > end_y1 else 3

        grid.code[i] = grid_code


def NRPA_display_policy(strategy, log_file):
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
