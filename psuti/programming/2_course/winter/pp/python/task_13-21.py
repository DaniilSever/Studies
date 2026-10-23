import random
from typing import Callable

# tools
Matrix = list[list[int]]


class Reader:
    def __init__(self) -> None:
        self.buf: list[str] = []

    def next_int(self) -> int:
        while not self.buf:
            self.buf = input().split()
        return int(self.buf.pop(0))

    def matrix(self, n: int, m: int) -> Matrix:
        return [[self.next_int() for _ in range(m)] for _ in range(n)]


def random_matrix(n: int, m: int, max_val: int) -> Matrix:
    return [[random.randrange(max_val) for _ in range(m)] for _ in range(n)]


def print_matrix(a: Matrix) -> None:
    for row in a:
        print(" ".join(f"{v:3d}" for v in row))


def transpose(a: Matrix) -> Matrix:
    n = len(a)
    m = len(a[0])
    return [[a[j][i] for j in range(n)] for i in range(m)]


def rows_with_max(a: Matrix) -> list[int]:
    max_v: int = a[0][0]
    for row in a:
        for v in row:
            max_v = max(max_v, v)
    rows: list[int] = []
    for i, row in enumerate(a):
        for v in row:
            if v == max_v:
                rows.append(i)
                break
    return rows


class TaskMatrix:
    def __call__(self):
        """Запуск решения задач"""
        TASKS: dict[str, Callable[[], None]] = {
            "13": self.task_13,
            "14": self.task_14,
            "15": self.task_15,
            "16": self.task_16,
            "17": self.task_17,
            "18": self.task_18,
            "19": self.task_19,
            "20": self.task_20,
            "21": self.task_21,
        }

        num = input()
        if len(num) < 2:
            print("Использование: python3 stage2.py <номер задачи 13-21> [< input.txt]")
            return
        task: Callable[[], None] | None = TASKS.get(num)
        if task is None:
            print("Нет такой задачи:", num)
            return
        task()

    # --------------Tasks----------------

    def task_13(self) -> None:
        """
        13) Создать матрицу из случайных чисел и вывести построчно с
            форматным выводом, выделив 3 символа на каждый столбец и пробел в качестве разделителя
        """
        print_matrix(random_matrix(5, 4, 500))

    def task_14(self) -> None:
        """14) Осуществить транспонирование случайной матрицы (создать новую матрицу - транспонированную из предыдущей)."""
        a: Matrix = random_matrix(3, 5, 200)
        print("Исходная:")
        print_matrix(a)
        print("\nТранспонированная:")
        print_matrix(transpose(a))

    def task_15(self) -> None:
        """
        15) (A) Дано число n. Создайте массив int A[n][n], и заполните его по следующему правилу:
        - Числа на диагонали, идущей из правого верхнего в левый нижний угол равны 1.
        - Числа, стоящие выше этой диагонали, равны 0.
        - Числа, стоящие ниже этой диагонали, равны 2.
        Полученный массив выведите на экран. Числа разделяйте одним пробелом.
        """
        n = Reader().next_int()
        for i in range(n):
            row: list[int] = []
            for j in range(n):
                if i + j == n - 1:
                    row.append(i)
                elif i + j < n - 1:
                    row.append(0)
                else:
                    row.append(2)
            print(" ".join(map(str, row)))

    def task_16(self) -> None:
        """
        16) (B) Дано число n и квадратный массив int A[n][n].
        Проверьте, является ли массив симметричным относительно главной диагонали.
        Программа должна выводить слово "yes" для симметричного массива и слово "no" для несимметричного.
        """
        r: Reader = Reader()
        n = r.next_int()
        a: Matrix = r.matrix(n, n)
        for i in range(n):
            for j in range(i + 1, n):
                if a[i][j] != a[j][i]:
                    print("no")
                    return
        print("yes")

    def task_17(self) -> None:
        """
        17) (C) Состязания - 1.
        В метании молота состязается n спортсменов.
        Каждый из них сделал m бросков.
        Победителем считается тот спортсмен, у которого сумма результатов по всем броскам максимальна.
        Если перенумеровать спортсменов числами от 0 до n-1,
            а попытки каждого из них – от 0 до m-1,
            то на вход программа получает массив int
        A[n][m], состоящий из неотрицательных чисел.
        Программа должна определить максимальную сумму чисел в одной строке
            и вывести на экран эту сумму и номер строки, для которой достигается эта сумма.
        Если таких строк несколько, то выводится номер наименьшей из них.
        """
        r: Reader = Reader()
        n = r.next_int()
        m = r.next_int()
        a: Matrix = r.matrix(n, m)
        best_sum = -1
        best_row = -1
        for i in range(n):
            s = 0
            for j in range(m):
                s += a[i][j]
            if s > best_sum:
                best_sum, best_row = s, i
        print(best_sum, "\n", best_row)

    def task_18(self) -> None:
        """
        18) (D) Состязания - 2.
        Победителем соревнований объявляется тот спортсмен, у которого максимален наилучший результат по всем броскам.
        Таким образом, программа должна найти значение максимального элемента в данном массиве, а также его индексы
            (то есть номер спортсмена и номер попытки).
        Программа выводит значение максимального элемента, затем номер строки и номер столбца, в котором он встречается.
        Если в массиве несколько максимальных элементов, то нужно вывести минимальный номер строки,
            в которой встречается такой элемент, а если в этой строке таких элементов несколько,
            то нужно вывести минимальный номер столбца.
        """
        r: Reader = Reader()
        n = r.next_int()
        m = r.next_int()
        a: Matrix = r.matrix(n, m)
        max_v = a[0][0]
        mi = 0
        mj = 0
        for i in range(n):
            for j in range(m):
                if a[i][j] > max_v:
                    max_v, mi, mj = a[i][j], i, j
        print(max_v, mi, mj)

    def task_19(self) -> None:
        """
        19) (E) Состязания - 3.
        Будем считать, что побеждает спортсмен, у которого максимален наилучший бросок.
        Если таких несколько, то из них побеждает тот, у которого наилучшая сумма результатов по всем попыткам.
        Если и таких несколько, победителем считается спортсмен с минимальным номеров.
        """
        r: Reader = Reader()
        n = r.next_int()
        m = r.next_int()
        a: Matrix = r.matrix(n, m)
        winner = -1
        win_best = -1
        win_sum = -1
        for i in range(n):
            best = a[i][0]
            total = 0
            for v in a[i]:
                total += v
                best = max(best, v)
            if best > win_best or (best == win_best and total > win_sum):
                winner, win_best, win_sum = i, best, total
        print(winner)

    def task_20(self) -> None:
        """
        20) (F) Состязания - 4.
        Будем считать, что победитель определяется по лучшему результату.
        Определите количество участников состязаний, которые разделили первое место,
            то есть определите количество строк в массиве, которые содержат значение, равное наибольшему.
        """
        r: Reader = Reader()
        n = r.next_int()
        m = r.next_int()
        print(len(rows_with_max(r.matrix(n, m))))

    def task_21(self) -> None:
        """
        21) (G) Состязания - 5.
        Решите предыдущую задачу, но на экран выведите еще и номера спортсменов, разделивших первое место.
        Сначала программа выводит количество спортсменов, показавших наилучший результат,
            затем – их номера в порядке возрастания.
        """
        r: Reader = Reader()
        n = r.next_int()
        m = r.next_int()
        rows: list[int] = rows_with_max(r.matrix(n, m))
        print(len(rows))
        print(" ".join(map(str, rows)))


if __name__ == "__main__":
    TaskMatrix()()
