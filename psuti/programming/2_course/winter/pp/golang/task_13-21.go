package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
)

// tools
var in = bufio.NewReader(os.Stdin)
var out = bufio.NewWriter(os.Stdout)

func readInt() int {
	var x int
	fmt.Fscan(in, &x)
	return x
}

func readMatrix(n, m int) [][]int {
	a := make([][]int, n)
	for i := range a {
		a[i] = make([]int, m)
		for j := range a[i] {
			a[i][j] = readInt()
		}
	}
	return a
}

func randomMatrix(n, m, maxVal int) [][]int {
	a := make([][]int, n)
	for i := range a {
		a[i] = make([]int, m)
		for j := range a[i] {
			a[i][j] = rand.Intn(maxVal)
		}
	}
	return a
}

func printMatrix(a [][]int) {
	for _, row := range a {
		for j, v := range row {
			if j > 0 {
				fmt.Fprint(out, " ")
			}
			fmt.Fprintf(out, "%3d", v)
		}
		fmt.Fprintln(out)
	}
}

//  13. Создать матрицу из случайных чисел и вывести построчно с
//     форматным выводом, выделив 3 символа на каждый столбец и пробел в качестве разделителя
func task13() {
	a := randomMatrix(3, 4, 300)
	printMatrix(a)
}

// 14) Осуществить транспонирование случайной матрицы (создать новую матрицу - транспонированную из предыдущей).
func transpose(a [][]int) [][]int {
	n, m := len(a), len(a[0])
	t := make([][]int, m)
	for i := range t {
		t[i] = make([]int, n)
		for j := range t[i] {
			t[i][j] = a[j][i]
		}
	}
	return t
}

func task14() {
	a := randomMatrix(2, 4, 100)
	fmt.Fprintln(out, "Исходная:")
	printMatrix(a)
	fmt.Fprintln(out, "Транспонированная:")
	printMatrix(transpose(a))
}

// 15) (A) Дано число n. Создайте массив int A[n][n], и заполните его по следующему правилу:
// - Числа на диагонали, идущей из правого верхнего в левый нижний угол равны 1.
// - Числа, стоящие выше этой диагонали, равны 0.
// - Числа, стоящие ниже этой диагонали, равны 2.
// Полученный массив выведите на экран. Числа разделяйте одним пробелом.
func task15() {
	n := readInt()
	a := make([][]int, n)
	for i := 0; i < n; i++ {
		a[i] = make([]int, n)
		for j := 0; j < n; j++ {
			switch {
			case i+j == n-1:
				a[i][j] = 1
			case i+j < n-1:
				a[i][j] = 0
			default:
				a[i][j] = 2
			}
		}
	}
	for i := 0; i < n; i++ {
		for j := 0; j < n; j++ {
			if j > 0 {
				fmt.Fprint(out, " ")
			}
			fmt.Fprint(out, a[i][j])
		}
		fmt.Fprintln(out)
	}
}

// 16) (B) Дано число n и квадратный массив int A[n][n].
// Проверьте, является ли массив симметричным относительно главной диагонали.
// Программа должна выводить слово "yes" для симметричного массива и слово "no" для несимметричного.
func task16() {
	n := readInt()
	a := readMatrix(n, n)
	for i := 0; i < n; i++ {
		for j := i + 1; j < n; j++ {
			if a[i][j] != a[j][i] {
				fmt.Fprintln(out, "no")
				return
			}
		}
		fmt.Fprintln(out, "yes")
	}
}

// 17) (C) Состязания - 1.
// В метании молота состязается n спортсменов.
// Каждый из них сделал m бросков.
// Победителем считается тот спортсмен, у которого сумма результатов по всем броскам максимальна.
// Если перенумеровать спортсменов числами от 0 до n-1,
//
//	а попытки каждого из них – от 0 до m-1,
//	то на вход программа получает массив int
//
// A[n][m], состоящий из неотрицательных чисел.
// Программа должна определить максимальную сумму чисел в одной строке
//
//	и вывести на экран эту сумму и номер строки, для которой достигается эта сумма.
//
// Если таких строк несколько, то выводится номер наименьшей из них.
func task17() {
	n, m := readInt(), readInt()
	a := readMatrix(n, m)
	bestSum, bestRow := -1, -1
	for i := 0; i < n; i++ {
		s := 0
		for j := 0; j < m; j++ {
			s += a[i][j]
		}
		if s > bestSum {
			bestSum, bestRow = s, i
		}
	}
	fmt.Fprintln(out, bestSum)
	fmt.Fprintln(out, bestRow)
}

// 18) (D) Состязания - 2.
// Победителем соревнований объявляется тот спортсмен, у которого максимален наилучший результат по всем броскам.
// Таким образом, программа должна найти значение максимального элемента в данном массиве, а также его индексы
//
//	(то есть номер спортсмена и номер попытки).
//
// Программа выводит значение максимального элемента, затем номер строки и номер столбца, в котором он встречается.
// Если в массиве несколько максимальных элементов, то нужно вывести минимальный номер строки,
//
//	в которой встречается такой элемент, а если в этой строке таких элементов несколько,
//	то нужно вывести минимальный номер столбца.
func task18() {
	n, m := readInt(), readInt()
	a := readMatrix(n, m)
	maxV, mi, mj := a[0][0], 0, 0
	for i := 0; i < n; i++ {
		for j := 0; j < m; j++ {
			if a[i][j] > maxV {
				maxV, mi, mj = a[i][j], i, j
			}
		}
	}
	fmt.Fprintln(out, maxV, mi, mj)
}

// 19) (E) Состязания - 3.
// Будем считать, что побеждает спортсмен, у которого максимален наилучший бросок.
// Если таких несколько, то из них побеждает тот, у которого наилучшая сумма результатов по всем попыткам.
// Если и таких несколько, победителем считается спортсмен с минимальным номеров.
func task19() {
	n, m := readInt(), readInt()
	a := readMatrix(n, m)
	winner, winBest, winSum := -1, -1, -1
	for i := 0; i < n; i++ {
		best, sum := a[i][0], 0
		for _, v := range a[i] {
			sum += v
			if v > best {
				best = v
			}
		}
		if best > winBest || (best == winBest && sum > winSum) {
			winner, winBest, winSum = i, best, sum
		}
	}
	fmt.Fprintln(out, winner)
}

// 20) (F) Состязания - 4.
// Будем считать, что победитель определяется по лучшему результату.
// Определите количество участников состязаний, которые разделили первое место,
// 		то есть определите количество строк в массиве, которые содержат значение, равное наибольшему.
//
// 21) (G) Состязания - 5.
// Решите предыдущую задачу, но на экран выведите еще и номера спортсменов, разделивших первое место.
// Сначала программа выводит количество спортсменов, показавших наилучший результат,
// 		затем – их номера в порядке возрастания.

func rowsWithMax(a [][]int) []int {
	maxV := a[0][0]
	for _, row := range a {
		for _, v := range row {
			if v > maxV {
				maxV = v
			}
		}
	}
	var rows []int
	for i, row := range a {
		for _, v := range row {
			if v == maxV {
				rows = append(rows, i)
				break
			}
		}
	}
	return rows
}

func task20() {
	n, m := readInt(), readInt()
	fmt.Fprintln(out, len(rowsWithMax(readMatrix(n, m))))
}

func task21() {
	n, m := readInt(), readInt()
	rows := rowsWithMax(readMatrix(n, m))
	fmt.Fprintln(out, len(rows))
	for i, r := range rows {
		if i > 0 {
			fmt.Fprint(out, " ")
		}
		fmt.Fprint(out, r)
	}
	fmt.Fprintln(out)
}

func main() {
	defer out.Flush()

	if len(os.Args) < 2 {
		fmt.Fprintln(out, "Использование: go run main.go <номер задачи 13-21> [< input.txt]")
		return
	}

	tasks := map[string]func(){
		"13": task13, "14": task14, "15": task15, "16": task16, "17": task17,
		"18": task18, "19": task19, "20": task20, "21": task21,
	}

	task, ok := tasks[os.Args[1]]
	if !ok {
		fmt.Fprintln(out, "Нет такой задачи:", os.Args[1])
		return
	}
	task()
}
