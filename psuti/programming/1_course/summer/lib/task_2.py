from math import sqrt, sin, atan, cos
from .decorator import Task_2

@Task_2.register(1)
class T2Var1:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            if n == 1:
                numerator = sin(self.x)
            else:
                numerator = sin(numerator)

            denominator = sqrt(n+1 + denominator)

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(2)
class T2Var2:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            numerator = atan(self.x) + n

            denominator = sqrt(2 + denominator)

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(3)
class T2Var3:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            if n == 1:
                numerator = cos(self.x)
            else:
                numerator = cos(numerator)

            if n % 2 == 0:
                denominator += 5
            else:
                denominator += 3

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(4)
class T2Var4:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            numerator = (self.x + 1)**n

            if n % 2 == 0:
                denominator = sqrt(5 + denominator)
            else:
                denominator = sqrt(3 + denominator)

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(5)
class T2Var5:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            if n == 1:
                numerator = cos(self.x)
            else:
                numerator = cos(numerator)

            denominator = sqrt(n+1 + denominator)

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(6)
class T2Var6:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            if n == 1:
                numerator = atan(self.x)
            else:
                numerator = atan(numerator)

            denominator = sqrt(2 + denominator)

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(7)
class T2Var7:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 1

        for n in range(1, self.N+1):
            if n == 1:
                numerator = 1
            else:
                numerator += self.x ** (n - 1)

            denominator *= (2*n - 1)

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(8)
class T2Var8:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(0, self.N):
            if n == 0:
                numerator = 1
            else:
                numerator += self.x ** n

            denominator = sqrt(2 + denominator)

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(9)
class T2Var9:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            numerator = sin(self.x) + n

            if n == 1:
                denominator = 1
            else:
                if n % 2 == 0:
                    denominator += 3
                else:
                    denominator += 1

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(10)
class T2Var10:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            numerator = cos(self.x) + n

            denominator = n**2

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(11)
class T2Var11:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 1

        for n in range(1, self.N+1):
            numerator = atan(self.x) + n

            denominator *= (2*n - 1)

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(12)
class T2Var12:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            numerator = (self.x + 1)**n

            denominator = sqrt(2 + denominator)

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(13)
class T2Var13:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            if n == 1:
                numerator = sin(self.x)
            else:
                numerator = sin(numerator)

            denominator = sqrt(2 + denominator)

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(14)
class T2Var14:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            numerator = cos(self.x) + n

            if n % 2 == 0:
                denominator = sqrt(4 + denominator)
            else:
                denominator = sqrt(3 + denominator)

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(15)
class T2Var15:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 1

        for n in range(1, self.N+1):
            if n == 1:
                numerator = sin(self.x)
            else:
                numerator = sin(numerator)

            denominator *= n * 2

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(16)
class T2Var16:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            if n == 1:
                numerator = atan(self.x)
            else:
                numerator = atan(numerator)

            denominator += n 

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(17)
class T2Var17:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 1

        for n in range(1, self.N+1):
            numerator = (self.x + 1)**n
            denominator *= n * 2

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(18)
class T2Var18:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            numerator = atan(self.x) + n
            denominator += n
            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")


@Task_2.register(19)
class T2Var19:
    def __init__(self, x: float, N: int):
        self.x = x
        self.N = N
        self.total = 0.0
    
    def __call__(self):
        denominator = 0

        for n in range(1, self.N+1):
            if n == 1:
                numerator = sin(self.x)
            else:
                numerator = sin(numerator)

            denominator = n ** 2

            self.total += numerator / denominator

        print(f"Сумма первых {self.N} членов при x={self.x} = {self.total:.4f}")
