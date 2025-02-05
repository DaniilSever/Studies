class Soda:
    def __init__(self, supplement: str = None):
        if isinstance(supplement, str):
            self.__supplement = supplement
        else:
            self.__supplement = None

    def show_my_drink(self):
        if self.__supplement is None:
            print("Обычная газировка")
        else:
            print(f"Газировка с добавкой '{self.__supplement}'")
