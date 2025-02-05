from main import three_args


def test_three_args_all_None_args():
    assert three_args() is None


def test_three_args_NotNone_1_args():
    assert three_args(value_1=1) == print("Переданные аргументы: var1 = 1")
    assert three_args(value_2="g") == print("Переданные аргументы: var2 = g")
    assert three_args(value_3=23) == print("Переданные аргументы: var3 = 23")


def test_three_args_NotNone_2_args():
    assert three_args(value_1=1, value_2=4) == print(
        "Переданные аргументы: var1 = 1 var2 = 4"
    )
    assert three_args(value_2="g", value_3=41) == print(
        "Переданные аргументы: var2 = g var3 = 41"
    )
    assert three_args(value_1="jn", value_3=23) == print(
        "Переданные аргументы: var1 = jn var3 = 23"
    )


def test_three_args_NotNone_3_args():
    assert three_args(value_1="jn", value_2=False, value_3=23) == print(
        "Переданные аргументы: var1 = jn var2 = False var3 = 23"
    )
