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
		parts := make([]string, fm.cols)
		for j := 0; j < fm.cols; j++ {
			parts[j] = fmt.Sprintf("%3d", fm.Get(i, j))
		}
		fmt.Println(strings.Join(parts, " "))
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

type TaskHardMatrix struct{}

func (TaskHardMatrix) Run() {
	fmt.Println("Через пробел номер задачи и размер (default 4)")

	br := bufio.NewReader(os.Stdin)
	line, _ := br.ReadString('\n')
	parts := strings.Fields(line)

	if len(parts) == 0 {
		fmt.Println("<номер задачи 22-26>")
		return
	}

	taskNum, err := strconv.Atoi(parts[0])
	if err != nil {
		fmt.Println("<номер задачи 22-26>")
		return
	}

	num := 4
	if len(parts) > 1 {
		v, err := strconv.Atoi(parts[1])
		if err != nil {
			fmt.Println("Размер должен быть целым числом >= 1")
			return
		}
		num = v
	}

	if len(strconv.Itoa(taskNum)) < 2 {
		fmt.Println("<номер задачи 22-26>")
		return
	}
	if num < 1 {
		fmt.Println("Размер должен быть целым числом >= 1")
		return
	}

	tm := TaskHardMatrix{}
	switch taskNum {
	case 22:
		tm.task22(num)
	case 23:
		tm.task23(num)
	case 24:
		tm.task24(num)
	case 25:
		tm.task25(num)
	case 26:
		tm.task26()
	default:
		fmt.Println("Нет такой задачи:", taskNum)
	}
}

// 22) Создайте матрицу A[2*N+1]x[2*N+1], заполненную по спирали от центра по часовой стрелке, начиная с 0

func (TaskHardMatrix) task22(n int) {
	spiral := func(n int) Matrix {
		size := 2*n + 1
		a := make(Matrix, size)
		for i := range a {
			a[i] = make([]int, size)
		}
		dirs := [4][2]int{{0, 1}, {1, 0}, {0, -1}, {-1, 0}}

		r, c := n, n
		value, step, d := 0, 1, 0
		total := size * size

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
	printMatrix(spiral(n))
}

// 23) Для случайной матрицы осуществить ее абсолютную сортировку (от [0][0] к [n-1][n-1]).
func (TaskHardMatrix) task23(n int) {
	absoluteSort := func(a Matrix) {
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

	a := randomMatrix(n, n+1, 100)
	fmt.Println("До:")
	printMatrix(a)
	absoluteSort(a)
	fmt.Println("После:")
	printMatrix(a)
}

// 24) Отсортировать столбцы матрицы по результату среднего арифметического элементов.
func (TaskHardMatrix) task24(n int) {
	swapColumns := func(a Matrix, x, y int) {
		for _, row := range a {
			row[x], row[y] = row[y], row[x]
		}
	}

	columnMeans := func(a Matrix) []float64 {
		nRows, m := len(a), len(a[0])
		means := make([]float64, 0, m)
		for j := 0; j < m; j++ {
			s := 0
			for i := 0; i < nRows; i++ {
				s += a[i][j]
			}
			means = append(means, float64(s)/float64(nRows))
		}
		return means
	}

	sortColumnsByMean := func(a Matrix) {
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

	fmtMeans := func(means []float64) string {
		parts := make([]string, len(means))
		for i, x := range means {
			parts[i] = fmt.Sprintf("%.2f", x)
		}
		return "[" + strings.Join(parts, " ") + "]"
	}

	a := randomMatrix(n, n+1, 100)
	fmt.Println("До:")
	printMatrix(a)
	fmt.Println("Средние:", fmtMeans(columnMeans(a)))
	sortColumnsByMean(a)
	fmt.Println("После:")
	printMatrix(a)
	fmt.Println("Средние:", fmtMeans(columnMeans(a)))
}

//  25. Создать матрицу NxN, заполненную случайными числами, но чтобы около 25% элементов матрицы были = 0.
//     Расположение нулей должно быть случайным. Подсчитать количество нулей.
func (TaskHardMatrix) task25(n int) {
	matrixWithZeros := func(n int) Matrix {
		a := make(Matrix, n)
		for i := range a {
			a[i] = make([]int, n)
			for j := range a[i] {
				a[i][j] = rand.Intn(99) + 1
			}
		}
		zeros := n * n / 4
		for _, p := range rand.Perm(n * n)[:zeros] {
			a[p/n][p%n] = 0
		}
		return a
	}

	countZeros := func(a Matrix) int {
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
func (TaskHardMatrix) task26() {
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
	TaskHardMatrix{}.Run()
}
