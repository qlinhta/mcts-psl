## MORPION SOLITAIRE WITH NESTED ROLLOUT POLICY ADAPTATION

This project implements the Nested Rollout Policy Adaptation (NRPA) algorithm to solve the Morpion Solitaire game. The algorithm iteratively improves the strategy used to explore the game tree, leveraging Monte Carlo tree search (MCTS) techniques and dynamic policy adaptation.

### Setup and Installation

1. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. Clone this repository to local machine:
    ```bash
    https://github.com/qlinhta/mcts-psl.git
    cd mcts-psl
    ```

### Running the Code

To run the NRPA algorithm, use the following command:

```bash
python3 ./main.py --iterations 100 --level 2 --alpha 1 --log ./logs/nrpa_100_2_1.log --result ./logs/nrpa_100_2_1.txt --data ./logs/nrpa_100_2_1.csv --seed 1
```

#### Arguments

- `--iterations`: Number of iterations for the NRPA algorithm.
- `--level`: Nesting level for the NRPA algorithm.
- `--alpha`: Learning rate for policy adaptation.
- `--log`: Path to the log file to store detailed execution logs.
- `--result`: Path to the result file to store results and list of moves.
- `--data`: Path to the CSV file to store detailed results in CSV format.
- `--seed`: Seed value for random number generator to ensure reproducibility.

### Example

To run the algorithm with 100 iterations, nesting level 2, and a learning rate of 1.0, and store the logs, results, and data in the specified files, use the following command:

```bash
python3 ./main.py --iterations 100 --level 2 --alpha 1 --log ./logs/nrpa_100_2_1.log --result ./logs/nrpa_100_2_1.txt --data ./logs/nrpa_100_2_1.csv --seed 1
```

### Results

The results of the experiments, including the number of moves achieved and the execution time, are stored in the specified result and data files. Refer to these files for detailed information on the performance of the NRPA algorithm for different nesting levels and iteration counts.
