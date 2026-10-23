package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"strings"
)

type Matrix [][]int

// tools
var stdinScanner = newStdinScanner()

func newStdinScanner() *bufio.Scanner {
	s := bufio.NewScanner(os.Stdin)
	s.Buffer(make([]byte, 1<<20), 1<<20)
	s.Split(bufio.ScanWords)
	return s
}

type Reader struct {}

func (Reader) nextInt() int {
	stdinScanner.Scan()
	x, _ := strconv.Atoi(stdinScanner.Text())
	return x
}

func (Reader) nextString() string {
	stdinScanner.Scan()
	return stdinScanner.Text()
}

func (r Reader) matrix(n, m int) Matrix {
	a := make(Matrix, n)
	for i := range a {
		a[i] = make([]int, m)
		for j := range a[i] {
			a[i][j] = r.nextInt()
		}
	}
	return a
}

func randomMatrix(n, m, maxVal int) Matrix {
	a := make(Matrix, n)
	for i := range a {
		a[i] = make([]int, m)
		for j := range a[i] {
			a[i][j] = rand.Intn(maxVal)
		}
	}
	return a
}

func printMatrix(a Matrix) {
	for _, row := range a {
		parts := make([]string, len(row))
		for i, v := range row {
			parts[i] = fmt.Sprintf("%3d", v)
		}
		fmt.Println(strings.Join(parts, " "))
	}
}

func transpose(a Matrix) Matrix {
	n, m := len(a), len(a[0])
	t := make(Matrix, m)
	for i := range t {
		t[i] = make([]int, n)
		for j := range t[i] {
			t[i][j] = a[j][i]
		}
	}
	return t
}

func rowsWithMax(a Matrix) []int {
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

// Запуск всех функций
type TaskMatrix struct{}

func (TaskMatrix) Run() {
	tasks := map[string]func(){
		"13": TaskMatrix{}.task13,
		"14": TaskMatrix{}.task14,
		"15": TaskMatrix{}.task15,
		"16": TaskMatrix{}.task16,
		"17": TaskMatrix{}.task17,
		"18": TaskMatrix{}.task18,
		"19": TaskMatrix{}.task19,
		"20": TaskMatrix{}.task20,
		"21": TaskMatrix{}.task21,
	}


	num := Reader{}.nextString()
	if len(num) < 2 {
		fmt.Println("<номер задачи 13-21>")
		return
	}
	task, ok := tasks[num]
	if !ok {
		fmt.Println("Нет такой задачи:", num)
		return
	}
	task()
}

// --------------Tasks----------------

//  13. Создать матрицу из случайных чисел и вывести построчно с
//     форматным выводом, выделив 3 символа на каждый столбец и пробел в качестве разделителя
func (TaskMatrix) task13() {
	printMatrix(randomMatrix(3, 4, 300))
}

// 14) Осуществить транспонирование случайной матрицы (создать новую матрицу - транспонированную из предыдущей).
func (TaskMatrix) task14() {
	a := randomMatrix(3, 5, 200)
	fmt.Println("Исходная:")
	printMatrix(a)
	fmt.Println("\nТранспонированная:")
	printMatrix(transpose(a))
}

// 15) (A) Дано число n. Создайте массив int A[n][n], и заполните его по следующему правилу:
// - Числа на диагонали, идущей из правого верхнего в левый нижний угол равны 1.
// - Числа, стоящие выше этой диагонали, равны 0.
// - Числа, стоящие ниже этой диагонали, равны 2.
// Полученный массив выведите на экран. Числа разделяйте одним пробелом.
func (TaskMatrix) task15() {
	n := Reader{}.nextInt()
	for i := 0; i < n; i++ {
		row := make([]int, n)
		for j := 0; j < n; j++ {
			switch {
			case i+j == n-1:
				row[j] = 1
			case i+j < n-1:
				row[j] = 0
			default:
				row[j] = 2
			}
		}
		parts := make([]string, n)
		for k, v := range row {
			parts[k] = strconv.Itoa(v)
		}
		fmt.Println(strings.Join(parts, " "))
	}
}

// 16) (B) Дано число n и квадратный массив int A[n][n].
// Проверьте, является ли массив симметричным относительно главной диагонали.
// Программа должна выводить слово "yes" для симметричного массива и слово "no" для несимметричного.
func (TaskMatrix) task16() {
	r := Reader{}
	n := r.nextInt()
	a := r.matrix(n, n)
	for i := 0; i < n; i++ {
		for j := i + 1; j < n; j++ {
			if a[i][j] != a[j][i] {
				fmt.Println("no")
				return
			}
		}
	}
	fmt.Println("yes")
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
func (TaskMatrix) task17() {
	r := Reader{}
	n, m := r.nextInt(), r.nextInt()
	a := r.matrix(n, m)
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
	fmt.Println(bestSum)
	fmt.Println(bestRow)
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
func (TaskMatrix) task18() {
	r := Reader{}
	n, m := r.nextInt(), r.nextInt()
	a := r.matrix(n, m)
	maxV, mi, mj := a[0][0], 0, 0
	for i := 0; i < n; i++ {
		for j := 0; j < m; j++ {
			if a[i][j] > maxV {
				maxV, mi, mj = a[i][j], i, j
			}
		}
	}
	fmt.Println(maxV, mi, mj)
}

// 19) (E) Состязания - 3.
// Будем считать, что побеждает спортсмен, у которого максимален наилучший бросок.
// Если таких несколько, то из них побеждает тот, у которого наилучшая сумма результатов по всем попыткам.
// Если и таких несколько, победителем считается спортсмен с минимальным номеров.
func (TaskMatrix) task19() {
	r := Reader{}
	n, m := r.nextInt(), r.nextInt()
	a := r.matrix(n, m)
	winner, winBest, winSum := -1, -1, -1
	for i := 0; i < n; i++ {
		best, total := a[i][0], 0
		for _, v := range a[i] {
			total += v
			if v > best {
				best = v
			}
		}
		if best > winBest || (best == winBest && total > winSum) {
			winner, winBest, winSum = i, best, total
		}
	}
	fmt.Println(winner)
}

// 20) (F) Состязания - 4.
// Будем считать, что победитель определяется по лучшему результату.
// Определите количество участников состязаний, которые разделили первое место,
// 		то есть определите количество строк в массиве, которые содержат значение, равное наибольшему.
func (TaskMatrix) task20() {
	r := Reader{}
	n, m := r.nextInt(), r.nextInt()
	fmt.Println(len(rowsWithMax(r.matrix(n, m))))
}

// 21) (G) Состязания - 5.
// Решите предыдущую задачу, но на экран выведите еще и номера спортсменов, разделивших первое место.
// Сначала программа выводит количество спортсменов, показавших наилучший результат,
// 		затем – их номера в порядке возрастания.
func (TaskMatrix) task21() {
	r := Reader{}
	n, m := r.nextInt(), r.nextInt()
	rows := rowsWithMax(r.matrix(n, m))
	fmt.Println(len(rows))
	parts := make([]string, len(rows))
	for i, v := range rows {
		parts[i] = strconv.Itoa(v)
	}
	fmt.Println(strings.Join(parts, " "))
}

func main() {
	TaskMatrix{}.Run()
}
