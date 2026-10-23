BUF_SIZE = 256
CStr = list[str]


# tools
def new_str(s: str) -> CStr:
    """Создает буфер сиволов и копирует в него строку"""
    buf = ["\0"] * BUF_SIZE
    for i, ch in enumerate(s):
        buf[i] = ch
    return buf


def to_string(cs: CStr) -> str:
    """Переводит C-строку в обычную строку"""
    return "".join(cs[: TaskChar().my_strlen(cs)])


class TaskChar:
    def __call__(self):
        """Запуск решения задач"""

        def show(name: str, a: CStr) -> None:
            print(f"{name:<10} [{to_string(a)}] len={self.my_strlen(a)}")

        print("1) my_strlen('hello') =", self.my_strlen(new_str("hello")))

        dst: CStr = new_str("")
        self.my_strcpy(dst, new_str("copy me"))
        show("2) strcpy", dst)

        cat: CStr = new_str("foo")
        self.my_strcat(cat, new_str("bar"))
        show("3) strcat", cat)

        print(
            "4) strcmp(abc, after) =", self.my_strcmp(new_str("abc"), new_str("after"))
        )
        print("   strcmp(abc, abc) =", self.my_strcmp(new_str("abc"), new_str("abc")))
        print("   strcmp(abcd, abc) =", self.my_strcmp(new_str("abcd"), new_str("abc")))

        t: CStr = new_str("  hi  ")
        self.trim_right(t)
        show("5) trimRight", t)

        t = new_str("  hi  ")
        self.trim_left(t)
        show("6) trimLeft", t)

        p: CStr = new_str("go")
        self.pad_right(p, 6)
        show("7) padRight", p)

        p = new_str("go")
        self.pad_left(p, 6)
        show("8) padLeft", p)

        p = new_str("go")
        self.center(p, 6)
        show("9) center", p)

        print(
            "10) count(abracadabra, 'a') =",
            self.count_char(new_str("abracadabra"), "a"),
        )

        print(
            "11) count(abracadabra, bax) =",
            self.count_chars(new_str("abracadabra"), new_str("bax")),
        )

        d: CStr = new_str("abracadabra")
        self.delete_char(d, "a")
        show("12) delete", d)

    # --------------Tasks----------------

    def my_strlen(self, a: CStr) -> int:
        """1) Аналог strlen"""
        n = 0
        while a[n] != "\0":
            n += 1
        return n

    def my_strcpy(self, a: CStr, b: CStr) -> None:
        """2) Аналог strcpy"""
        i = 0
        while b[i] != "\0":
            a[i] = b[i]
            i += 1
        a[i] = "\0"

    def my_strcat(self, a: CStr, b: CStr) -> None:
        """3) Аналог srtcat"""
        i = self.my_strlen(a)
        j = 0
        while b[j] != "\0":
            a[i] = b[j]
            i += 1
            j += 1
        a[i] = "\0"

    def my_strcmp(self, a: CStr, b: CStr) -> int:
        """4) Аналог strcmp"""
        i = 0
        while a[i] != "\0" and a[i] == b[i]:
            i += 1
        return ord(a[i]) - ord(b[i])

    def trim_right(self, a: CStr) -> None:
        """5) Функция для удаления всех пустых пробелов после окончания строки (trimRight)"""
        i = self.my_strlen(a) - 1
        while i >= 0 and a[i] == " ":
            i -= 1
        a[i + 1] = "\0"

    def trim_left(self, a: CStr) -> None:
        """6) Функция для удаления всех пустых пробелов перед началом строки (trimLeft)"""
        start: int = 0
        while a[start] == " ":
            start += 1
        if start == 0:
            return
        i = 0
        while a[start + i] != "\0":
            a[i] = a[start + i]
            i += 1
        a[i] = "\0"

    def pad_right(self, a: CStr, n: int) -> None:
        """
        7) Функция для добавления дополнительных пробелов после окончания строки, чтобы длина строки стала равна n.
        Если строка уже из n или больше символов, то изменять строку не нужно (padRight)
        """
        length = self.my_strlen(a)
        if length >= n:
            return
        for i in range(length, n):
            a[i] = " "
        a[n] = "\0"

    def pad_left(self, a: CStr, n: int) -> None:
        """
        8) Функция для добавления дополнительных пробелов перед началом строки, чтобы длина строки стала равна n.
        Если строка уже из n или больше символов, то изменять строку не нужно (padLeft)
        """
        length = self.my_strlen(a)
        if length >= n:
            return
        shift = n - length
        for i in range(length, -1, -1):
            a[i + shift] = a[i]
        for i in range(shift):
            a[i] = " "

    def center(self, a: CStr, n: int) -> None:
        """
        9) Функция «выравнивания» по центру строки, добавляя слева и справа необходимое количество пробелов.
        Если строка уже из n или больше символов, то изменять строку не нужно.
        Если количество пробелов нечетно – дополнительный пробел необходимо добавить справа
        """
        length = self.my_strlen(a)
        if length >= n:
            return
        left: int = (n - length) // 2
        self.pad_left(a, length + left)
        self.pad_right(a, n)

    def count_char(self, a: CStr, c: str) -> int:
        """10) Функция count, которая подсчитывает, сколько раз символ встретился в строке a"""
        total = 0
        i = 0
        while a[i] != "\0":
            if a[i] == c:
                total += 1
            i += 1
        return total

    def count_chars(self, a: CStr, b: CStr) -> int:
        """
        11) Функция , count, которая подсчитывает, сколько раз символы из строки b встретились в строке a
        (суммарное количество вхождений каждого из уникальных символов)
        """
        seen: set[str] = set()
        total = 0
        i = 0
        while b[i] != "\0":
            c = b[i]
            if c not in seen:
                seen.add(c)
                total += self.count_char(a, c)
            i += 1
        return total

    def delete_char(self, a: CStr, c: str) -> None:
        """12) Функция deleteChar, которая удаляет все вхождения символа"""
        w = 0
        r = 0
        while a[r] != "\0":
            if a[r] != c:
                a[w] = a[r]
                w += 1
            r += 1
        a[w] = "\0"


if __name__ == "__main__":
    TaskChar()()
