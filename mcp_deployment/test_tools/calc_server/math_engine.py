#!/usr/bin/env python3
"""
Mathematical Engine - Advanced Calculator Service
Production calculator with environment configuration and different variable name
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
    exit(1)

# Environment Configuration
PRECISION = int(os.getenv("MATH_PRECISION", "8"))
MAX_VALUE = float(os.getenv("MAX_CALCULATION_VALUE", "1e12"))
ENABLE_ADVANCED = os.getenv("ENABLE_ADVANCED_MATH", "true").lower() == "true"
CALC_SERVICE_NAME = os.getenv("CALC_SERVICE_NAME", "math-engine")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ALLOWED_OPERATIONS = os.getenv("ALLOWED_OPERATIONS", "+,-,*,/,%,^").split(",")

# Create MCP instance with different variable name
math_server = FastMCP(name=CALC_SERVICE_NAME)

def validate_input(value: float) -> bool:
    """Validate input values against constraints"""
    return abs(value) <= MAX_VALUE

@math_server.tool()
def calculate(operation: str, a: float, b: float) -> str:
    """
    Perform mathematical operations with validation

    Args:
        operation: Math operation (+, -, *, /, %, ^)
        a: First number
        b: Second number

    Returns:
        Mathematical result in JSON format
    """
    try:
        if LOG_LEVEL == "DEBUG":
            print(f"Calculation request: {a} {operation} {b}")

        # Validate inputs
        if not validate_input(a) or not validate_input(b):
            return json.dumps({
                "error": f"Input values exceed maximum allowed: {MAX_VALUE}",
                "operation": f"{a} {operation} {b}",
                "timestamp": datetime.now().isoformat()
            })

        # Check if operation is allowed
        if operation not in ALLOWED_OPERATIONS:
            return json.dumps({
                "error": f"Operation not allowed: {operation}",
                "allowed_operations": ALLOWED_OPERATIONS,
                "timestamp": datetime.now().isoformat()
            })

        operations = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y if y != 0 else None,
            '%': lambda x, y: x % y if y != 0 else None,
            '^': lambda x, y: x ** y,
            'pow': lambda x, y: x ** y
        }

        result = operations[operation](a, b)

        if result is None:
            return json.dumps({
                "error": "Division by zero",
                "operation": f"{a} {operation} {b}",
                "timestamp": datetime.now().isoformat()
            })

        calc_data = {
            "operation": f"{a} {operation} {b}",
            "result": round(result, PRECISION) if isinstance(result, float) else result,
            "precision": PRECISION,
            "service": CALC_SERVICE_NAME,
            "max_value_limit": MAX_VALUE,
            "timestamp": datetime.now().isoformat()
        }

        return json.dumps(calc_data, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Calculation failed: {str(e)}",
            "operation": f"{a} {operation} {b}",
            "service": CALC_SERVICE_NAME,
            "timestamp": datetime.now().isoformat()
        })

@math_server.tool()
def advanced_function(function: str, value: float, extra_param: Optional[float] = None) -> str:
    """
    Perform advanced mathematical functions (if enabled)

    Args:
        function: Math function (sqrt, sin, cos, tan, log, ln, exp, abs, ceil, floor)
        value: Input value
        extra_param: Extra parameter for functions that need it

    Returns:
        Mathematical result in JSON format
    """
    try:
        if not ENABLE_ADVANCED:
            return json.dumps({
                "error": "Advanced mathematics is disabled",
                "service": CALC_SERVICE_NAME,
                "timestamp": datetime.now().isoformat()
            })

        if not validate_input(value):
            return json.dumps({
                "error": f"Input value exceeds maximum allowed: {MAX_VALUE}",
                "function": function,
                "input_value": value,
                "timestamp": datetime.now().isoformat()
            })

        function = function.lower()

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
            "result": round(result, PRECISION) if isinstance(result, float) else result,
            "precision": PRECISION,
            "service": CALC_SERVICE_NAME,
            "advanced_enabled": ENABLE_ADVANCED,
            "timestamp": datetime.now().isoformat()
        }

        return json.dumps(calc_data, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Mathematical function failed: {str(e)}",
            "function": function,
            "input_value": value,
            "service": CALC_SERVICE_NAME,
            "timestamp": datetime.now().isoformat()
        })

@math_server.tool()
def get_service_info() -> str:
    """
    Get information about the calculator service configuration

    Returns:
        Service configuration in JSON format
    """
    try:
        service_info = {
            "service_name": CALC_SERVICE_NAME,
            "precision": PRECISION,
            "max_value": MAX_VALUE,
            "advanced_math_enabled": ENABLE_ADVANCED,
            "allowed_operations": ALLOWED_OPERATIONS,
            "log_level": LOG_LEVEL,
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat()
        }

        return json.dumps(service_info, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to get service info: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })

if __name__ == "__main__":
    print(f"Mathematical Engine - {math_server.name}")
    print(f"Precision: {PRECISION}")
    print(f"Max value: {MAX_VALUE}")
    print(f"Advanced math: {ENABLE_ADVANCED}")
    print(f"Allowed operations: {ALLOWED_OPERATIONS}")
    print("Starting math server...")
    math_server.run()