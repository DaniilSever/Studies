from src.decorator import run_time


@run_time
def long__check_close_brackets(line: str) -> bool:
    stack = []
    for char in line:
        if char == "(":
            stack.append(char)
        elif char == ")":
            if not stack or stack.pop() != "(":
                return False
    return not stack


@run_time
def best__check_close_brackets(line: str) -> bool:
    str_filter = "()"
    for _ in line:
        line = line.replace(str_filter, "")
        if len(line) == 0 or len(line) == 1:
            break

    if len(line) != 0:
        return False
    else:
        return True


s = ""
for _ in range(1000):
    s += "()()()()()()()"
print(best__check_close_brackets(s))
print(long__check_close_brackets(s))
