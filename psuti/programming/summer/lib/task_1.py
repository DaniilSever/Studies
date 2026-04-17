from math import sqrt, sin, pi
from .decorator import Task_1, Interval

@Task_1.register(1)
class T1Var1:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-9, 10):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-9, -6)
    def func_1(x: int) -> int: return -sqrt(9 - (x + 6)**2)
    
    @interval.registry(-6, -3)
    def func_2(x: int)-> int: return x + 3

    @interval.registry(-3, 0)
    def func_3(x: int)-> int: return sqrt(9 - x**2)
    
    @interval.registry(0, 3)
    def func_4(x: int)-> int: return -x + 3

    @interval.registry(3, 10)
    def func_5(x: int)-> int: return (x - 3) / 2


@Task_1.register(2)
class T1Var2:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-10, 9):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-10, -8)
    def func_1(x: int) -> int: return -3
    
    @interval.registry(-8, -3)
    def func_2(x: int)-> int: return 0.6 * x + 1.8

    @interval.registry(-3, 3)
    def func_3(x: int)-> int: return -sqrt(9 - x**2)
    
    @interval.registry(3, 5)
    def func_4(x: int)-> int: return x - 3

    @interval.registry(5, 9)
    def func_5(x: int)-> int: return 3


@Task_1.register(3)
class T1Var3:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-9, 6):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-9, -5)
    def func_1(x: int) -> int: return -sqrt(4 - (x + 7)**2) + 2
    
    @interval.registry(-5, -4)
    def func_2(x: int)-> int: return 2

    @interval.registry(-4, 0)
    def func_3(x: int)-> int: return -x / 2
    
    @interval.registry(0, pi)
    def func_4(x: int)-> int: return sin(x)

    @interval.registry(pi, 6)
    def func_5(x: int)-> int: return x - pi


@Task_1.register(4)
class T1Var4:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-10, 9):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-10, 0)
    def func_1(x: int) -> int: return (-x - 6) / 2
    
    @interval.registry(0, 3)
    def func_2(x: int)-> int: return -sqrt(9 - x**2)

    @interval.registry(3, 6)
    def func_3(x: int)-> int: return sqrt(9 - (x - 6)**2)
    
    @interval.registry(6, 9)
    def func_4(x: int)-> int: return 0


@Task_1.register(5)
class T1Var5:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-4, 11):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-4, -2)
    def func_1(x: int) -> int: return x + 3
    
    @interval.registry(-2, 4)
    def func_2(x: int)-> int: return -x / 2

    @interval.registry(4, 6)
    def func_3(x: int)-> int: return -2
    
    @interval.registry(6, 11)
    def func_4(x: int)-> int: return sqrt(4 - (x - 8)**2) - 2


@Task_1.register(6)
class T1Var6:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-8, 11):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-8, -5)
    def func_1(x: int) -> int: return -3
    
    @interval.registry(-5, -3)
    def func_2(x: int)-> int: return x + 3

    @interval.registry(-3, 3)
    def func_3(x: int)-> int: return sqrt(9 - x**2)
    
    @interval.registry(3, 8)
    def func_4(x: int)-> int: return 0.6 * x - 1.8
    
    @interval.registry(8, 11)
    def func_5(x: int)-> int: return 3


@Task_1.register(7)
class T1Var7:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-7, 12):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-7, -3)
    def func_1(x: int) -> int: return 3
    
    @interval.registry(-3, 3)
    def func_2(x: int)-> int: return -sqrt(9 - x**2) + 3

    @interval.registry(3, 6)
    def func_3(x: int)-> int: return -2 * x + 9
    
    @interval.registry(6, 12)
    def func_4(x: int)-> int: return x - 9


@Task_1.register(8)
class T1Var8:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-10, 9):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-10, -6)
    def func_1(x: int) -> int: return sqrt(4 - (x + 8)**2) - 2
    
    @interval.registry(-6, 2)
    def func_2(x: int)-> int: return (x + 2) / 2

    @interval.registry(2, 6)
    def func_3(x: int)-> int: return 0
    
    @interval.registry(6, 9)
    def func_4(x: int)-> int: return (x - 6)**2


@Task_1.register(9)
class T1Var9:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-9, 8):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-9, -7)
    def func_1(x: int) -> int: return 0
    
    @interval.registry(-7, -3)
    def func_2(x: int)-> int: return x + 7

    @interval.registry(-3, -2)
    def func_3(x: int)-> int: return 4
    
    @interval.registry(-2, 2)
    def func_4(x: int)-> int: return x**2
    
    @interval.registry(2, 4)
    def func_5(x: int)-> int: return -2 * x + 8
 
    @interval.registry(4, 8)
    def func_6(x: int)-> int: return 0


@Task_1.register(10)
class T1Var10:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-10, 5):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-10, -6)
    def func_1(x: int) -> int: return -sqrt(4 - (x + 8)**2) + 2
    
    @interval.registry(-6, -4)
    def func_2(x: int)-> int: return 2

    @interval.registry(-4, 2)
    def func_3(x: int)-> int: return -x / 2
    
    @interval.registry(2, 5)
    def func_4(x: int)-> int: return x - 3


@Task_1.register(11)
class T1Var11:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-3, 6):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-3, -2)
    def func_1(x: int) -> int: return -x - 2
    
    @interval.registry(-2, -1)
    def func_2(x: int)-> int: return sqrt(1 - (x + 1)**2)

    @interval.registry(-1, 1)
    def func_3(x: int)-> int: return 1
    
    @interval.registry(1, 2)
    def func_4(x: int)-> int: return -2 * x + 3

    @interval.registry(2, 6)
    def func_5(x: int)-> int: return -1


@Task_1.register(12)
class T1Var12:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-7, 4):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-7, -6)
    def func_1(x: int) -> int: return 2
    
    @interval.registry(-6, -2)
    def func_2(x: int)-> int: return (x + 2) / 4

    @interval.registry(-2, 0)
    def func_3(x: int)-> int: return -sqrt(4 - (x + 2)**2) + 2
    
    @interval.registry(0, 2)
    def func_4(x: int)-> int: return sqrt(4 - x**2)

    @interval.registry(2, 4)
    def func_5(x: int)-> int: return -x + 2


@Task_1.register(13)
class T1Var13:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-5, 10):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-5, -3)
    def func_1(x: int) -> int: return x + 3
    
    @interval.registry(-3, 0)
    def func_2(x: int)-> int: return sqrt(9 - x**2)

    @interval.registry(0, 6)
    def func_3(x: int)-> int: return -0.5 * x + 3
    
    @interval.registry(6, 10)
    def func_4(x: int)-> int: return x - 6


@Task_1.register(14)
class T1Var14:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-6, 13):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-6, -4)
    def func_1(x: int) -> int: return -2
    
    @interval.registry(-4, 0)
    def func_2(x: int)-> int: return (0.5 * x) / 2

    @interval.registry(0, 2)
    def func_3(x: int)-> int: return x**2
    
    @interval.registry(2, 13)
    def func_4(x: int)-> int: return (-x + 10) / 2


@Task_1.register(15)
class T1Var15:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-7, 4):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-7, -6)
    def func_1(x: int) -> int: return 1
    
    @interval.registry(-6, -4)
    def func_2(x: int)-> int: return -0.5 * x - 2

    @interval.registry(-4, 0)
    def func_3(x: int)-> int: return sqrt(4 - (x + 2)**2)
    
    @interval.registry(0, 2)
    def func_4(x: int)-> int: return -sqrt(1 - (x - 1)**2)

    @interval.registry(2, 4)
    def func_5(x: int)-> int: return -x + 2


@Task_1.register(16)
class T1Var16:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-8, 11):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-8, -4)
    def func_1(x: int) -> int: return -3
    
    @interval.registry(-4, -3)
    def func_2(x: int)-> int: return 2 * x + 6

    @interval.registry(-3, 3)
    def func_3(x: int)-> int: return sqrt(9 - x**2)
    
    @interval.registry(3, 8)
    def func_4(x: int)-> int: return 0.6 * x - 1.8

    @interval.registry(8, 11)
    def func_5(x: int)-> int: return 3


@Task_1.register(17)
class T1Var17:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-5, 6):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-5, -3)
    def func_1(x: int) -> int: return 1
    
    @interval.registry(-3, -1)
    def func_2(x: int)-> int: return -sqrt(4 - (x + 1)**2)

    @interval.registry(-1, 2)
    def func_3(x: int)-> int: return -2
    
    @interval.registry(2, 6)
    def func_4(x: int)-> int: return x - 4


@Task_1.register(18)
class T1Var18:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-3, 8):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-3, -2)
    def func_1(x: int) -> int: return -x - 2
    
    @interval.registry(-2, 0)
    def func_2(x: int)-> int: return sqrt(1 - (x + 1)**2)

    @interval.registry(0, 4)
    def func_3(x: int)-> int: return -sqrt(4 - (x - 2)**2)
    
    @interval.registry(4, 6)
    def func_4(x: int)-> int: return (-x + 4) / 2

    @interval.registry(6, 8)
    def func_5(x: int)-> int: return -1


@Task_1.register(19)
class T1Var19:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-3, 8):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-3, -1)
    def func_1(x: int) -> int: return -x - 1
    
    @interval.registry(-1, 1)
    def func_2(x: int)-> int: return 0

    @interval.registry(1, 5)
    def func_3(x: int)-> int: return sqrt(4 - (x - 3)**2)
    
    @interval.registry(5, 8)
    def func_4(x: int)-> int: return (-x + 5) / 2


@Task_1.register(20)
class T1Var20:
    interval = Interval()

    def __call__(self):
        # ---- header ----
        print("\n\nТаблица значений функции")
        print("=" * 23)
        print("|{:^10}|{:^10}|".format("x", "y"))
        print("=" * 23)

        for x in range (-4, 6):
            func = self.interval.get_func(x)
            if func:
                y = func(x)
                print("|{:10.2f}|{:10.2f}|".format(x, y))
        print("=" * 23)

    # ---- funcs ----
    @interval.registry(-4, 0)
    def func_1(x: int) -> int: return -0.5 * x
    
    @interval.registry(0, 2)
    def func_2(x: int)-> int: return 2 - sqrt(4 - x**2)

    @interval.registry(2, 4)
    def func_3(x: int)-> int: return sqrt(4 - (x - 2)**2)
    
    @interval.registry(4, 6)
    def func_4(x: int)-> int: return -x + 4

