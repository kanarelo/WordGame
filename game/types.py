# -*- coding: utf-8 -*-

import json
import random
from .utils import *

try:
    from termcolor import colored
except ImportError:
    def colored(string, colour):
        return string
try:
    from tqdm import trange
except ImportError:
    def trange(number, desc="", *args, **kwargs):
        print desc + "..."
        return xrange(number)

def find_parent_node(node, subword, current_index=0):
    if not node:
        return

    is_complete_word = False
    if not subword:
        return node, is_complete_word

    subword = subword.lower()
    length_of_subword = len(subword)
    current_letter = subword[current_index]
    
    search_node = node.children.get(current_letter)

    if current_index == (length_of_subword - 1): 
        is_complete_word = (subword in node.complete_words)
    else:
        if search_node is not None:
            search_node, is_complete_word = find_parent_node(
                search_node, subword, current_index=(current_index + 1))

    return search_node, is_complete_word
 
def add_word_to_node(node, word, current_index=0):
    if not word:
        return node

    word = word.lower()
    length_of_word = len(word)
    current_letter = word[current_index]
    
    if (current_index == (length_of_word - 1)):
        node.complete_words.add(word)
        return node
    else:
        search_node = node.children.get(current_letter)
        if search_node is None:
            search_node = Node(parent=node, letter=current_letter)
            node.children[current_letter] = search_node

        return add_word_to_node(
            search_node, word, current_index=(current_index + 1))

def all_possible_words(node_tuple, level=2):
    _letter, node = node_tuple
    all_words = []

    if not node.children:
        all_words += node.complete_words
    else:
        for _node_tuple in node.children.iteritems():
            all_words += all_possible_words(_node_tuple)
    
    return flatten_array(all_words)

class Node(object):
    def __init__(self, parent=None, letter=None, *args, **kwargs):

        self.parent = parent
        self.letter = letter
        self.children = dict()
        self.complete_words = set()

    def add_word(self, word):
        return add_word_to_node(self, word)

    def is_complete_word(self, word):
        return (word in self.complete_words)

    def __repr__(self):
        return """
Node: (%s)[letter]
Children: %s
Complete Words: %s
Has parent: %s
        """ % (
            self.letter, 
            self.children,# indent=2, sort_keys=True),
            self.complete_words,
            self.parent is not None
        )

    def __str__(self, level=0):
        ret = "\t" * level + self.__repr__() + "\n"

        # for key, child in self.children.items():
        #     ret += child.__str__(level=1)

        return ret

class Dictionary(object):
    def __init__(self, *args, **kwargs):
        self.root_node = Node()

    def add_words(self, words):
        return map(self.__add_word, words)

    def __add_word(self, word):
        if not word:
            return

        return self.root_node.add_word(word)

    def get_root_node(self):
        return self.root_node

    def find_parent_node(self, subword, node=None):
        return find_parent_node(
            node and node or self.root_node, subword)

    def nearest_node_to_subword(self, subword, node=None):
        node, is_complete_word = self.find_parent_node(subword, node=node)

        if node is not None and node.is_complete_word(subword):
            return node, True

        try:
            # choices = {}
            # for k, v in node.children.items(): 
            #     if not v.is_complete_word(subword + k):
            #         choices[k] = v
            random_choice = random.choice(node.children.values())
            return random_choice, False
        except (IndexError, AttributeError):
            return None, False

    def next_possible_move(self, subword, node=None):
        node, is_complete_word = self.nearest_node_to_subword(subword, node=node)

        if node is not None:
            return node.letter, is_complete_word
        else:
            return node, is_complete_word

    def next_possible_word_from_subword(self, subword, node=None):
        next_possible_move, last_move = self.next_possible_move(subword, node=node)

        if next_possible_move and not last_move:
            return subword + next_possible_move

class Player(object):
    def __init__(self, player_no, is_ai_player=False):
        self.player_no = player_no
        self.is_ai_player = is_ai_player

    def __eq__(self, other):
        if type(other) == int:
            return other == self.player_no
        else:
            return other.player_no == other.player_no 

    def __str__(self):
        return "AI" if self.is_ai_player else "You"

class Game(object):
    def __init__(self, no_of_players=2):
        self.winner = None
        self.no_of_players = no_of_players
        self.cumulative_word = ""
        self.current_node = None
        self.game_over = False
        self.last_move = None
        self.last_player = None
        self.game_root_node = None
        self.setup_complete = False
        self.dictionary = Dictionary()
    
    def add_words(self, words):
        self.dictionary.add_words(words)

    def get_players(self):
        return self.players

    def setup_players(self):
        players = range(self.no_of_players or 0)

        if players:
            ai_player = random.choice(players)

            self.players = [
                Player(player, is_ai_player=(ai_player == player))
                for player in players ]
        
    def get_first_player(self):
        self.setup_players()

        print colored("""
+================================================================+
| Welcome to the word game!                                      |
|                                                                |
| This is a 2-player word game, in which the players take        |
| turns saying a letter. If a player says a letter that ends     |
| a word, that player loses. Similarly, if a player says a       |
| letter from which no word can be spelled, that player loses.   |
|                                                                |
| For example: if the letters so far are "COR", then the next    |
| player could not say "E" (spelling "CORE") or "Z" ("CORZ"      |
| is not the beginning to any words) without losing.             |
|                                                                |
+================================================================+
        """, 
        "blue")

        print colored("\n%s start%s\n""" % (
            self.players[0], 
            "s" if self.players[0].is_ai_player else ""), "red")

        return self.players[0]

    def get_winner_message(self):
        if self.winner is not None:
            if not self.winner.is_ai_player:
                return colored("I yield, You win!\n", "green")
 
            return colored("%s wins!" % self.winner, "red")

    def get_winner(self):
        return self.winner

    def is_game_over(self):
        return self.game_over

    def end_game(self, winner=None):
        if winner is None:
            winner = self.last_player

        self.current_node = None
        self.winner = winner
        self.game_over = True

    def setup_game(self, words):
        no_of_words = len(words)
        thousandths = no_of_words / 1000

        for i in trange(thousandths, desc="Loading words...", 
            ascii=True, unit="'000 words", ncols=75):
            words_to_add = words[(1000 * i):(1000 * (i + 1))]
            self.add_words(words_to_add)
            del words_to_add
        else:
            remaining_words = no_of_words % 1000
            words_to_add = words[-remaining_words:]
            self.add_words(words_to_add)
            del words_to_add
        
        print "\nLoading complete..."

        self.first_player = self.get_first_player()
        self.setup_complete = True

    def clear_game(self):
        self.current_node = None,
        self.game_over = False
        self.cumulative_word = ""
        self.game_root_node = None

        self.first_player = self.get_first_player()

    def move_is_damned(self, move):
        nearest_node, last_move = \
            self.dictionary.nearest_node_to_subword(
                (self.cumulative_word + move))

        if nearest_node is None:
            return True
        
        if not nearest_node.children:
            return True

        return False

    def make_move(self, player):
        if player.is_ai_player:
            move, self.last_move = self.dictionary\
                .next_possible_move(self.cumulative_word)
        else:
            move = None
            while not move:
                if not self.cumulative_word:
                    message = "Please enter any letter to start: "
                else:
                    message = "Enter next word: "

                move = raw_input(message.upper())
                move = move[0] if move else move

                if not move:
                    print "Please enter a value\n"

                if move.isdigit():
                    print "Invalid value, try again\n"
        
        node = None

        is_complete_word = False
        if move is not None:
            node, is_complete_word = self.dictionary.find_parent_node(
                self.cumulative_word + move)

            if not self.move_is_damned(move):
                print colored("⬤  %s(%s)" % (str(player), player.player_no+1),  
                        "green" if not player.is_ai_player else "red"), \
                    " %s word: %s" % (
                        "Incomplete" if not is_complete_word else "Complete", 
                        self.cumulative_word.strip()), " + ", \
                    colored(move.lower(), "blue"), " = ", \
                    self.cumulative_word.strip() + move

                self.cumulative_word += move

                if node is not None and is_complete_word:
                    self.end_game()
                else:
                    self.last_player = player #set the last player
            else:
                print colored("⬤  %s(%s)" % (str(player), player.player_no+1),
                    "green" if not player.is_ai_player else "red"), \
                    " Final Word: %s" % (self.cumulative_word.strip() + move.lower())
                if node is not None:
                    if node.complete_words:
                        print "\nI bet you we thinking either: ", ', '.join(node.complete_words), "lol"

                else:
                    if player.is_ai_player:
                        print ("\nYour word; '%s%s', is not in the dictionary!\n" % 
                            (self.cumulative_word.lower(), move.lower()))

                self.end_game()
                is_complete_word = True
                
        return node, is_complete_word

    def play_game(self, words):
        if not self.setup_complete:
            self.setup_game(words)
        else:
            self.clear_game()

        def print_game_over():
            print "Game Over!\n", self.get_winner_message()
            print "." * 65
            print

        move_no = 1
        while not self.is_game_over():
            for i, player in enumerate(self.get_players()):
                self.current_node, is_complete_word = self.make_move(player)

                if move_no == 1:
                     self.game_root_node = self.current_node

                if self.is_game_over():
                    print_game_over()
                    return

                move_no += 1
            else:
                print "." * 65
                print
        else:
            print_game_over()
