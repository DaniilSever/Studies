def three_args(value_1: any = None, value_2: any = None, value_3: any = None):
    if any((value_1, value_2, value_3)) is None:
        pass
    else:
        print("Переданные аргументы:", end=' ')
        if value_1:
            print(f"var1 = {value_1}", end=' ')
        if value_2:
            print(f"var2 = {value_2}", end=' ')
        if value_3:
            print(f"var3 = {value_3}")


three_args(value_1=1, value_2=True, value_3='b')
