import pytest
from lib.LinkedList import LinkedList

_list = LinkedList()

val_list_good = [i for i in range(10, 20)]
val_list_bad = ["Hello", "World", 15]


@pytest.mark.parametrize("val_list, result", [(val_list_good, True)])
def test_add_element_good(val_list, result):
    for i in val_list:
        assert _list.add_element(i) == result


def test_clean_list_true_head():
    assert _list.clean_list() is True


@pytest.mark.parametrize("expected_exception, val_list", [(TypeError, val_list_bad)])
def test_add_element_bad(expected_exception, val_list):
    with pytest.raises(expected_exception):
        for i in val_list:
            assert _list.add_element(i)
    _list.clean_list()


@pytest.mark.parametrize("val_list, result", [(val_list_good, val_list_good)])
def test_show_list_true_head(val_list, result):
    for i in val_list:
        _list.add_element(i)
    assert _list.show_list() == result
    _list.clean_list()


@pytest.mark.parametrize("val_list, result", [(val_list_good, val_list_good[::-1])])
def test_reverse_list_true_head(val_list, result):
    for i in val_list:
        _list.add_element(i)
    assert _list.reverse_list() == result
    _list.clean_list()


@pytest.mark.parametrize(
    "val_list, result, result_list", [(val_list_good, True, val_list_good[1::])]
)
def test_remove_head_true_head(val_list, result, result_list):
    for i in val_list:
        _list.add_element(i)
    assert _list.remove_head() == result
    assert _list.show_list() == result_list
    _list.clean_list()


@pytest.mark.parametrize(
    "val_list, result, result_list", [(val_list_good, True, val_list_good[:-1:])]
)
def test_remove_tail_true_head(val_list, result, result_list):
    for i in val_list:
        _list.add_element(i)
    assert _list.remove_tail() == result
    assert _list.show_list() == result_list
    _list.clean_list()


@pytest.mark.parametrize("result", [(None)])
def test_show_list_none_head(result):
    assert _list.show_list() == result


@pytest.mark.parametrize("result", [(None)])
def test_reverse_list_none_head(result):
    assert _list.reverse_list() == result


@pytest.mark.parametrize("result", [(None)])
def test_remove_head_none_head(result):
    assert _list.remove_head() == result


@pytest.mark.parametrize("result", [(None)])
def test_remove_tail_none_head(result):
    assert _list.remove_tail() == result
