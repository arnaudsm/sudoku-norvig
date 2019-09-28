# Sudoku Solver

## Importing Solver Library
from sudoku import *

## Solving different sudokus from files
solve_all(from_file("data/Sudoku_Easy50.txt"), "easy50", None)
solve_all(from_file("data/Sudoku_top95.txt"), "top95", None)
solve_all(from_file("data/Sudoku_hardest.txt"), "hardest", None)

## Solve 99 random sudokus
solve_all([random_puzzle() for _ in range(100)], "aléatoires", 0.01)