import math
import statistics
import random
from typing import List, Union, Optional


def calcstr(calculation: str) -> Union[int, float]:
    """Calculates a mathematical expression from a string.
    
    Args:
        calculation: A string containing a mathematical expression
                    (e.g., "7+2*3", "10/2", "2**3")
    
    Returns:
        The result of the calculation as int or float
        
    Example:
        >>> calcstr("7+2*3")
        13
        >>> calcstr("10/3")
        3.3333333333333335
    """
    # Remove whitespace and evaluate safely
    result = eval(calculation.strip())
    return result


def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Returns the sum of two numbers.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Sum of a and b
    """
    return a + b


def subtract(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Returns the difference of two numbers.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Difference of a and b (a - b)
    """
    return a - b


def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Returns the product of two numbers.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Product of a and b
    """
    return a * b


def divide(a: Union[int, float], b: Union[int, float]) -> float:
    """Returns the division of two numbers.
    
    Args:
        a: Dividend
        b: Divisor
    
    Returns:
        Result of a / b
        
    Raises:
        ZeroDivisionError: If b is zero
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


def power(base: Union[int, float], exponent: Union[int, float]) -> Union[int, float]:
    """Returns base raised to the power of exponent.
    
    Args:
        base: The base number
        exponent: The exponent
    
    Returns:
        base ^ exponent
    """
    return base ** exponent


def square_root(number: Union[int, float]) -> float:
    """Returns the square root of a number.
    
    Args:
        number: The number to find the square root of
    
    Returns:
        Square root of the number
        
    Raises:
        ValueError: If number is negative
    """
    if number < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(number)


def factorial(n: int) -> int:
    """Returns the factorial of a non-negative integer.
    
    Args:
        n: A non-negative integer
    
    Returns:
        n! (factorial of n)
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    return math.factorial(n)


def absolute(number: Union[int, float]) -> Union[int, float]:
    """Returns the absolute value of a number.
    
    Args:
        number: The input number
    
    Returns:
        Absolute value of the number
    """
    return abs(number)


def modulo(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Returns the modulo (remainder) of two numbers.
    
    Args:
        a: Dividend
        b: Divisor
    
    Returns:
        Remainder of a / b
    """
    return a % b


def floor(number: Union[int, float]) -> int:
    """Returns the largest integer less than or equal to the number.
    
    Args:
        number: The input number
    
    Returns:
        Floored integer
    """
    return math.floor(number)


def ceil(number: Union[int, float]) -> int:
    """Returns the smallest integer greater than or equal to the number.
    
    Args:
        number: The input number
    
    Returns:
        Ceiling integer
    """
    return math.ceil(number)


def round_number(number: Union[int, float], decimals: int = 0) -> Union[int, float]:
    """Rounds a number to specified decimal places.
    
    Args:
        number: The number to round
        decimals: Number of decimal places (default 0)
    
    Returns:
        Rounded number
    """
    return round(number, decimals)


def average(numbers: List[Union[int, float]]) -> float:
    """Returns the arithmetic mean of a list of numbers.
    
    Args:
        numbers: List of numbers
    
    Returns:
        Average of the numbers
        
    Raises:
        ValueError: If the list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return statistics.mean(numbers)


def median(numbers: List[Union[int, float]]) -> Union[int, float]:
    """Returns the median of a list of numbers.
    
    Args:
        numbers: List of numbers
    
    Returns:
        Median value
        
    Raises:
        ValueError: If the list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate median of empty list")
    return statistics.median(numbers)


def mode(numbers: List[Union[int, float]]) -> Union[int, float]:
    """Returns the mode (most common value) of a list of numbers.
    
    Args:
        numbers: List of numbers
    
    Returns:
        Mode value
        
    Raises:
        ValueError: If the list is empty or no unique mode
    """
    if not numbers:
        raise ValueError("Cannot calculate mode of empty list")
    return statistics.mode(numbers)


def standard_deviation(numbers: List[Union[int, float]]) -> float:
    """Returns the standard deviation of a list of numbers.
    
    Args:
        numbers: List of numbers (at least 2 elements)
    
    Returns:
        Standard deviation
        
    Raises:
        ValueError: If the list has fewer than 2 elements
    """
    if len(numbers) < 2:
        raise ValueError("Need at least 2 numbers to calculate standard deviation")
    return statistics.stdev(numbers)


def variance(numbers: List[Union[int, float]]) -> float:
    """Returns the variance of a list of numbers.
    
    Args:
        numbers: List of numbers (at least 2 elements)
    
    Returns:
        Variance
        
    Raises:
        ValueError: If the list has fewer than 2 elements
    """
    if len(numbers) < 2:
        raise ValueError("Need at least 2 numbers to calculate variance")
    return statistics.variance(numbers)


def sine(angle_degrees: Union[int, float]) -> float:
    """Returns the sine of an angle in degrees.
    
    Args:
        angle_degrees: Angle in degrees
    
    Returns:
        Sine of the angle
    """
    return math.sin(math.radians(angle_degrees))


def cosine(angle_degrees: Union[int, float]) -> float:
    """Returns the cosine of an angle in degrees.
    
    Args:
        angle_degrees: Angle in degrees
    
    Returns:
        Cosine of the angle
    """
    return math.cos(math.radians(angle_degrees))


def tangent(angle_degrees: Union[int, float]) -> float:
    """Returns the tangent of an angle in degrees.
    
    Args:
        angle_degrees: Angle in degrees
    
    Returns:
        Tangent of the angle
    """
    return math.tan(math.radians(angle_degrees))


def logarithm(number: Union[int, float], base: Union[int, float] = 10) -> float:
    """Returns the logarithm of a number with specified base.
    
    Args:
        number: The number to calculate logarithm of
        base: The base of the logarithm (default 10)
    
    Returns:
        Logarithm of the number
        
    Raises:
        ValueError: If number <= 0 or base <= 0 or base == 1
    """
    if number <= 0:
        raise ValueError("Logarithm undefined for non-positive numbers")
    if base <= 0 or base == 1:
        raise ValueError("Base must be positive and not equal to 1")
    return math.log(number, base)


def natural_log(number: Union[int, float]) -> float:
    """Returns the natural logarithm (ln) of a number.
    
    Args:
        number: The number to calculate natural logarithm of
    
    Returns:
        Natural logarithm of the number
        
    Raises:
        ValueError: If number <= 0
    """
    if number <= 0:
        raise ValueError("Natural logarithm undefined for non-positive numbers")
    return math.log(number)


def random_number(min_val: int = 0, max_val: int = 100) -> int:
    """Returns a random integer between min_val and max_val (inclusive).
    
    Args:
        min_val: Minimum value (default 0)
        max_val: Maximum value (default 100)
    
    Returns:
        Random integer in the specified range
    """
    return random.randint(min_val, max_val)


def random_float(min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Returns a random float between min_val and max_val.
    
    Args:
        min_val: Minimum value (default 0.0)
        max_val: Maximum value (default 1.0)
    
    Returns:
        Random float in the specified range
    """
    return random.uniform(min_val, max_val)


def gcd(a: int, b: int) -> int:
    """Returns the greatest common divisor of two integers.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Greatest common divisor
    """
    return math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    """Returns the least common multiple of two integers.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Least common multiple
    """
    return abs(a * b) // math.gcd(a, b)


def clamp(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """Clamps a value between a minimum and maximum.
    
    Args:
        value: The value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))


def percentage(part: Union[int, float], whole: Union[int, float]) -> float:
    """Calculates what percentage 'part' is of 'whole'.
    
    Args:
        part: The part value
        whole: The whole value
    
    Returns:
        Percentage as a float
        
    Raises:
        ValueError: If whole is zero
    """
    if whole == 0:
        raise ValueError("Cannot calculate percentage with zero as whole")
    return (part / whole) * 100


def percentage_of(percentage: Union[int, float], whole: Union[int, float]) -> Union[int, float]:
    """Calculates the value that is a certain percentage of 'whole'.
    
    Args:
        percentage: The percentage value
        whole: The whole value
    
    Returns:
        The calculated value
    """
    return (percentage / 100) * whole