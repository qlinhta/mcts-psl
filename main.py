import random
import argparse
import csv
from prettytable import PrettyTable
from nrpa import *
from colorama import Fore, Style, init
import colorlog
import logging

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


def main():
    parser = argparse.ArgumentParser(description='Morpion Solitaire with NRPA')
    parser.add_argument('--log', type=str, default='process.log', help='Path to log file')
    parser.add_argument('--result', type=str, default='results.txt', help='Path to result file')
    parser.add_argument('--iterations', type=int, default=100, help='Number of iterations in NRPA')
    parser.add_argument('--alpha', type=float, default=1.0, help='Alpha value for policy adaptation in NRPA')
    parser.add_argument('--data', type=str, default='data.csv', help='Path to save data for plotting')
    parser.add_argument('--level', type=int, help='Run for a single level')
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
