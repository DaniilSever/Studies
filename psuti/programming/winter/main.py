from math import (
  pi,
  sqrt,
  cos, acos,
  sin, asin,
  tan, atan,
  e,
  log, log10,
)


# ----- custom func -----

def ctg(x):
      return 1 / tan(x)

def arcctg(x: float):
  return pi/2 - atan(x)

# -----------------

def task_1():
  option_mapping = {
      1: lambda x: asin(e**-x) / ( sqrt(1 + cos(x)**2) * e**-x * (1 + sin(x)**2) ),
      2: lambda x: sqrt(e**-x * (1 + sin(x)**2) + asin(e**-x)) / (2 + sin(2*x)**2)**(1/3),
      3: lambda x: sin(e**x) / (atan(1 + sin(x)**2) * log(3 - cos(x)**2)),
      4: lambda x: ( (2**x)**(1/5) + e**-x * (1 + sin(x)**2) ) / sin(e**x),
      5: lambda x: ( (log(3 - cos(x)**2))**(1/5) + e**-x * (1 + sin(x)**2) ) / (2 + sin(2*x)**2)**(1/3),
      6: lambda x: (sin(e**x)**(1/5) + sqrt(1 + cos(x)**2)) / arcctg(x),
      7: lambda x: ((sin(e**x))**(1/5) + (2 + sin(2*x)**2)**(1/3)) / asin(e**-x),
      8: lambda x: ( atan(1 + sin(x)**2) * acos(e**-x) ) / arcctg(x),
      9: lambda x: ( log( sin(x)**2 + pi) + log10(1 + x**2)) / sqrt(2**x),
      10: lambda x: sqrt(acos(e**-x)) / ( 2**x + sin(e**x) ),
      11: lambda x: ( acos(e**-x) + sqrt(1 + cos(x)**2) ) / sqrt(e**-x * (1 + sin(x)**2)),
      12: lambda x: log10(1 + x**2) / ( acos(e**-x) * e**-x * (1 + sin(x)**2) ),
      13: lambda x: ( log10(1 + x**2)**(1/5) + e**-x * (1 + sin(x)**2) ) / (2 + sin(2*x)**2)**(1/3),
      14: lambda x: sqrt(sqrt(1 + cos(x)**2)) / (2**x + log10(1 + x**2)),
      15: lambda x: ( 2**x + arcctg(x) ) / sqrt((2 + sin(2*x)**2)**(1/3)),
      16: lambda x: ( (2+sin(2*x)**2)**(1/3) * sin(e**x) ) / atan(1 + sin(x)**2),
      17: lambda x: log((1 + e**-x), 2) + sqrt( log(3 - cos(x)**2) / ctg(x/pi) ),
      18: lambda x: sqrt(sqrt(1 + cos(x)**2)) / ( arcctg(x) + log(3 - cos(x)**2) ),
      19: lambda x: sqrt( atan(1 + sin(x)**2) + log((1+e**-x), 2)) / log(sin(x)**2 + pi),
      20: lambda x: ctg(x/pi) + sqrt(asin(e**-x) / log(3 - cos(x)**2)),
      21: lambda x: (2 + sin(2*x)**2)**(1/3) / ( asin(e**-x) * arcctg(x) ),
      22: lambda x: ( atan(1+ sin(x)**2) * e**-x * (1+sin(x)**2) ) / log(3 - cos(x)**2) ,
      23: lambda x: ( sin(e**x) + arcctg(x) ) / sqrt(log10(1 + x**2)),
      24: lambda x: sqrt(sin(e**x)) / ( asin(e**-x) + 2**x ),
      25: lambda x: ( atan(1 + sin(x)**2) + log((1+e**-x), 2) ) / sqrt(sqrt(1 + cos(x)**2)),
      26: lambda x: log((1 + e**-x), 2) + sqrt(sin(e**x) / asin(e**-x)),
      27: lambda x: ( log10(1+x**2) * sin(e**x) ) / log((1+e**-x), 2),
      28: lambda x: asin(e**-x) + sqrt(ctg(x/pi)/sqrt(1 + cos(x)**2)),
      29: lambda x: 2**x + sqrt(sin(e**x) / log(sin(x)**2 + pi)),
      30: lambda x: sqrt(sin(e**x) + log(3 - cos(x)**2)) / sqrt(1 + cos(x)**2)
  }

  OPTION = int(input("Вариант: "))
  X_VALUE = [0.5, 1]

  func = option_mapping.get(OPTION)
  for x in X_VALUE:
      print(f"y({x}): {round(func(x), 4)}")

# -----------------------------------------------------------------------------------

def task_2():
  z_mapping = {
      1: lambda x, y: ( (x + y**2)*(x**2 + y) ) / sqrt( (sin(x/pi) + y) * (e**x + e**-y) ) ,
      2: lambda x, y: ( sqrt(x**2 + y**2) * (x + y**2) ) / ( (x + tan(y/pi)**2)**2 * (x + 2*sin(y/pi)**2)**2 ),
      3: lambda x, y: ( (x**2 + y**2)**2 * (x**2 + e**y)**2 ) / ( (cos(x/(2*pi)) + sin(y/pi)) * sqrt(x + y + 1) ),
      4: lambda x, y: ( sqrt(sin(x)**2 + 3*y) * (x + log(y + pi))**2 ) / ( (x + y**2)**2 * (x**2 + y) ),
      5: lambda x, y: sqrt( (sin(x)**2 + 3*y) * (x + y**2) ) / ( (cos(x/(2*pi)) + sin(y/pi)) * (sin(x/pi)**2 + y**2)**2 ),
      6: lambda x, y: ( sqrt(x + atan(y)) * (cos(x/(2*pi)) + sin(y/pi)) ) / ( sqrt(e**x + e**-y) * (x + y +1)**2 ),
      7: lambda x, y: ( sqrt( (sin(x)**2 + 3*y) * (sin(x/pi)**2 + y**2) ) ) / ( sqrt(x**2 + y**2) * (e**x + e**-y)**2 ),
      8: lambda x, y: ( sqrt(x + 2*sin(y/pi)**2) * (sin(x/pi)**2 + y**2)**2 ) / ( (x + tan(y/pi)**2)**2 * (x + log(y + pi))**2 ),
      9: lambda x, y: ( (x+y**2) * sqrt(x**2 + y**2) ) / sqrt( (x + tan(y/pi)**2) * (x**2 + e**y) ),
      10: lambda x, y: ( (x + 2*sin(y/pi)**2) * (sin(x)**2 + 3*y) ) / ( (x**2 + y**2)**2 * (sin(x/pi)**2 + y**2) ),
      11: lambda x, y: ( sqrt(x + y + 1) * (e**x + e**-y) ) / ( (x + tan(y/pi)**2)**2 * sqrt(3*x + 2*y) ),
      12: lambda x, y: ( (x + 2*sin(y/pi)**2) * (e**x + e**-y)**2 ) / ( (sin(x/pi) + y) * sqrt(3*x + 2*y) ),
      13: lambda x, y: sqrt( (e**x + e**-y) * (sin(x/pi)**2 + y**2) ) / ( (x + 2*sin(y/pi)**2) * sqrt(sin(x/pi) + y) ),
      14: lambda x, y: sqrt( (x + y + 1) * (x + atan(y)) ) / ( (x**2 + y)**2 * sqrt(sin(x/pi)**2 + y**2) ),
      15: lambda x, y: ( (sin(x)**2 + 3*y) * (x**2 + y) ) / sqrt( (x + y**2) * (x + tan(y/pi)**2) ),
      16: lambda x, y: ( (sin(x)**2 + 3*y)**2 * sqrt(x + 2*sin(y/pi)**2) ) / ( (x + atan(y))**2 * (x**2 + y**2)**2 ),
      17: lambda x, y: ( (sin(x)**2 + 3*y)**2 * (x**2 + e**y)**2 ) / ( (x + tan(y/pi)**2) * sqrt(cos(x/(2*pi)) + sin(y/pi)) ),
      18: lambda x, y: ( (x + atan(y))**2 * sqrt(sin(x/pi)**2 + y**2) ) / ( (x**2 + e**y) * (x + tan(y/pi)**2)**2 ),
      19: lambda x, y: ( sqrt(x + y**2) * (x**2 + e**y)**2 ) / sqrt( (e**x + e**-y) * (x + log(y + pi)) ),
      20: lambda x, y: ( (cos(x/(2*pi)) + sin(y/pi)) * sqrt(x + atan(y)) ) / ( (sin(x/pi) + y)**2 * (x**2 + e**y)**2 ),
      21: lambda x, y: sqrt( (x + atan(y)) * (x + 2*sin(y/pi)**2) ) / ( (x + log(y + pi)) * (sin(x/pi)**2 + y**2)**2 ),
      22: lambda x, y: ( (sin(x/pi)**2 + y**2) * (x**2 + e**y)**2 ) / ( sqrt(sin(x)**2 + 3*y) * (cos(x/(2*pi)) + sin(y/pi)) ),
      23: lambda x, y: ( (x**2 + y) * sqrt(x + 2*sin(y/pi)**2) ) / ( sqrt(x + y + 1) * (e**x + e**-y) ),
      24: lambda x, y: ( (x**2 + y)**2 * sqrt(sin(x/pi) + y) ) / ( (x**2 + e**y) * (x + log(y + pi)) ),
      25: lambda x, y: ( (x + 2*sin(y/pi)**2) * (sin(x/pi)**2 + y**2)**2 ) / ( (e**x + e**-y)**2 * sqrt(x + y**2) ),
      26: lambda x, y: sqrt( (sin(x/pi)**2 + y**2) * (x + 2*sin(y/pi)**2) ) / ( sqrt(x**2 + y) * (x**2 + y**2) ),
      27: lambda x, y: ( (x**2 + e**y) * (sin(x/pi) + y)**2 ) / ( sqrt(3*x + 2*y) * (sin(x/pi)**2 + y**2)**2 ),
      28: lambda x, y: ( (x + y + 1) * sqrt(x + tan(y/pi)**2) ) / ( sqrt(sin(x/pi)**2 + y**2) * (x + log(y + pi))**2 ),
      29: lambda x, y: ( sqrt(x + atan(y)) * (x**2 + y**2)**2 ) / ( (x + y + 1) * sqrt(x + log(y + pi)) ),
      30: lambda x, y: ( sqrt(x + 2*sin(y/pi)**2) * (x + tan(y/pi)**2) ) / ( (x + y**2) * sqrt(sin(x)**2 + 3*y) )
  }

  f_mapping = {
      1: lambda a, b:  z_mapping[1]( (a + 2*b), (a*b + 1) ) + z_mapping[1]( (a + sqrt(b)), (a**2 + b) ) ,
      2: lambda a, b: z_mapping[2]( (sqrt(a) + sqrt(b)), (a**2 + b) ) + z_mapping[2]( (a + sqrt(b)), (3*a + b**2) ),
      3: lambda a, b: z_mapping[3]( (a + 2*b), (sqrt(a) + sqrt(b)) ) + z_mapping[3]( (sqrt(a) + b), (a**2 + b) ),
      4: lambda a, b: z_mapping[4]( (a + sqrt(b)), (a**2 + b) ) + z_mapping[4]( (a*b + 1), (3*a + b**2) ),
      5: lambda a, b: z_mapping[5]( (3*a + b**2), (a + 2*b) ) + z_mapping[5]( (a*b + 1), (sqrt(a) + b) ),
      6: lambda a, b: z_mapping[6]( (sqrt(a) + b), (2*a + b) ) + z_mapping[6]( (sqrt(a) + sqrt(b)), (a*b + 1) ),
      7: lambda a, b: z_mapping[7]( (2*a + b), (a*b + 1) ) + z_mapping[7]( (3*a + b**2), (a + 2*b) ),
      8: lambda a, b: z_mapping[8]( (a**2 + b), (a*b + 1) ) + z_mapping[8]( (3*a + b**2), (2*a + b) ),
      9: lambda a, b: z_mapping[9]( (3*a + b**2), (a*b + 1) ) + z_mapping[9]( (a + 2*b), (a**2 + b) ),
      10: lambda a, b: z_mapping[10]( (2*a + b), (3*a + b**2) ) + z_mapping[10]( (a**2 + b), (sqrt(a) + sqrt(b)) ),
      11: lambda a, b: z_mapping[11]( (a*b + 1), (a + 2*b) ) + z_mapping[11]( (2*a + b), (sqrt(a) + b) ),
      12: lambda a, b: z_mapping[12]( (sqrt(a) + sqrt(b)), (a**2 + b) ) + z_mapping[12]( (3*a + b**2), (sqrt(a) + b) ),
      13: lambda a, b: z_mapping[13]( (sqrt(a) + sqrt(b)), (3*a + b**2) ) + z_mapping[13]( (a + sqrt(b)), (2*a + b) ),
      14: lambda a, b: z_mapping[14]( (3*a + b**2), (a**2 + b) ) + z_mapping[14]( (a + 2*b), (2*a + b) ),
      15: lambda a, b: z_mapping[15]( (3*a + b**2), (a + 2*b)  ) + z_mapping[15]( (a*b + 1), (a**2 + b) ),
      16: lambda a, b: z_mapping[16]( (3*a + b**2), (2*a + b) ) + z_mapping[16]( (a**2 + b), (sqrt(a) + b) ),
      17: lambda a, b: z_mapping[17]( (sqrt(a) + sqrt(b)), (2*a + b) ) + z_mapping[17]( (sqrt(a) + b), (a + sqrt(b)) ),
      18: lambda a, b: z_mapping[18]( (2*a + b), (a + sqrt(b)) ) + z_mapping[18]( (a**2 + b), (a + 2*b) ),
      19: lambda a, b: z_mapping[19]( (a + sqrt(b)), (a**2 + b) ) + z_mapping[19]( (a*b + 1), (3*a + b**2) ),
      20: lambda a, b: z_mapping[20]( (sqrt(a) + b), (a + sqrt(b)) ) + z_mapping[20]( (sqrt(a) + sqrt(b)), (a*b + 1) ),
      21: lambda a, b: z_mapping[21]( (sqrt(a) + b), (2*a + b) ) + z_mapping[21]( (a*b + 1), (3*a + b**2) ),
      22: lambda a, b: z_mapping[22]( (a + sqrt(b)), (3*a + b**2) ) + z_mapping[22]( (a**2 + b), (sqrt(a) + sqrt(b)) ),
      23: lambda a, b: z_mapping[23]( (a**2 + b), (a + sqrt(b)) ) + z_mapping[23]( (sqrt(a) + sqrt(b)), (a*b + 1) ),
      24: lambda a, b: z_mapping[24]( (a**2 + b), (a + 2*b) ) + z_mapping[24]( (sqrt(a) + b), (2*a + b) ),
      25: lambda a, b: z_mapping[25]( (2*a + b), (a*b + 1) ) + z_mapping[25]( (a + sqrt(b)), (a**2 + b) ),
      26: lambda a, b: z_mapping[26]( (sqrt(a) + sqrt(b)), (a*b + 1) ) + z_mapping[26]( (sqrt(a) + b), (a**2 + b) ),
      27: lambda a, b: z_mapping[27]( (a**2 + b), (a + 2*b) ) + z_mapping[27]( (a + sqrt(b)), (sqrt(a) + sqrt(b)) ),
      28: lambda a, b: z_mapping[28]( (sqrt(a) + sqrt(b)), (a + 2*b) ) + z_mapping[28]( (sqrt(a) + b), (a*b + 1) ),
      29: lambda a, b: z_mapping[29]( (2*a + b), (a**2 + b) ) + z_mapping[29]( (a*b + 1), (sqrt(a) + sqrt(b)) ),
      30: lambda a, b: z_mapping[30]( (a*b + 1), (3*a + b**2) ) + z_mapping[30]( (sqrt(a) + sqrt(b)), (a + 2*b) )
  }

  OPTION = int(input("Вариант: "))
  AB_VALUE = [ (0.5, 0.5), (0.5, 1), (1, 0.5), (1, 1) ]

  func = f_mapping.get(OPTION)
  for values in AB_VALUE:
      print(f"f{values}: {round(func(*values), 4)}")

if __name__ == "__main__":
  TASK = int(input("Заданние: "))

  match TASK:
      case 1:
          task_1()
      case 2:
          task_2()