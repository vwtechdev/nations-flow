from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def month_name(month_number):
    """Converte número do mês em nome"""
    months = {
        '1': 'Janeiro',
        '2': 'Fevereiro',
        '3': 'Março',
        '4': 'Abril',
        '5': 'Maio',
        '6': 'Junho',
        '7': 'Julho',
        '8': 'Agosto',
        '9': 'Setembro',
        '10': 'Outubro',
        '11': 'Novembro',
        '12': 'Dezembro'
    }
    return months.get(str(month_number), month_number) 