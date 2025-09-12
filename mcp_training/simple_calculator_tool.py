#!/usr/bin/env python3
"""
Simple Calculator Tool - Training Example
Single-page MCP tool for basic mathematical operations
"""

import os
import json
import math
from datetime import datetime
from typing import Optional

try:
    from fastmcp import FastMCP
except ImportError:
    print("❌ ERROR: FastMCP not found!")
    print("📦 Install required dependency:")
    print("   pip install fastmcp")
    print("💡 Or run: pip install -r requirements.txt")
    exit(1)

# Configuration
DEFAULT_PRECISION = int(os.getenv("CALC_PRECISION", "6"))
stateless_mode = os.getenv("STATELESS_HTTP", "true").lower() == "true"

# Create MCP instance
mcp = FastMCP(name="simple-calculator-tool")

@mcp.tool()
def basic_math(operation: str, a: float, b: float) -> str:
    """
    Perform basic mathematical operations
    
    Args:
        operation: Math operation (+, -, *, /, %, ^)
        a: First number
        b: Second number
        
    Returns:
        Mathematical result in JSON format
    """
    try:
        operations = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y if y != 0 else None,
            '%': lambda x, y: x % y if y != 0 else None,
            '^': lambda x, y: x ** y,
            'pow': lambda x, y: x ** y
        }
        
        if operation not in operations:
            return json.dumps({
                "error": f"Unsupported operation: {operation}",
                "supported_operations": list(operations.keys()),
                "timestamp": datetime.now().isoformat()
            })
        
        result = operations[operation](a, b)
        
        if result is None:
            return json.dumps({
                "error": "Division by zero",
                "operation": f"{a} {operation} {b}",
                "timestamp": datetime.now().isoformat()
            })
        
        calc_data = {
            "operation": f"{a} {operation} {b}",
            "result": round(result, DEFAULT_PRECISION) if isinstance(result, float) else result,
            "precision": DEFAULT_PRECISION,
            "timestamp": datetime.now().isoformat(),
            "note": "Basic mathematical calculation"
        }
        
        return json.dumps(calc_data, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Calculation failed: {str(e)}",
            "operation": f"{a} {operation} {b}",
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
def advanced_math(function: str, value: float, extra_param: Optional[float] = None) -> str:
    """
    Perform advanced mathematical functions
    
    Args:
        function: Math function (sqrt, sin, cos, tan, log, ln, exp, abs, ceil, floor)
        value: Input value
        extra_param: Extra parameter for functions that need it (like log base)
        
    Returns:
        Mathematical result in JSON format
    """
    try:
        function = function.lower()
        
        # Functions that require extra parameter
        if function == 'log' and extra_param is not None:
            result = math.log(value, extra_param)
        elif function in ['sqrt', 'square_root']:
            result = math.sqrt(value)
        elif function in ['sin', 'sine']:
            result = math.sin(value)
        elif function in ['cos', 'cosine']:
            result = math.cos(value)
        elif function in ['tan', 'tangent']:
            result = math.tan(value)
        elif function in ['log', 'log10']:
            result = math.log10(value)
        elif function in ['ln', 'log_natural']:
            result = math.log(value)
        elif function in ['exp', 'exponential']:
            result = math.exp(value)
        elif function in ['abs', 'absolute']:
            result = abs(value)
        elif function in ['ceil', 'ceiling']:
            result = math.ceil(value)
        elif function in ['floor']:
            result = math.floor(value)
        else:
            return json.dumps({
                "error": f"Unsupported function: {function}",
                "supported_functions": ["sqrt", "sin", "cos", "tan", "log", "ln", "exp", "abs", "ceil", "floor"],
                "timestamp": datetime.now().isoformat()
            })
        
        operation_desc = f"{function}({value})" + (f" base {extra_param}" if extra_param and function == 'log' else "")
        
        calc_data = {
            "function": function,
            "input_value": value,
            "extra_parameter": extra_param,
            "operation": operation_desc,
            "result": round(result, DEFAULT_PRECISION) if isinstance(result, float) else result,
            "precision": DEFAULT_PRECISION,
            "timestamp": datetime.now().isoformat(),
            "note": "Advanced mathematical function"
        }
        
        return json.dumps(calc_data, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Mathematical function failed: {str(e)}",
            "function": function,
            "input_value": value,
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
def evaluate_expression(expression: str) -> str:
    """
    Safely evaluate mathematical expressions
    
    Args:
        expression: Mathematical expression (e.g., "2 + 3 * 4", "sqrt(16) + 2")
        
    Returns:
        Evaluation result in JSON format
    """
    try:
        # Create a safe namespace for evaluation
        safe_dict = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "ceil": math.ceil,
            "floor": math.floor,
            "pi": math.pi,
            "e": math.e
        }
        
        # Basic validation - reject potentially dangerous expressions
        dangerous_keywords = ['import', 'exec', 'eval', 'open', 'file', '__']
        if any(keyword in expression.lower() for keyword in dangerous_keywords):
            return json.dumps({
                "error": "Expression contains potentially unsafe operations",
                "expression": expression,
                "timestamp": datetime.now().isoformat()
            })
        
        result = eval(expression, safe_dict)
        
        eval_data = {
            "expression": expression,
            "result": round(result, DEFAULT_PRECISION) if isinstance(result, float) else result,
            "precision": DEFAULT_PRECISION,
            "timestamp": datetime.now().isoformat(),
            "note": "Expression evaluation result"
        }
        
        return json.dumps(eval_data, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Expression evaluation failed: {str(e)}",
            "expression": expression,
            "timestamp": datetime.now().isoformat()
        })

if __name__ == "__main__":
    print(f"Simple Calculator Tool - {mcp.name}")
    print(f"Default precision: {DEFAULT_PRECISION}")
    print("Starting MCP server...")
    mcp.run(stateless_http=stateless_mode)