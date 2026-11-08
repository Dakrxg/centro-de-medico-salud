import re

from django.core.exceptions import ValidationError


def normalizar_rut(valor):
    """Deja solo dígitos y K en mayúscula: '12.345.678-5' -> '123456785'."""
    return re.sub(r'[^0-9kK]', '', valor or '').upper()


def formatear_rut(valor):
    rut = normalizar_rut(valor)
    cuerpo, dv = rut[:-1], rut[-1]
    return f"{int(cuerpo):,}".replace(',', '.') + '-' + dv


def validar_rut(valor):
    """Valida un RUT chileno con el algoritmo módulo 11."""
    rut = normalizar_rut(valor)
    if len(rut) < 8 or len(rut) > 9 or not rut[:-1].isdigit():
        raise ValidationError('Ingresa un RUT válido, por ejemplo 12.345.678-5.')
    cuerpo, dv = rut[:-1], rut[-1]
    suma, multiplicador = 0, 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    resto = 11 - (suma % 11)
    esperado = '0' if resto == 11 else 'K' if resto == 10 else str(resto)
    if dv != esperado:
        raise ValidationError('El dígito verificador del RUT no es correcto.')
