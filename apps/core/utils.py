from django import forms


def aplicar_estilos_bootstrap(form):
    """Agrega las clases de Bootstrap 5 a todos los widgets de un formulario."""
    for campo in form.fields.values():
        widget = campo.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs['class'] = 'form-check-input'
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            widget.attrs['class'] = 'form-select'
        else:
            widget.attrs['class'] = 'form-control'
