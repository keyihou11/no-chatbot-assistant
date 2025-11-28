# Example Python file with intentional issues for testing

def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    total = 0
    count = 0
    
    for num in numbers:
        total += num
        count += 1
    
    unused_var = 42  # This will trigger W0612
    
    if count == 0:
        return 0
    
    average = total / count
    return average


def greet(name):
    """Greet a person by name."""
    message = f"Hello, {name}!"
    print(message)
    x = 10  # Another unused variable W0612
    

class Calculator:
    """Simple calculator class."""
    
    def __init__(self):
        self.result = 0
        self.temp = None  # Unused attribute
    
    def add(self, a, b):
        """Add two numbers."""
        self.result = a + b
        return self.result
    
    def subtract(self,a,b):  # Missing space after comma - C0326
        """Subtract b from a."""
        return a-b  # Missing spaces around operator


if __name__ == "__main__":
    numbers = [1, 2, 3, 4, 5]
    avg = calculate_average(numbers)
    print(f"Average: {avg}")
    
    greet("World")
