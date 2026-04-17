class Task_1:
    variants = {}

    @classmethod
    def register(cls, number):
        def wrapper(var_class):
            cls.variants[number] = var_class
            return var_class
        return wrapper
    
    @classmethod
    def run(cls, number):
        if number in cls.variants:
            cls.variants[number]()()
        else:
            print(f"Вариант {number} не найден")

class Task_2:
    variants = {}

    @classmethod
    def register(cls, number):
        def wrapper(var_class):
            cls.variants[number] = var_class
            return var_class
        return wrapper
    
    @classmethod
    def run(cls, number):
        x = float(input("Введите x: "))
        n = int(input("Введите N: "))
        if number in cls.variants:
            cls.variants[number](x, n)()
        else:
            print(f"Вариант {number} не найден")

class Interval:
    def __init__(self):
        self.intervals = []

    def registry(self, start: int, end: int):
        def wrapper(func):
            self.intervals.append((start, end, func))
            return func
        return wrapper
    
    def get_func(self, x: int):
        for start, end, func in self.intervals:
            if start <= x < end:
                return func
        return None