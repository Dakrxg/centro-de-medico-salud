from .canasta import Canasta


def agenda_context(request):
    """Permite acceder al número de exámenes en la canasta desde cualquier plantilla."""
    return {'canasta_cantidad': len(Canasta(request))}
