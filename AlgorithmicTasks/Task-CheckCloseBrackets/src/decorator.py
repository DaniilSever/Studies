from time import time


def run_time(func):
    def wrapper(*args, **kwargs):
        start_millisec = float(time() * 1000)
        result = func(*args, **kwargs)
        end_millisec = float(time() * 1000)
        middle = end_millisec - start_millisec
        print(f"Time taken: {round(middle, 4)} millisecond, result:", end=" ")
        return result

    return wrapper
