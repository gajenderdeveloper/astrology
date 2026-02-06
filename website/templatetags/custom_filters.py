from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key) 

@register.filter
def indian_notation(number):
    try:
        number = float(number)
        if number.is_integer():
            number = int(number)
        return "{:,}".format(number).replace(",", ",")
    except (ValueError, TypeError):
        return number