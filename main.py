import random
import argparse
import csv
from prettytable import PrettyTable
from nrpa import *
from colorama import Fore, Style, init

init()


def setup_logging(log_file):
    log_colors = {
        'DEBUG': 'reset',
        'INFO': 'bold_white',
        'WARNING': 'bold_yellow',
        'ERROR': 'bold_red',
        'CRITICAL': 'bold_red,bg_white',
    }

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        log_colors=log_colors
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])


def run_nrpa_for_level(level, iterations, alpha, log_file_path, seed):
    with open(log_file_path, "w") as log_file:
        initial_grid = Grid()
        best_grid = Grid()
        strategy = Policy()

        random.seed(seed)
        logging.info(f"Seed: {seed}")

        initialize_game(initial_grid)
        current_node = initial_grid.copy()
        search_moves(current_node)
        logging.info(
            Fore.LIGHTYELLOW_EX + f"Starting NRPA with level={level}, iterations={iterations}, alpha={alpha}" + Style.RESET_ALL)
        start_time = time.time()

        best_grid.move_history_count = 0
        move_counter = 0

        while current_node.move_count > 0:
            best_grid = NRPA(level, current_node, strategy, log_file, iterations, alpha)
            log_file.write(f"End recursion level {level}, iterations={iterations}\n")
            current_node = construct_game(best_grid, initial_grid, best_grid.move_history_count, log_file)
            search_moves(current_node)

            move_counter += 1
            logging.info(
                f"Move {move_counter} completed ## Total moves: {best_grid.move_history_count} ## Time elapsed: {time.time() - start_time:.2f}s")

            log_file.write("Best Grid\n")
            display_game(best_grid, log_file)
            NRPA_display_policy(strategy, log_file)

        end_time = time.time()
        execution_time = end_time - start_time

        display_game(best_grid, log_file)
        NRPA_display_policy(strategy, log_file)

        return {
            'level': level,
            'moves': best_grid.move_history_count,
            'signature': sign_grid(best_grid),
            'time': execution_time
        }


def main():
    parser = argparse.ArgumentParser(description='Morpion Solitaire with NRPA')
    parser.add_argument('--log', type=str, default='process.log', help='Path to log file')
    parser.add_argument('--result', type=str, default='results.txt', help='Path to result file')
    parser.add_argument('--iterations', type=int, default=100, help='Number of iterations in NRPA')
    parser.add_argument('--alpha', type=float, default=1.0, help='Alpha value for policy adaptation')
    parser.add_argument('--data', type=str, default='data.csv', help='Path to save data for plotting')
    parser.add_argument('--level', type=int, help='Run NRPA for a single level')
    parser.add_argument('--seed', type=int, default=1, help='Random seed for reproducibility')

    args = parser.parse_args()

    setup_logging(args.log)

    iterations = args.iterations
    alpha = args.alpha
    seed = args.seed
    results = []

    if args.level:
        result = run_nrpa_for_level(args.level, iterations, alpha, args.result, seed)
        results.append(result)
    else:
        for level in range(1, 6):
            result = run_nrpa_for_level(level, iterations, alpha, args.result, seed)
            results.append(result)

    with open(args.data, 'w', newline='') as data_file:
        writer = csv.DictWriter(data_file, fieldnames=['level', 'moves', 'signature', 'time'])
        writer.writeheader()
        writer.writerows(results)

    logging.info(f"Results saved to {args.data}")

    table = PrettyTable()
    table.field_names = ["Seed", "Level", "Moves", "Signature", "Time (s)", "Time per iteration (s)",
                         "Time per move (s)"]
    for result in results:
        table.add_row([
            seed,
            result['level'],
            result['moves'],
            result['signature'],
            result['time'],
            result['time'] / iterations,
            result['time'] / result['moves']
        ])

    logging.info("\n" + table.get_string())


if __name__ == "__main__":
    main()
