class TriangleChecker:
    def __init__(self, first_value: int, second_value: int, third_value: int):
        self.__first_rib = first_value
        self.__second_rib = second_value
        self.__third_rib = third_value

    def check(self, res, max):
        if res > max:
            print("Ура, можно построить треугольник!")
        else:
            print("Жаль, но из этого треугольник не сделать")

    def is_triangle(self):
        if (
            isinstance(self.__first_rib, int)
            and isinstance(self.__second_rib, int)
            and isinstance(self.__third_rib, int)
        ):
            if self.__first_rib > 0 and self.__second_rib > 0 and self.__third_rib > 0:
                max_rib = max(self.__first_rib, self.__second_rib, self.__third_rib)
                match max_rib:
                    case self.__first_rib:
                        res = self.__second_rib + self.__third_rib
                        self.check(res, max_rib)

                    case self.__second_rib:
                        res = self.__first_rib + self.__third_rib
                        self.check(res, max_rib)

                    case self.__third_rib:
                        res = self.__first_rib + self.__second_rib
                        self.check(res, max_rib)
            else:
                print("С отрицательными числами ничего не выйдет!")
        else:
            print("Нужно вводить только числа!")
