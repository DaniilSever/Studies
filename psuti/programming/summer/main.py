from lib.decorator import Task_1, Task_2
from lib.task_1 import *
from lib.task_2 import *


if __name__ == "__main__":
    task_num = int(input("Номер задания - "))
    match task_num:
        case 1:
            var = int(input("Вариант - "))
            Task_1.run(var)

        case 2:
            var = int(input("Вариант - "))
            Task_2.run(var)