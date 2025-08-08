# Testing Python concepts

# Logging decorator
def my_decorator(func):
    def wrapper(name):
        print(f"Calling {func.__name__} with arguments {name}")
        func(name)
    return wrapper

@my_decorator
def greet(name):
    print(f"Hello, {name}")

#greet("Roberto")


# Simple decorator
def simple_decorator(func):
    def wrapper():
        print("Starting function")
        func()
        print("Function ended")
    return wrapper

@simple_decorator
def say():
    print("Hello")

say()
