package main

import "fmt"

const Bufsize = 256

type CStr []byte

// tools
func newStr(s string) CStr {
	buf := make(CStr, Bufsize)
	copy(buf, s)
	return buf
}

func toString(a CStr) string {
	return string(a[:TaskChar{}.myStrlen(a)])
}

type TaskChar struct{}

// Запуск всех функций
func (t TaskChar) Run() {
	show := func(name string, a CStr) {
		fmt.Printf("%-12s [%s] len=%d\n", name, toString(a), t.myStrlen(a))
	}

	fmt.Println("1. myStrlen(\"hello\") =", t.myStrlen(newStr("hello")))

	dst := newStr("")
	t.myStrcpy(dst, newStr("copy me"))
	show("2. myStrcpy", dst)

	cat := newStr("foo")
	t.myStrcat(cat, newStr("bar"))
	show("3. myStrcat", cat)

	fmt.Println("4. myStrcmp(abc, after) =", t.myStrcmp(newStr("abc"), newStr("after")))
	fmt.Println("	myStrcmp(abc, abc) =", t.myStrcmp(newStr("abc"), newStr("abc")))
	fmt.Println("	myStrcmp(abcd, abc) =", t.myStrcmp(newStr("abcd"), newStr("abc")))

	tr := newStr("  hi  ")
	t.trimRight(tr)
	show("5. trimRight", tr)

	tr = newStr("  hi  ")
	t.trimLeft(tr)
	show("6. trimLeft", tr)

	p := newStr("go")
	t.padRight(p, 6)
	show("7. padRight", p)

	p = newStr("go")
	t.padLeft(p, 6)
	show("8. padLeft", p)

	p = newStr("go")
	t.center(p, 7)
	show("9. center", p)

	fmt.Println("10. count(abracadabra, 'a') =", t.countChar(newStr("abracadabra"), 'a'))
	fmt.Println("11. count(abracadabra, bax) =", t.countChars(newStr("abracadabra"), newStr("bax")))

	d := newStr("abracadabra")
	t.deleteChar(d, 'a')
	show("12. delete", d)
}

// --------------Tasks----------------

// 1) Аналог strlen
func (t TaskChar) myStrlen(a CStr) int {
	n := 0
	for a[n] != 0 {
		n++
	}
	return n
}

// 2) Аналог strcpy
func (t TaskChar) myStrcpy(a, b CStr) {
	i := 0
	for b[i] != 0 {
		a[i] = b[i]
		i++
	}
	a[i] = 0
}

// 3) Аналог srtcat
func (t TaskChar) myStrcat(a, b CStr) {
	i := t.myStrlen(a)
	j := 0
	for b[j] != 0 {
		a[i] = b[j]
		i++
		j++
	}
	a[i] = 0
}

// 4) Аналог strcmp
func (t TaskChar) myStrcmp(a, b CStr) int {
	i := 0
	for a[i] != 0 && a[i] == b[i] {
		i++
	}
	return int(a[i]) - int(b[i])
}

// 5) Функция для удаления всех пустых пробелов после окончания строки (trimRight)
func (t TaskChar) trimRight(a CStr) {
	i := t.myStrlen(a) - 1
	for i >= 0 && a[i] == ' ' {
		i--
	}
	a[i+1] = 0
}

// 6) Функция для удаления всех пустых пробелов перед началом строки (trimLeft)
func (t TaskChar) trimLeft(a CStr) {
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
func (t TaskChar) padRight(a CStr, n int) {
	length := t.myStrlen(a)
	if length >= n {
		return
	}
	for i := length; i < n; i++ {
		a[i] = ' '
	}
	a[n] = 0
}

// 8) Функция для добавления дополнительных пробелов перед началом строки, чтобы длина строки стала равна n.
// Если строка уже из n или больше символов, то изменять строку не нужно (padLeft)
func (t TaskChar) padLeft(a CStr, n int) {
	length := t.myStrlen(a)
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
func (t TaskChar) center(a CStr, n int) {
	length := t.myStrlen(a)
	if length >= n {
		return
	}
	left := (n - length) / 2
	t.padLeft(a, length+left)
	t.padRight(a, n)
}

// 10) Функция count, которая подсчитывает, сколько раз символ встретился в строке a
func (t TaskChar) countChar(a CStr, c byte) int {
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
func (t TaskChar) countChars(a, b CStr) int {
	var seen [256]bool
	total := 0
	for i := 0; b[i] != 0; i++ {
		c := b[i]
		if seen[c] {
			continue
		}
		seen[c] = true
		total += t.countChar(a, c)
	}
	return total
}

// 12) Функция deleteChar, которая удаляет все вхождения символа
func (t TaskChar) deleteChar(a CStr, c byte) {
	w := 0
	for r := 0; a[r] != 0; r++ {
		if a[r] != c {
			a[w] = a[r]
			w++
		}
	}
	a[w] = 0
}

func main() {
	TaskChar{}.Run()
}
