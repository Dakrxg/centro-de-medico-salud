from django import forms

from apps.core.utils import aplicar_estilos_bootstrap

from .models import EspecialidadMedica, PrestacionMedica


class PrestacionForm(forms.ModelForm):
    class Meta:
        model = PrestacionMedica
        fields = [
            'especialidad', 'codigo', 'nombre', 'descripcion', 'requisitos',
            'arancel', 'duracion_minutos', 'cupos_diarios', 'estado',
            'imagen', 'destacada', 'vigente',
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'placeholder': 'Ej. CAR-003'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej. Electrocardiograma de reposo'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'requisitos': forms.Textarea(attrs={'rows': 2}),
            'arancel': forms.NumberInput(attrs={'min': 0}),
            'cupos_diarios': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['especialidad'].queryset = EspecialidadMedica.objects.filter(activa=True)
        aplicar_estilos_bootstrap(self)

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo'].strip().upper()
        repetido = PrestacionMedica.objects.filter(codigo__iexact=codigo).exclude(pk=self.instance.pk)
        if repetido.exists():
            raise forms.ValidationError('Ya existe una prestación con ese código.')
        return codigo

    def clean_arancel(self):
        arancel = self.cleaned_data['arancel']
        if arancel < 0:
            raise forms.ValidationError('El arancel no puede ser negativo.')
        return arancel

    def clean_cupos_diarios(self):
        cupos = self.cleaned_data['cupos_diarios']
        if cupos < 0:
            raise forms.ValidationError('Los cupos no pueden ser negativos.')
        return cupos

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen and hasattr(imagen, 'size') and imagen.size > 2 * 1024 * 1024:
            raise forms.ValidationError('La imagen no puede superar los 2 MB.')
        return imagen
