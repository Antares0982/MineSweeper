#!/usr/bin/python3

from minesweep import MineSweepGame


def main():
    game = MineSweepGame()
    game.start(10, 10, 20)
    game.run()


if __name__ == "__main__":
    main()
