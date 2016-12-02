
def flatten_array(items):
    flattened = []

    for item in items:
        if type(item) == list:
            flattened += flatten_array(item)
        else:
            flattened.append(item)

    return flattened

def split_word_to_letters(word):
    if word is None:
        word = ''

    return [letter for letter in word]

def read_file_lines(words_file):
    return [word.rstrip() for word in words_file]
