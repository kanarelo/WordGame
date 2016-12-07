
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
