import numpy as np
from base import *
import logging
import random
import colorlog
from colorama import Fore, Style
import time


class NMCS:
    def __init__(self, level, max_running_time=2):
        self.level = level
        self.max_running_time = max_running_time

    def search(self, grid):
        return self.nmcs(grid, self.level)

    def nmcs(self, grid, level):
        if level == 0:
            return self.playout(grid)
        else:
            best_grid = Grid()
            best_grid.move_history_count = 0
            start_time = time.time()
            search_moves(grid)
            for i in range(grid.move_count):
                new_grid = grid.copy()
                play_move(grid, new_grid, i)
                start_time = time.time()
                result_grid = self.nmcs(new_grid, level - 1)
                if result_grid.move_history_count > best_grid.move_history_count:
                    best_grid = result_grid.copy()
            logging.info(Fore.GREEN +
                         f"NMCS: COMPLETED LEVEL {level} // TOTAL MOVES: {best_grid.move_history_count} // TIME: {time.time() - start_time:.2f}s // SIGNATURE: {sign_grid(best_grid):010d}"
                         + Style.RESET_ALL)
            return best_grid

    def playout(self, grid):
        current_grid = grid.copy()
        temp_grid = Grid()
        search_moves(current_grid)
        while current_grid.move_count > 0:
            start_time = time.time()
            move = np.random.choice(current_grid.move_count)
            play_move(current_grid, temp_grid, move)
            search_moves_optimized(current_grid, temp_grid, move)
            if (time.time() - start_time) > self.max_running_time:
                break
            if temp_grid.move_count > 0:
                move = np.random.choice(temp_grid.move_count)
                play_move(temp_grid, current_grid, move)
                search_moves_optimized(temp_grid, current_grid, move)
                if (time.time() - start_time) > self.max_running_time:
                    break
            else:
                current_grid = temp_grid.copy()
        return current_grid


def run_nmcs_for_level(level, log_file_path, seed):
    with open(log_file_path, "w") as log_file:
        initial_grid = Grid()
        best_grid = Grid()

        random.seed(seed)
        logging.info(f"Seed: {seed}")

        initialize_game(initial_grid)
        current_node = initial_grid.copy()
        search_moves(current_node)
        logging.info(Fore.LIGHTYELLOW_EX + f"Starting NMCS with level={level}" + Style.RESET_ALL)

        nmcs_solver = NMCS(level)
        best_grid = nmcs_solver.search(current_node)

        display_game(best_grid, log_file)

        return {
            'level': level,
            'moves': best_grid.move_history_count,
            'signature': sign_grid(best_grid),
            'time': time.time()
        }


def sign_grid(grid):
    signature = 0
    for i in range(MAX_GRID_SIZE):
        for j in range(MAX_GRID_SIZE):
            signature += grid.grid[i, j] * i * j
    return signature
