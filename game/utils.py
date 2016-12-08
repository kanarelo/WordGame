try:
    from termcolor import colored
except ImportError:
    def colored(string, colour):
        return string

def flatten_list(items):
    def flatten(flattened, item):
        if type(item) == list:
            flattened += flatten_list(item)
        else:
            flattened.append(item)
        return flattened
    return reduce(flatten, items, [])

def split_word_to_letters(word):
    if word is None:
        word = ''

    return [letter for letter in word]

def read_file_lines(words_file):
    return [word.rstrip() for word in words_file]

def print_game_message():
    print colored("""
+==============================================================+
| Welcome to the word game!                                    |
|                                                              |
| This is a 2-player word game, in which the players take      |
| turns saying a letter. If a player says a letter that ends   |
| a word, that player loses. Similarly, if a player says a     |
| letter from which no word can be spelled, that player loses. |
|                                                              |
| For example: if the letters so far are "COR", then the next  |
| player could not say "E" (spelling "CORE") or "Z" ("CORZ"    |
| is not the beginning to any words) without losing.           |
|                                                              |
+==============================================================+
        """, 
        "blue")

is_even = lambda s: (s % 2) == 0
is_odd  = lambda s: (s % 2) == 1