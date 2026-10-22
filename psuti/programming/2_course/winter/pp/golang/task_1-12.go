package main

import "fmt"

const Bufsize = 256

// C_tools
func newStr(s string) []byte {
	buf := make([]byte, Bufsize)
	for i := 0; i < len(s); i++ {
		buf[i] = s[i]
	}
	return buf
}

func toString(a []byte) string {
	return string(a[:myStrlen(a)])
}

// 1) Аналог strlen
func myStrlen(a []byte) int {
	n := 0
	for a[n] != 0 {
		n++
	}
	return n
}

// 2) Аналог strcpy
func myStrcpy(a, b []byte) {
	i := 0
	for b[i] != 0 {
		a[i] = b[i]
		i++
	}
	a[i] = 0
}

// 3) Аналог srtcat
func myStrcat(a, b []byte) {
	i := myStrlen(a)
	j := 0
	for b[j] != 0 {
		a[i] = b[j]
		i++
		j++
	}
	a[i] = 0
}

// 4) Аналог strcmp
func myStrcmp(a, b []byte) int {
	i := 0
	for a[i] != 0 && a[i] == b[i] {
		i++
	}
	return int(a[i]) - int(b[i])
}

// 5) Функция для удаления всех пустых пробелов после окончания строки (trimRight)
func trimRight(a []byte) {
	i := myStrlen(a) - 1
	for i >= 0 && a[i] == ' ' {
		i--
	}
	a[i+1] = 0
}

// 6) Функция для удаления всех пустых пробелов перед началом строки (trimLeft)
func trimLeft(a []byte) {
	start := 0
	for a[start] == ' ' {
		start++
	}
	if start == 0 {
		return
	}
	i := 0
	for a[start+i] != 0 {
		a[i] = a[start+i]
		i++
	}
	a[i] = 0
}

// 7) Функция для добавления дополнительных пробелов после окончания строки, чтобы длина строки стала равна n.
// Если строка уже из n или больше символов, то изменять строку не нужно (padRight)
func padRight(a []byte, n int) {
	length := myStrlen(a)
	for i := length; i < n; i++ {
		a[i] = ' '
	}
	if length < n {
		a[n] = 0
	}
}

// 8) Функция для добавления дополнительных пробелов перед началом строки, чтобы длина строки стала равна n.
// Если строка уже из n или больше символов, то изменять строку не нужно (padLeft)
func padLeft(a []byte, n int) {
	length := myStrlen(a)
	if length >= n {
		return
	}
	shift := n - length
	for i := length; i >= 0; i-- {
		a[i+shift] = a[i]
	}
	for i := 0; i < shift; i++ {
		a[i] = ' '
	}
}

// 9) Функция «выравнивания» по центру строки, добавляя слева и справа необходимое количество пробелов.
// Если строка уже из n или больше символов, то изменять строку не нужно.
// Если количество пробелов нечетно – дополнительный пробел необходимо добавить справа
func center(a []byte, n int) {
	length := myStrlen(a)
	if length >= n {
		return
	}
	left := (n - length) / 2
	padLeft(a, length+left)
	padRight(a, n)
}

// 10) Функция count, которая подсчитывает, сколько раз символ встретился в строке a
func countChar(a []byte, c byte) int {
	cnt := 0
	for i := 0; a[i] != 0; i++ {
		if a[i] == c {
			cnt++
		}
	}
	return cnt
}

// 11) Функция , count, которая подсчитывает, сколько раз символы из строки b встретились в строке a
// (суммарное количество вхождений каждого из уникальных символов)
func countChars(a, b []byte) int {
	var seen [256]bool
	total := 0
	for i := 0; b[i] != 0; i++ {
		c := b[i]
		if seen[c] {
			continue
		}
		seen[c] = true
		total += countChar(a, c)
	}
	return total
}

// 12) Функция deleteChar, которая удаляет все вхождения символа
func deleteChar(a []byte, c byte) {
	w := 0
	for r := 0; a[r] != 0; r++ {
		if a[r] != c {
			a[w] = a[r]
			w++
		}
	}
	a[w] = 0
}

// tool
func show(name string, a []byte) {
	fmt.Printf("%-10s [%s] len=%d\n", name, toString(a), myStrlen(a))
}

// Проверки:
func main() {
	s := newStr("hello")
	fmt.Println("1. myStrlen(\"hello\") =", myStrlen(s))

	dst := newStr("")
	myStrcpy(dst, newStr("copy me"))
	show("2. myStrcpy", dst)

	cat := newStr("foo")
	myStrcat(cat, newStr("bar"))
	show("3. myStrcat", cat)

	fmt.Println("4. myStrcmp(abc, after) =", myStrcmp(newStr("abc"), newStr("after")))
	fmt.Println("	myStrcmp(abc, abc) =", myStrcmp(newStr("abc"), newStr("abc")))
	fmt.Println("	myStrcmp(abcd, abc) =", myStrcmp(newStr("abcd"), newStr("abc")))

	t := newStr("  hi  ")
	trimRight(t)
	show("5. trimRight", t)

	t = newStr("  hi  ")
	trimLeft(t)
	show("6. trimLeft", t)

	p := newStr("go")
	padRight(p, 6)
	show("7. padRight", p)

	p = newStr("go")
	padLeft(p, 6)
	show("8. padLeft", p)

	p = newStr("go")
	center(p, 7)
	show("9. center", p)

	fmt.Println("10. count(abracadabra, 'a') =", countChar(newStr("abracadabra"), 'a'))
	fmt.Println("11. count(abracadabra, bax) =", countChars(newStr("abracadabra"), newStr("bax")))

	d := newStr("abracadabra")
	deleteChar(d, 'a')
	show("12. delete", d)
}
