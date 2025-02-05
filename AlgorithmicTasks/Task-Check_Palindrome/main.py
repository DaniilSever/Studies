def check_palindrome(word: str) -> bool:
    remove_symbol = ' ,!?.'
    for symbol in remove_symbol:
        word = word.replace(symbol, "")

    if word[::-1] == word:
        return True
    else:
        return False


print(check_palindrome("яд ефрему, а умер федя"))
