import random

# tools
Matrix = list[list[int]]


def random_matrix(n: int, m: int, max_val: int) -> Matrix:
    return [[random.randrange(max_val) for _ in range(m)] for _ in range(n)]


def print_matrix(a: Matrix) -> None:
    for row in a:
        print(" ".join(f"{v:3d}" for v in row))


class FlatMatrix:
    def __init__(self, rows: int, cols: int, data: list[int] | None = None) -> None:
        self.rows: int = rows
        self.cols: int = cols
        self.data: list[int] = data if data is not None else [0] * (rows * cols)

    def _index(self, row: int, col: int) -> int:
        return row * self.cols + col

    def get(self, row: int, col: int) -> int:
        return self.data[self._index(row, col)]

    def set(self, row: int, col: int, value: int) -> None:
        self.data[self._index(row, col)] = value

    def coords(self, k: int) -> tuple[int, int]:
        return k // self.cols, k % self.cols

    def print(self) -> None:
        for i in range(self.rows):
            print(" ".join(f"{self.get(i, j):3d}" for j in range(self.cols)))

    def row_sums(self) -> list[int]:
        sums: list[int] = [0] * self.rows
        for i in range(self.rows):
            for j in range(self.cols):
                sums[i] += self.get(i, j)
        return sums

    def col_sums(self) -> list[int]:
        sums: list[int] = [0] * self.cols
        for i in range(self.rows):
            for j in range(self.cols):
                sums[j] += self.get(i, j)
        return sums


class TaskHardMatrix:
    def __call__(self):
        """Запуск решения задач"""
        parts = input("Через пробел номер задачи и размер (default 4)\n").split()

        task_num = int(parts[0])
        num = int(parts[1]) if len(parts) > 1 else 4

        if len(str(task_num)) < 2:
            print("<номер задачи 22-26>")
            return

        if num < 1:
            print("Размер должен быть целым числом >= 1")
            return

        match task_num:
            case 22:
                self.task22(num)
            case 23:
                self.task23(num)
            case 24:
                self.task24(num)
            case 25:
                self.task25(num)
            case 26:
                self.task26()
            case _:
                print("Нет такой задачи:", task_num)

    # --------------Tasks----------------

    def task22(self, n: int) -> None:
        """22) Создайте матрицу A[2*N+1]x[2*N+1], заполненную по спирали от центра по часовой стрелке, начиная с 0"""

        def spiral(n: int) -> Matrix:
            size: int = 2 * n + 1
            a: Matrix = [[0] * size for _ in range(size)]
            dirs: list[tuple[int, int]] = [(0, 1), (1, 0), (0, -1), (-1, 0)]

            r: int = n
            c: int = n
            value: int = 0
            step: int = 1
            d: int = 0
            total: int = size * size

            while value < total - 1:
                for _ in range(2):
                    for _ in range(step):
                        r += dirs[d][0]
                        c += dirs[d][1]
                        if not (0 <= r < size and 0 <= c < size):
                            return a
                        value += 1
                        a[r][c] = value
                    d = (d + 1) % 4
                step += 1
            return a

        print_matrix(spiral(n))

    def task23(self, n: int) -> None:
        """23) Для случайной матрицы осуществить ее абсолютную сортировку (от [0][0] к [n-1][n-1])."""

        def absolute_sort(a: Matrix) -> None:
            m: int = len(a[0])
            total: int = len(a) * m

            def get(k: int) -> int:
                return a[k // m][k % m]

            def put(k: int, v: int) -> None:
                a[k // m][k % m] = v

            for i in range(1, total):
                key: int = get(i)
                j: int = i - 1
                while j >= 0 and get(j) > key:
                    put(j + 1, get(j))
                    j -= 1
                put(j + 1, key)

        a: Matrix = random_matrix(n, n + 1, 100)
        print("До:")
        print_matrix(a)
        absolute_sort(a)
        print("После:")
        print_matrix(a)

    def task24(self, n: int) -> None:
        """24) Отсортировать столбцы матрицы по результату среднего арифметического элементов."""

        def swap_columns(a: Matrix, x: int, y: int) -> None:
            for row in a:
                row[x], row[y] = row[y], row[x]

        def sort_columns_by_mean(a: Matrix) -> None:
            means: list[float] = column_means(a)
            m: int = len(means)
            for i in range(m - 1):
                min_idx: int = i
                for j in range(i + 1, m):
                    if means[j] < means[min_idx]:
                        min_idx = j
                if min_idx != i:
                    swap_columns(a, i, min_idx)
                    means[i], means[min_idx] = means[min_idx], means[i]

        def column_means(a: Matrix) -> list[float]:
            n: int = len(a)
            m: int = len(a[0])
            means: list[float] = []
            for j in range(m):
                s: int = 0
                for i in range(n):
                    s += a[i][j]
                means.append(s / n)
            return means

        def fmt_means(means: list[float]) -> str:
            return "[" + " ".join(f"{x:.2f}" for x in means) + "]"

        a: Matrix = random_matrix(n, n + 1, 100)
        print("До:")
        print_matrix(a)
        print("Средние:", fmt_means(column_means(a)))
        sort_columns_by_mean(a)
        print("После:")
        print_matrix(a)
        print("Средние:", fmt_means(column_means(a)))

    def task25(self, n: int) -> None:
        """
        25) Создать матрицу NxN, заполненную случайными числами, но чтобы около 25% элементов матрицы были = 0.
            Расположение нулей должно быть случайным. Подсчитать количество нулей.
        """

        def matrix_with_zeros(n: int) -> Matrix:
            a: Matrix = [[random.randint(1, 99) for _ in range(n)] for _ in range(n)]
            zeros: int = n * n // 4
            for p in random.sample(range(n * n), zeros):
                a[p // n][p % n] = 0
            return a

        def count_zeros(a: Matrix) -> int:
            cnt: int = 0
            for row in a:
                for v in row:
                    if v == 0:
                        cnt += 1
            return cnt

        a: Matrix = matrix_with_zeros(n)
        print_matrix(a)
        print(f"Нулей: {count_zeros(a)} из {n * n}")

    def task26(self) -> None:
        """
        26) Создать одномерный массив, который содержит последовательную запись элементов матрицы NxM.
        Обеспечить интерфейс работы с данным массивом как с матрицей:
            а) вывод в виде матрицы NxM;
            б) изменение элемента с координатами x, y;
            в) вычисление суммы по строкам, по столбцам.
        Например, матрица 2x3 из 1й задачи будет храниться в виде массива из 6 элементов:
            {44, 31, 15, 11, 221, 78}, т.е. каждую новую строку матрицы мы записываем последовательно в массив.
        “Матричные” координаты 5го элемента массива со значением 221 будут [1][1].
        """
        fm: FlatMatrix = FlatMatrix(2, 3, [44, 31, 15, 11, 221, 78])
        print("Хранение:", fm.data)
        print("а) Вывод матрицей:")
        fm.print()

        r: int
        c: int
        r, c = fm.coords(4)
        print(f"Элемент data[4] = {fm.data[4]} имеет координаты [{r}][{c}]")

        fm.set(0, 2, 99)
        print("б) После set(0, 2, 99):")
        fm.print()
        print("   Хранение:", fm.data)

        print("в) Суммы по строкам: ", fm.row_sums())
        print("   Суммы по столбцам:", fm.col_sums())


if __name__ == "__main__":
    TaskHardMatrix()()
