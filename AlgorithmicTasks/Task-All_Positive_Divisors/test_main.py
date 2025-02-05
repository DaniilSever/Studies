import pytest
from main import all_divisors

set_values = [23436, 190187200, 380457890232]


def test_all_divisors_return_list():
    for value in set_values:
        assert type(all_divisors(value)) is list


@pytest.mark.parametrize("values", set_values)
def test_all_divisors_check_divisors(values):
    divisors = all_divisors(values)
    print(divisors)
    for value in divisors:
        print(value)
        assert not values % value
