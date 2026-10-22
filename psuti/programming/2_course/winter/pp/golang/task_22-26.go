package main

import (
	"fmt"
	"math/rand"
	"os"
	"strconv"
)

// tools
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
				fmt.Print(" ")
			}
			fmt.Printf("%3d", v)
		}
		fmt.Println()
	}
}

// 22) Создайте матрицу A[2*N+1]x[2*N+1], заполненную по спирали от центра по часовой стрелке, начиная с 0
func spiral(n int) [][]int {
	size := 2*n + 1
	a := make([][]int, size)
	for i := range a {
		a[i] = make([]int, size)
	}

	dirs := [4][2]int{{0, 1}, {1, 0}, {0, -1}, {-1, 0}}

	r, c := n, n
	value := 0
	a[r][c] = value
	total := size * size
	step := 1
	d := 0

	for value < total-1 {
		for rep := 0; rep < 2; rep++ {
			for s := 0; s < step; s++ {
				r += dirs[d][0]
				c += dirs[d][1]
				if r < 0 || r >= size || c < 0 || c >= size {
					return a
				}
				value++
				a[r][c] = value
			}
			d = (d + 1) % 4
		}
		step++
	}
	return a
}

func task22(n int) {
	printMatrix(spiral(n))
}

// 23) Для случайной матрицы осуществить ее абсолютную сортировку (от [0][0] к [n-1][n-1]).
func absoluteSort(a [][]int) {
	m := len(a[0])
	total := len(a) * m
	get := func(k int) int { return a[k/m][k%m] }
	set := func(k, v int) { a[k/m][k%m] = v }

	for i := 1; i < total; i++ {
		key := get(i)
		j := i - 1
		for j >= 0 && get(j) > key {
			set(j+1, get(j))
			j--
		}
		set(j+1, key)
	}
}

func task23(n int) {
	a := randomMatrix(n, n+1, 100)
	fmt.Println("До:")
	printMatrix(a)
	absoluteSort(a)
	fmt.Println("После:")
	printMatrix(a)
}

// 24) Отсортировать столбцы матрицы по результату среднего арифметического элементов.
func columnMeans(a [][]int) []float64 {
	n, m := len(a), len(a[0])
	means := make([]float64, m)
	for j := 0; j < m; j++ {
		sum := 0
		for i := 0; i < n; i++ {
			sum += a[i][j]
		}
		means[j] = float64(sum) / float64(n)
	}
	return means
}

func swapColumns(a [][]int, x, y int) {
	for i := range a {
		a[i][x], a[i][y] = a[i][y], a[i][x]
	}
}

func sortColumnsByMean(a [][]int) {
	means := columnMeans(a)
	m := len(means)
	for i := 0; i < m-1; i++ {
		minIdx := i
		for j := i + 1; j < m; j++ {
			if means[j] < means[minIdx] {
				minIdx = j
			}
		}
		if minIdx != i {
			swapColumns(a, i, minIdx)
			means[i], means[minIdx] = means[minIdx], means[i]
		}
	}
}

func task24(n int) {
	a := randomMatrix(n, n+1, 100)
	fmt.Println("До:")
	printMatrix(a)
	fmt.Printf("Средние: %.2f\n", columnMeans(a))
	sortColumnsByMean(a)
	fmt.Println("После:")
	printMatrix(a)
	fmt.Printf("Средние: %.2f\n", columnMeans(a))
}

//  25. Создать матрицу NxN, заполненную случайными числами, но чтобы около 25% элементов матрицы были = 0.
//     Расположение нулей должно быть случайным. Подсчитать количество нулей.
func matrixWithZeros(n int) [][]int {
	a := make([][]int, n)
	for i := range a {
		a[i] = make([]int, n)
		for j := range a[i] {
			a[i][j] = rand.Intn(99) + 1
		}
	}
	zeros := n * n / 4
	positions := rand.Perm(n * n)
	for _, p := range positions[:zeros] {
		a[p/n][p%n] = 0
	}
	return a
}

func countZeros(a [][]int) int {
	cnt := 0
	for _, row := range a {
		for _, v := range row {
			if v == 0 {
				cnt++
			}
		}
	}
	return cnt
}

func task25(n int) {
	a := matrixWithZeros(n)
	printMatrix(a)
	fmt.Printf("Нулей: %d из %d\n", countZeros(a), n*n)
}

// 26) Создать одномерный массив, который содержит последовательную запись элементов матрицы NxM.
// Обеспечить интерфейс работы с данным массивом как с матрицей:
//
//	а) вывод в виде матрицы NxM;
//	б) изменение элемента с координатами x, y;
//	в) вычисление суммы по строкам, по столбцам.
//
// Например, матрица 2x3 из 1й задачи будет храниться в виде массива из 6 элементов:
//
//	{44, 31, 15, 11, 221, 78}, т.е. каждую новую строку матрицы мы записываем последовательно в массив.
//
// “Матричные” координаты 5го элемента массива со значением 221 будут [1][1].
type FlatMatrix struct {
	rows, cols int
	data       []int
}

func NewFlatMatrix(rows, cols int, data []int) *FlatMatrix {
	if data == nil {
		data = make([]int, rows*cols)
	}
	return &FlatMatrix{rows: rows, cols: cols, data: data}
}

func (fm *FlatMatrix) index(row, col int) int {
	return row*fm.cols + col
}

func (fm *FlatMatrix) Get(row, col int) int {
	return fm.data[fm.index(row, col)]
}

func (fm *FlatMatrix) Set(row, col, value int) {
	fm.data[fm.index(row, col)] = value
}

func (fm *FlatMatrix) Coords(k int) (int, int) {
	return k / fm.cols, k % fm.cols
}

func (fm *FlatMatrix) Print() {
	for i := 0; i < fm.rows; i++ {
		for j := 0; j < fm.cols; j++ {
			if j > 0 {
				fmt.Print(" ")
			}
			fmt.Printf("%3d", fm.Get(i, j))
		}
		fmt.Println()
	}
}

func (fm *FlatMatrix) RowSums() []int {
	sums := make([]int, fm.rows)
	for i := 0; i < fm.rows; i++ {
		for j := 0; j < fm.cols; j++ {
			sums[i] += fm.Get(i, j)
		}
	}
	return sums
}

func (fm *FlatMatrix) ColSums() []int {
	sums := make([]int, fm.cols)
	for i := 0; i < fm.rows; i++ {
		for j := 0; j < fm.cols; j++ {
			sums[j] += fm.Get(i, j)
		}
	}
	return sums
}

func task26() {
	fm := NewFlatMatrix(2, 3, []int{44, 31, 15, 11, 221, 78})
	fmt.Println("Хранение:", fm.data)
	fmt.Println("а) Вывод матрицей:")
	fm.Print()

	r, c := fm.Coords(4)
	fmt.Printf("Элемент data[4] = %d имеет координаты [%d][%d]\n", fm.data[4], r, c)

	fm.Set(0, 2, 99)
	fmt.Println("б) После Set(0, 2, 99):")
	fm.Print()
	fmt.Println("   Хранение:", fm.data)

	fmt.Println("в) Суммы по строкам: ", fm.RowSums())
	fmt.Println("   Суммы по столбцам:", fm.ColSums())
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Использование: go run . <номер задачи 22-26> [размер N]")
		return
	}

	n := 4
	if len(os.Args) >= 3 {
		v, err := strconv.Atoi(os.Args[2])
		if err != nil || v < 1 {
			fmt.Println("Размер должен быть целым числом >= 1")
			return
		}
		n = v
	}

	switch os.Args[1] {
	case "22":
		task22(n)
	case "23":
		task23(n)
	case "24":
		task24(n)
	case "25":
		task25(n)
	case "26":
		task26()
	default:
		fmt.Println("Нет такой задачи:", os.Args[1])
	}
}
