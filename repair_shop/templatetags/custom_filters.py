from django import template
import calendar

register = template.Library()


@register.filter
def month_name(month_number):
    """Convert an integer month number (1-12) to its full name (e.g. 1 → January)."""
    try:
        return calendar.month_name[int(month_number)]
    except (ValueError, IndexError, TypeError):
        return month_number
