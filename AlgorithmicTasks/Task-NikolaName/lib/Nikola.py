class Nikola:
    __slots__ = ("__first_name", "__age")

    def __init__(self, name: str, age: int):
        if name == "Николай":
            self.__first_name = "Николай"
            self.__age = age
        else:
            print(f"Я не {name}, а Николай")
