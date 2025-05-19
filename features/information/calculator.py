"""
Calculator capabilities for AREN
This module handles math calculation requests.
"""

import re
import math
from utils.logging_utils import logger

def calculate(expression):
    """
    Evaluate a mathematical expression safely
    
    Args:
        expression (str): Mathematical expression to evaluate
        
    Returns:
        str: Result of the calculation or error message
    """
    try:
        # Handle percentage calculations specially
        percentage_result = handle_percentage_calculation(expression)
        if percentage_result:
            return percentage_result
            
        # Clean the expression
        cleaned_expr = clean_expression(expression)
        
        if not cleaned_expr:
            return "I couldn't parse that expression. Please try again with a simple math problem. (Mujhe yeh ganitiya samasya samajh nahi aayi.)"
        
        # Handle special functions
        cleaned_expr = handle_special_functions(cleaned_expr)
        
        # Safely evaluate the expression
        # We use eval() but only after thoroughly sanitizing the input
        # In a production system, consider using a dedicated parsing library
        result = eval(cleaned_expr, {"__builtins__": None}, {"sqrt": math.sqrt, "sin": math.sin, 
                                                           "cos": math.cos, "tan": math.tan,
                                                           "pi": math.pi, "e": math.e,
                                                           "log": math.log, "log10": math.log10,
                                                           "abs": abs})
        
        # Format the result
        if isinstance(result, (int, float)):
            # Format integers without decimal, float with up to 6 decimal places
            if result == int(result):
                formatted_result = str(int(result))
            else:
                formatted_result = f"{result:.6f}".rstrip('0').rstrip('.')
                
            logger.info(f"Calculated: {expression} = {formatted_result}")
            
            # Create response with both expression and result
            response = f"{expression} = {formatted_result}"
            
            # Add simple Hindi translation for basic operations
            if "+" in expression:
                response += f"\n(Jod: {formatted_result})"
            elif "-" in expression and not expression.strip().startswith("-"):
                response += f"\n(Ghatav: {formatted_result})"
            elif "*" in expression or "×" in expression:
                response += f"\n(Gunan: {formatted_result})"
            elif "/" in expression or "÷" in expression:
                response += f"\n(Bhag: {formatted_result})"
            
            return response
        else:
            logger.warning(f"Calculation result is not a number: {result}")
            return "Sorry, I couldn't calculate that. (Mujhe yeh ganitiya samasya hal nahi kar saka.)"
            
    except ZeroDivisionError:
        return "Cannot divide by zero. (Shunya se bhag nahi ho sakta.)"
    except (SyntaxError, ValueError, TypeError, NameError) as e:
        logger.error(f"Calculation error: {str(e)}")
        return "Sorry, I couldn't calculate that. Please check your expression. (Mujhe yeh ganitiya samasya hal nahi kar saka.)"
    except Exception as e:
        logger.error(f"Unexpected calculation error: {str(e)}")
        return "Something went wrong with the calculation. (Ganana mein kuch gadbad hui.)"

def handle_percentage_calculation(expression):
    """
    Handle percentage calculations like "X% of Y" specially
    
    Args:
        expression (str): Expression to check for percentage calculation
        
    Returns:
        str or None: Calculation result or None if not a percentage calculation
    """
    # Match patterns like "15% of 240" or "what is 20 percent of 500"
    percentage_patterns = [
        r'(\d+\.?\d*)%\s+(?:of|ka)\s+(\d+\.?\d*)',  # 15% of 240
        r'(?:what\s+is|calculate|compute)\s+(\d+\.?\d*)\s*%\s+(?:of|ka)\s+(\d+\.?\d*)',  # what is 15% of 240
        r'(\d+\.?\d*)\s+(?:percent|percentage)\s+(?:of|ka)\s+(\d+\.?\d*)',  # 15 percent of 240
        r'(\d+\.?\d*)\s+(?:of|ka)\s+(\d+\.?\d*)\s+(?:percent|percentage)'  # 15 of 240 percent
    ]
    
    expression_lower = expression.lower()
    
    for pattern in percentage_patterns:
        match = re.search(pattern, expression_lower)
        if match:
            try:
                percentage = float(match.group(1))
                base_value = float(match.group(2))
                result = (percentage / 100) * base_value
                
                # Format result
                if result == int(result):
                    formatted_result = str(int(result))
                else:
                    formatted_result = f"{result:.6f}".rstrip('0').rstrip('.')
                
                logger.info(f"Calculated percentage: {percentage}% of {base_value} = {formatted_result}")
                
                # Make response
                response = f"{percentage}% of {base_value} = {formatted_result}"
                return response
            except Exception as e:
                logger.error(f"Error in percentage calculation: {str(e)}")
                return None
    
    return None

def clean_expression(expression):
    """
    Clean and normalize a mathematical expression
    
    Args:
        expression (str): Raw mathematical expression
        
    Returns:
        str: Cleaned expression ready for evaluation
    """
    # Remove any non-math characters
    expression = re.sub(r'[^0-9+\-*/().,%\^\s]', '', expression)
    
    # Replace common math symbols with their Python equivalents
    expression = expression.replace('×', '*').replace('÷', '/').replace('^', '**').replace('%', '/100')
    
    # Replace commas used as decimal separators
    expression = expression.replace(',', '.')
    
    # Handle implicit multiplication (e.g., 2(3+4) -> 2*(3+4))
    expression = re.sub(r'(\d)(\()', r'\1*\2', expression)
    
    return expression.strip()

def handle_special_functions(expression):
    """
    Handle special mathematical functions in the expression
    
    Args:
        expression (str): Cleaned mathematical expression
        
    Returns:
        str: Expression with special functions properly formatted for evaluation
    """
    # Replace square roots (sqrt)
    expression = re.sub(r'sqrt\s*\(', 'sqrt(', expression, flags=re.IGNORECASE)
    
    # Handle percentages correctly in context
    # e.g., "20% of 50" -> "0.2 * 50"
    expression = re.sub(r'(\d+)%\s+of\s+(\d+)', r'(\1/100)*\2', expression, flags=re.IGNORECASE)
    
    # Handle "X plus Y" text format
    expression = re.sub(r'(\d+)\s+plus\s+(\d+)', r'\1+\2', expression, flags=re.IGNORECASE)
    expression = re.sub(r'(\d+)\s+minus\s+(\d+)', r'\1-\2', expression, flags=re.IGNORECASE)
    expression = re.sub(r'(\d+)\s+times\s+(\d+)', r'\1*\2', expression, flags=re.IGNORECASE)
    expression = re.sub(r'(\d+)\s+divided\s+by\s+(\d+)', r'\1/\2', expression, flags=re.IGNORECASE)
    
    return expression

def extract_calculation(user_input):
    """
    Extract a calculation expression from user input
    
    Args:
        user_input (str): Raw user input text
        
    Returns:
        str or None: Extracted calculation expression or None if not found
    """
    # First, check for percentage calculations
    percentage_patterns = [
        r'(?:what\s+is|calculate|compute)?\s*(\d+\.?\d*)\s*%\s+(?:of|ka)\s+(\d+\.?\d*)',
        r'(\d+\.?\d*)\s+(?:percent|percentage)\s+(?:of|ka)\s+(\d+\.?\d*)'
    ]
    
    user_input_lower = user_input.lower()
    
    for pattern in percentage_patterns:
        match = re.search(pattern, user_input_lower)
        if match:
            percentage = match.group(1)
            base = match.group(2)
            return f"{percentage}% of {base}"
    
    # Check for direct mathematical expressions with operators
    math_pattern = r'(\d+\s*[\+\-\*\/\^\×\÷\%]\s*\d+(?:\s*[\+\-\*\/\^\×\÷\%]\s*\d+)*)'
    direct_match = re.search(math_pattern, user_input)
    if direct_match:
        return direct_match.group(1).strip()
    
    # Check for calculation requests
    calc_prefixes = [
        "calculate ", "compute ", "what is ", "what's ",
        "solve ", "evaluate ", "calculate ", "work out ",
    ]
    
    for prefix in calc_prefixes:
        if prefix in user_input_lower:
            # Extract everything after the prefix
            start_idx = user_input_lower.find(prefix) + len(prefix)
            expression = user_input[start_idx:].strip()
            
            # Remove question marks and periods
            expression = expression.rstrip('?.')
            
            if expression:
                return expression
    
    # Check for special calculation patterns like "X plus Y"
    special_pattern = r'(\d+)\s+(plus|minus|times|divided by)\s+(\d+)'
    special_match = re.search(special_pattern, user_input, re.IGNORECASE)
    if special_match:
        return user_input
    
    return None 