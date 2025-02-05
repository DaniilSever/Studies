def check_simple_number(value: int) -> bool:
    res = [1, value]
    for i in range(2, value-1):
        if i**2 == value:
            break

        if not value % i:
            res.append(i)
    if len(res) == 2:
        return True
    else:
        return False


set_value = [17, 10, 500, 50, 24, 20]
for i in set_value:
    print(check_simple_number(i))
