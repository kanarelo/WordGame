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
 
def add_word_to_node(node, word, current_index=0, make_lower=True):
    if not word:
        return node

    node.word_count += 1
    
    if make_lower:
        word = word.lower()

    length_of_word = len(word)
    current_letter = word[current_index]
    
    if (current_index == (length_of_word - 1)):
        n = Node(parent=node, letter=current_letter)
        node.children[current_letter] = n

        n.add_complete_words_list(word)
        return n
    else:
        search_node = node.children.get(current_letter)
        if search_node is None:
            search_node = Node(parent=node, letter=current_letter)
            node.children[current_letter] = search_node

        return add_word_to_node(
            search_node, word, 
            current_index=(current_index + 1))

def search_for_parent_node(node, subword, current_index=0, make_lower=True):
    is_complete_word = False

    if not node:
        return

    if not subword:
        return node, is_complete_word

    if make_lower:
        subword = subword.lower()
    
    length_of_subword = len(subword)
    current_letter = subword[current_index]

    search_node = node.children.get(current_letter)
    if current_index == (length_of_subword - 1): 
        is_complete_word = node.is_complete_word(subword)
    else:
        if search_node is not None:
            search_node, is_complete_word = search_for_parent_node(
                search_node, subword, current_index=(current_index + 1))

    return search_node, is_complete_word

def all_possible_words_after_node(node, level=0, end=2):
    all_words = []

    if not node.children:
        all_words += node.get_complete_words()
    else:
        for (_, child_node) in node.children.iteritems():
            all_words += all_possible_words_after_node(
                child_node, level=(level+1))
    
    return flatten_list(all_words)

class Node(object):
    def __init__(self, parent=None, letter=None, *args, **kwargs):
        self.parent = parent
        self.letter = letter
        self.children = dict()
        self.complete_words = set()
        self.odd_length_words = set()
        self.even_length_words = set()
        self.word_count = 0

    def add_word(self, word):
        return add_word_to_node(self, word)

    def is_complete_word(self, word):
        return (word in self.complete_words)

    def add_complete_words_list(self, word):
        if is_even(len(word)):
            self.even_length_words.add(word)
        else:
            self.odd_length_words.add(word)

        return self.complete_words.add(word)

    def get_complete_words(self):
        return self.complete_words

    def __repr__(self):
        return  self.letter or ''

    def __str__(self, level=0):
        return str(repr(self))

class Dictionary(object):
    def __init__(self, *args, **kwargs):
        self.root_node = Node()

    def add_words(self, words):
        no_of_words = len(words)
        thousandths = no_of_words / 1000
        w = []

        for i in trange(thousandths, desc="Loading words...", 
                ascii=True, unit="'000 words", ncols=75):
            w += map(self.__add_word, words[(1000 * i):(1000 * (i + 1))])
        else:
            remaining_words = no_of_words % 1000
            w += map(self.__add_word, words[-remaining_words:])

        return w

    def __add_word(self, word):
        if not word:
            return

        parent_node = self.root_node.add_word(word)
        return parent_node

    def get_root_node(self):
        return self.root_node

    def search_for_parent_node(self, subword, node=None):
        (node, is_complete_word) = \
            search_for_parent_node(
                node and node or self.root_node, subword)

        if node is not None:
            return (node, is_complete_word)
        else:
            return (None, False)

def Player(game, player_no, is_ai_player=False):
    class HumanPlayer(object):
        def __init__(self):
            self.game = game
            self.player_no = player_no

            self.is_ai_player = is_ai_player
            self.is_first_player = (player_no == 0)
            self.is_second_player = (player_no == 1)

        def __eq__(self, other):
            if type(other) == int:
                return (other == self.player_no)
            else:
                return (other.player_no == self.player_no)

        def __str__(self):
            return "AI" if self.is_ai_player else "You"

        def make_move(self):
            move = None

            while not move:
                if not game.cumulative_word:
                    message = "\nPlease enter any letter to Start: "
                else:
                    message = "\nEnter Next Word: "
                    
                move = raw_input(message)
                if move:
                    move = move[0]
                else:
                    print "\nPlease enter a value\n"
                    move = ''

                if not move.isalpha():
                    print "\nInvalid value, try again\n"
                    move = ''

            return move.lower()

    #------------------
    class AIPlayer(HumanPlayer):
        def __init__(self):
            self.winning_moves = {}

            super(AIPlayer, self).__init__()

        def populate_winning_moves(self, 
                node, move_no=0, winning_moves={}):

            def find_winning_moves(n):
                if n.children and not n.complete_words:
                    #reject nodes that dont have grandchildren. 
                    #We want to see one step ahead
                    winning_moves[n] = {}
                    
                    self.populate_winning_moves(
                        n,
                        move_no=(move_no + 1), 
                        winning_moves=winning_moves[n])

                    if winning_moves[n] == {}:
                        del winning_moves[n]

                elif n.complete_words:
                    if (self.is_first_player and n.even_length_words) or \
                       (self.is_second_player and n.odd_length_words):
                        winning_moves[n] = n

            map(find_winning_moves, node.children.values())

        def make_random_move(self, node):
            return node.children and \
                random.choice(node.children.values()) or None

        def choose_path_with_most_wins(self, forward_moves): 
            return random.choice(forward_moves)
        
        def make_educated_forward_move(self, node):
            self.winning_moves = {}
            self.populate_winning_moves(
                node, 
                move_no=self.game.move_no, 
                winning_moves=self.winning_moves)
            
            if self.winning_moves:
                return self.choose_path_with_most_wins(
                    self.winning_moves.keys()) 

        def make_move(self):
            subword = self.game.cumulative_word
            length_of_subword = len(subword)

            if self.game.current_node:
                node = self.game.current_node
                is_last_letter_in_word = node.is_complete_word(subword)
            else:
                node = self.game.dictionary.root_node
                is_last_letter_in_word = False
            
            if node and node.children or not is_last_letter_in_word:
                if len(node.children) == 1:
                    choice = node.children.values()[0]
                else:
                    choice = self.make_educated_forward_move(node)
                
                if choice is not None:
                    return choice.letter

    return (AIPlayer() if (is_ai_player) else HumanPlayer())

class Game(object):
    def __init__(self, no_of_players=2):
        self.cumulative_word = ""
        self.current_node = None
        self.dictionary = Dictionary()
        self.game_over = False
        self.game_root_node = None
        self.last_player = None
        self.move_no = 1
        self.no_of_players = no_of_players
        self.previous_player = None
        self.setup_complete = False
        self.winner = None
    
    def get_players(self):
        return self.players

    def setup_players(self):
        players = range(self.no_of_players or 0)

        if players:
            ai_player = random.choice(players)

            self.players = [
                Player(self, player_no,
                    is_ai_player=(ai_player == player_no))
                        for player_no in players ]

    def get_first_player(self):
        self.setup_players()

        print_game_message()

        print colored("\n%s start%s\n""" % (
            self.players[0], 
            "s" if self.players[0].is_ai_player else ""), 
            "red" if self.players[0].is_ai_player else "green")

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

    def end_game(self, player, move, node, winner=None):
        if winner is None:
            winner = self.last_player

        self.current_node = None
        self.winner = winner
        self.game_over = True

        self.concede_defeat(player, move, node)

    def setup_game(self, words):
        self.dictionary.add_words(words)
        print "\nLoading complete..."

        self.first_player = self.get_first_player()
        self.setup_complete = True

    def clear_game(self):
        self.current_node = None
        self.game_over = False
        self.cumulative_word = ""
        self.game_root_node = None

        self.first_player = self.get_first_player()

    def move_is_damned(self, move):
        is_damned = False

        new_subword = self.cumulative_word + move
        nearest_node, is_last_letter_in_word = \
            self.search_for_parent_node(new_subword)

        is_damned &= (is_last_letter_in_word is True)
        is_damned &= (nearest_node is None)
        is_damned &= (
            (nearest_node is not None) and 
            (not nearest_node.children))

        return is_damned

    def print_player_move(self, player, move, 
            is_complete_word=False, move_is_damned=False):

        player_identifier = "⬤  %s(%s) " % (str(player), player.player_no+1)
        new_substring = self.cumulative_word + move

        if move_is_damned:
            message_type = "Final Word:"
        else:
            message_type = "Incomplete" \
                if not is_complete_word else "Complete"

        message_colour = "green" if not player.is_ai_player else "red"

        print colored(player_identifier, message_colour), \
            message_type, \
            "'%s'" % self.cumulative_word, " + ", colored("'%s'" % move, "blue"), \
            " = ", new_substring

    def concede_defeat(self, player, move, node):
        def join_words(words):
            if words:
                return ', '.join([("'%s'" % word) for word in words])
            return words

        if node is not None:
            if not player.is_ai_player:
                list_of_complete_words = all_possible_words_after_node(node)

                if len(list_of_complete_words) >= 5:
                    list_of_complete_words = random.sample(list_of_complete_words, 5)

                if list_of_complete_words:
                    print "\nI bet you were thinking%s" % \
                        (" either" if len(list_of_complete_words) > 1 else ""), \
                        join_words(list_of_complete_words), "lol"
        else:
            if not player.is_ai_player:
                print ("\nYour word; '%s%s', is not in the dictionary!\n" % 
                    (self.cumulative_word, move))

    def search_for_parent_node(self, subword):
        return self.dictionary\
                .search_for_parent_node(subword)

    def make_move(self, player):
        node = None
        move = player.make_move()

        is_complete_word = False
        if move is not None:
            node, is_complete_word = self.search_for_parent_node(
                self.cumulative_word + move)

            if self.move_is_damned(move):
                self.print_player_move(player, move, 
                    is_complete_word, move_is_damned=True)
                self.end_game(player, move, node)
            else:
                self.print_player_move(player, move, is_complete_word)
                self.cumulative_word += move

                if node is not None and is_complete_word:
                    self.end_game(player, move, node)
                else:
                    self.last_player = player #set the last player

        return node, is_complete_word

    def play_game(self, words):
        if not self.setup_complete:
            self.setup_game(words)
        else:
            self.clear_game()

        def print_game_over():
            print "\nGame Over!\n", self.get_winner_message()
            print "." * 65
            print

        while not self.is_game_over():
            for i, player in enumerate(self.get_players()):
                self.current_player = player
                self.current_node, is_complete_word = self.make_move(player)
                
                if self.move_no == 1:
                     self.game_root_node = self.current_node

                if (self.is_game_over() or is_complete_word or self.current_node is None):
                    self.winner = self.previous_player
                    print_game_over()
                    return
                
                self.move_no += 1
                self.previous_player = player
            else:
                print "." * 65
                print

        print_game_over()
