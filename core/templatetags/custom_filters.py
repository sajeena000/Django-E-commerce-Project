from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    try:
        # Multiply the values
        result = float(value) * float(arg)
        
        # Check if the result is a whole number
        if result.is_integer():
            return int(result)
        else:
            return "{:.2f}".format(result)  # Return result with 2 decimal points
    except (ValueError, TypeError):
        return None  # Return None if invalid input