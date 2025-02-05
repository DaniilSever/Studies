from lib.Nikola import Nikola


def set_second_name(self, name: str):
    pass


my = Nikola("Николай", 30)
my.set_second_name = set_second_name.__get__(my)
my.second_name = "Дима"
print(my.__dict__)
