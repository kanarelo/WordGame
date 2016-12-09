#!/usr/bin/env python
import json
import random

from game.utils import read_file_lines
from game.types import Game, colored

def play_game(words_file):
    words = read_file_lines(words_file)
    
    game = Game()

    play_another_game = True
    while play_another_game:
        game.play_game(words)

        play = raw_input("Play another game? [y/n] ")
        if play.strip().startswith("n"):
            play_another_game = False
    else:
        message = ""
        if game.get_winner():
            if game.get_winner().is_ai_player:
                message = colored("You suck!", "red")
            else:
                message = colored("You rock!", "green")

        print "\nBye bye!" , message

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    with open('words.txt', 'r') as words_file:
        play_game(words_file)