from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class EspecialidadMedica(models.Model):
    """Entidad de contexto / agrupación (Cardiología, Laboratorio, etc.)."""

    nombre = models.CharField('especialidad', max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, help_text='URL amigable')
    descripcion = models.TextField('descripción', blank=True)
    icono = models.CharField(
        'icono Bootstrap', max_length=40, default='bi-heart-pulse',
        help_text='Clase de Bootstrap Icons, por ejemplo: bi-heart-pulse')
    activa = models.BooleanField('¿activa?', default=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'especialidad médica'
        verbose_name_plural = 'especialidades médicas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class PrestacionMedica(models.Model):
    """Entidad principal gestionable: examen, procedimiento o consulta."""

    class Estado(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'
        AGOTADO = 'AGOTADO', 'Sin cupos'

    # on_delete=PROTECT: no se puede borrar una especialidad con prestaciones asociadas
    especialidad = models.ForeignKey(
        EspecialidadMedica, on_delete=models.PROTECT, related_name='prestaciones',
        verbose_name='especialidad')
    codigo = models.CharField(
        'código', max_length=20, unique=True,
        validators=[RegexValidator(
            r'^[A-Za-z0-9-]+$', 'Solo letras, números y guiones (ej: CAR-001).')])
    slug = models.SlugField(max_length=60, unique=True, blank=True, editable=False)
    nombre = models.CharField('nombre de la prestación', max_length=120)
    descripcion = models.TextField('descripción')
    requisitos = models.TextField('requisitos / preparación', blank=True)
    arancel = models.IntegerField(
        'arancel (CLP)',
        validators=[MinValueValidator(0, 'El arancel no puede ser negativo.')])
    duracion_minutos = models.IntegerField(
        'duración (min)', default=30,
        validators=[MinValueValidator(1, 'La duración debe ser de al menos 1 minuto.')])
    cupos_diarios = models.IntegerField(
        'cupos diarios', default=10,
        validators=[MinValueValidator(0, 'Los cupos no pueden ser negativos.')])
    estado = models.CharField(
        'estado', max_length=12, choices=Estado.choices, default=Estado.DISPONIBLE)
    imagen = models.ImageField('fotografía', upload_to='prestaciones/', blank=True, null=True)
    destacada = models.BooleanField('¿destacada?', default=False)
    # Baja lógica: se desactiva sin borrar físicamente el registro
    vigente = models.BooleanField('¿vigente?', default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'prestación médica'
        verbose_name_plural = 'prestaciones médicas'
        ordering = ['especialidad__nombre', 'nombre']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'

    def save(self, *args, **kwargs):
        self.codigo = self.codigo.strip().upper()
        self.slug = slugify(self.codigo)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalogo:detalle', args=[self.slug])

    @property
    def arancel_formateado(self):
        return f'${self.arancel:,.0f}'.replace(',', '.')

    @property
    def disponible(self):
        """Se puede agregar a la canasta solo si está vigente, disponible y con cupos."""
        return (
            self.vigente
            and self.estado == self.Estado.DISPONIBLE
            and self.cupos_diarios > 0
            and self.especialidad.activa
        )
