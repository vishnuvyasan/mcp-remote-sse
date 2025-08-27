class Calculator:
    """
    A simple calculator class that provides basic arithmetic operations.
    """
    
    def add(self, a: float, b: float) -> float:
        """
        Add two numbers and return the result.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The sum of a and b
        """
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """
        Subtract b from a and return the result.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The difference between a and b
        """
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers and return the result.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The product of a and b
        """
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """
        Divide a by b and return the result.
        
        Args:
            a: First number (dividend)
            b: Second number (divisor)
            
        Returns:
            The quotient of a divided by b
            
        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

# Made with Bob
