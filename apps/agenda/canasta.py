"""Canasta de exámenes almacenada en request.session (sin persistir en BD).

Estructura en sesión: {'canasta': {'<id_prestacion>': cantidad}, 'canasta_prevision': 'FONASA'}
"""
from apps.catalogo.models import PrestacionMedica
from apps.usuarios.models import PerfilUsuario

SESSION_KEY = 'canasta'
PREVISION_KEY = 'canasta_prevision'

# Porcentaje del arancel que cubre cada previsión (valores de simulación)
COBERTURA_PCT = {'FONASA': 60, 'ISAPRE': 70, 'PARTICULAR': 0}
RECARGO_GESTION_PCT = 3  # recargo administrativo sobre el copago
MAX_UNIDADES = 10


class Canasta:
    def __init__(self, request):
        self.request = request
        self.session = request.session

    # --- acceso a la sesión ---
    @property
    def items(self):
        return self.session.get(SESSION_KEY, {})

    def _guardar(self, items):
        self.session[SESSION_KEY] = items
        self.session.modified = True  # avisa a Django que la sesión cambió

    def __len__(self):
        return len(self.items)

    # --- operaciones ---
    def _validar_cantidad(self, prestacion, cantidad):
        limite = min(prestacion.cupos_diarios, MAX_UNIDADES)
        if cantidad < 1:
            return 'La cantidad mínima es 1.'
        if cantidad > limite:
            return f"'{prestacion.nombre}': máximo {limite} unidad(es) según cupos disponibles."
        return None

    def agregar(self, prestacion, cantidad=1):
        """Retorna (ok, mensaje)."""
        if not prestacion.disponible:
            return False, f"'{prestacion.nombre}' no está disponible por el momento."
        items = dict(self.items)
        nueva = items.get(str(prestacion.pk), 0) + cantidad
        error = self._validar_cantidad(prestacion, nueva)
        if error:
            return False, error
        items[str(prestacion.pk)] = nueva
        self._guardar(items)
        return True, f"'{prestacion.nombre}' se agregó a tu canasta."

    def actualizar(self, prestacion, cantidad):
        items = dict(self.items)
        if str(prestacion.pk) not in items:
            return False, 'Ese examen no está en tu canasta.'
        error = self._validar_cantidad(prestacion, cantidad)
        if error:
            return False, error
        items[str(prestacion.pk)] = cantidad
        self._guardar(items)
        return True, 'Cantidad actualizada.'

    def quitar(self, pk):
        items = dict(self.items)
        if items.pop(str(pk), None) is None:
            return False
        self._guardar(items)
        return True

    def vaciar(self):
        self.session.pop(SESSION_KEY, None)
        self.session.modified = True

    # --- previsión (define el copago) ---
    @property
    def prevision(self):
        valor = self.session.get(PREVISION_KEY)
        if valor in COBERTURA_PCT:
            return valor
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'perfil'):
            return user.perfil.prevision
        return PerfilUsuario.Prevision.PARTICULAR

    def set_prevision(self, valor):
        if valor not in COBERTURA_PCT:
            return False
        self.session[PREVISION_KEY] = valor
        self.session.modified = True
        return True

    # --- desglose numérico/económico ---
    def detalle(self):
        items = self.items
        ids = [int(k) for k in items]
        prestaciones = PrestacionMedica.objects.select_related('especialidad').filter(pk__in=ids)

        encontradas = {p.pk: p for p in prestaciones}
        if len(encontradas) != len(ids):  # limpia ids que ya no existen
            self._guardar({str(pk): items[str(pk)] for pk in encontradas})
            items = self.items

        lineas, subtotal = [], 0
        for pk, prestacion in encontradas.items():
            cantidad = items[str(pk)]
            total_linea = prestacion.arancel * cantidad
            subtotal += total_linea
            lineas.append({
                'prestacion': prestacion,
                'cantidad': cantidad,
                'maximo': min(prestacion.cupos_diarios, MAX_UNIDADES),
                'total': total_linea,
            })

        prevision = self.prevision
        pct = COBERTURA_PCT[prevision]
        bonificacion = subtotal * pct // 100
        copago = subtotal - bonificacion
        recargo = copago * RECARGO_GESTION_PCT // 100
        return {
            'lineas': lineas,
            'subtotal': subtotal,
            'prevision': prevision,
            'prevision_label': PerfilUsuario.Prevision(prevision).label,
            'pct_cobertura': pct,
            'bonificacion': bonificacion,
            'copago': copago,
            'pct_recargo': RECARGO_GESTION_PCT,
            'recargo': recargo,
            'total': copago + recargo,
            'unidades': sum(l['cantidad'] for l in lineas),
        }
