from lib.TriangleChecker import TriangleChecker

# 1) Можно построить
triangle = TriangleChecker(60, 30, 80)
triangle.is_triangle()
# 2) Нельзя построить
triangle = TriangleChecker(10, 90, 80)
triangle.is_triangle()
# 3) Отрицательные числа
triangle = TriangleChecker(60, -30, 80)
triangle.is_triangle()
# 4) Не правильный тип данных
triangle = TriangleChecker(60, "Hello", 80)
triangle.is_triangle()
