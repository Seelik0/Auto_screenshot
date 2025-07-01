class NoAlphabetException(Exception):
    """
    アルファベットを見分ける
    """
    pass

def alphabet(character):
    return character.isalpha()

def check_string(string):
    alphabets = [char for char in string if alphabet(char)]

    if alphabets:
        raise NoAlphabetException(f"{alphabets}")
    elif string == "":
        raise NoAlphabetException("Please enter the resolution")
