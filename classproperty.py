class classproperty:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func(owner)


class MyClass:
    _value = 42

    @classproperty
    def value(cls):
        return cls._value

    @classproperty
    def description(cls):
        return f"MyClass with value {cls._value}"


# Example usage
if __name__ == "__main__":
    print(MyClass.value)  # Output: 42
    print(MyClass.description)  # Output: MyClass with value 42