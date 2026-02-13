#!/usr/bin/env python3
"""Sample Python file for testing grep_clone."""


def hello_world():
    """Print hello message."""
    print("Hello, World!")


def calculate_factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)


class Calculator:
    """Simple calculator class."""

    def __init__(self):
        self.history = []

    def add(self, a, b):
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a, b):
        """Subtract b from a."""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result


def main():
    calc = Calculator()
    print(calc.add(5, 3))
    print(calc.subtract(10, 4))
    hello_world()


if __name__ == "__main__":
    main()
