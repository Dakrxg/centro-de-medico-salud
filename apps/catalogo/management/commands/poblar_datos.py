import textwrap
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont

from apps.catalogo.models import EspecialidadMedica, PrestacionMedica
from apps.usuarios.models import PerfilUsuario

ESPECIALIDADES = [
    ('Cardiología', 'Diagnóstico y control de la salud del corazón y el sistema circulatorio.', 'bi-heart-pulse', (178, 34, 52)),
    ('Laboratorio Clínico', 'Exámenes de sangre y orina para el diagnóstico y seguimiento de patologías.', 'bi-droplet', (22, 122, 110)),
    ('Imagenología', 'Radiografías y ecografías para visualizar estructuras internas del cuerpo.', 'bi-camera', (44, 90, 160)),
    ('Traumatología', 'Evaluación y tratamiento de lesiones óseas, articulares y musculares.', 'bi-bandaid', (196, 112, 24)),
]

PRESTACIONES = [
    dict(esp='Cardiología', codigo='CAR-001', nombre='Electrocardiograma de reposo',
         descripcion='Registro de la actividad eléctrica del corazón en reposo. Examen rápido e indoloro.',
         requisitos='Orden médica. Evitar cremas en el pecho el día del examen.',
         arancel=18000, duracion=20, cupos=12, estado='DISPONIBLE', destacada=True),
    dict(esp='Cardiología', codigo='CAR-002', nombre='Ecocardiograma Doppler color',
         descripcion='Ecografía del corazón que evalúa su estructura, válvulas y flujo sanguíneo.',
         requisitos='Orden médica. Asistir con ropa cómoda.',
         arancel=65000, duracion=40, cupos=6, estado='DISPONIBLE', destacada=False),
    dict(esp='Laboratorio Clínico', codigo='LAB-001', nombre='Hemograma completo',
         descripcion='Análisis de glóbulos rojos, blancos y plaquetas para detectar anemias e infecciones.',
         requisitos='Ayuno de 8 horas recomendado.',
         arancel=6500, duracion=10, cupos=40, estado='DISPONIBLE', destacada=True),
    dict(esp='Laboratorio Clínico', codigo='LAB-002', nombre='Perfil lipídico',
         descripcion='Mide colesterol total, HDL, LDL y triglicéridos para evaluar el riesgo cardiovascular.',
         requisitos='Ayuno de 12 horas. Evitar alcohol las 24 horas previas.',
         arancel=12000, duracion=10, cupos=30, estado='DISPONIBLE', destacada=False),
    dict(esp='Imagenología', codigo='IMG-001', nombre='Radiografía de tórax',
         descripcion='Imagen de pulmones, corazón y estructuras del tórax en proyección frontal y lateral.',
         requisitos='Orden médica. Retirar joyas y objetos metálicos del cuello y tórax.',
         arancel=22000, duracion=15, cupos=20, estado='DISPONIBLE', destacada=False),
    dict(esp='Imagenología', codigo='IMG-002', nombre='Ecografía abdominal',
         descripcion='Evaluación por ultrasonido de hígado, vesícula, páncreas, riñones y bazo.',
         requisitos='Ayuno de 8 horas y vejiga llena (beber 1 litro de agua una hora antes).',
         arancel=38000, duracion=30, cupos=8, estado='DISPONIBLE', destacada=True),
    dict(esp='Traumatología', codigo='TRA-001', nombre='Consulta de traumatología',
         descripcion='Evaluación médica de lesiones y dolores articulares, óseos o musculares.',
         requisitos='Traer exámenes de imágenes previos, si existen.',
         arancel=35000, duracion=30, cupos=10, estado='DISPONIBLE', destacada=True),
    dict(esp='Traumatología', codigo='TRA-002', nombre='Infiltración articular',
         descripcion='Procedimiento para aliviar el dolor articular mediante la aplicación local de medicamento.',
         requisitos='Evaluación previa con traumatólogo. Informar alergias y uso de anticoagulantes.',
         arancel=72000, duracion=45, cupos=0, estado='SUSPENDIDO', destacada=False),
]

USUARIOS = [
    # username, clave, nombre, apellido, email, staff, superuser, rut, rol, previsión, teléfono
    ('admin', 'Admin12345!', 'Administrador', 'Sistema', 'admin@redsalud.cl', True, True,
     '11.111.111-1', 'ADMINISTRATIVO', 'PARTICULAR', '+56911111111'),
    ('recepcion', 'Recepcion12345!', 'Carla', 'Soto', 'recepcion@redsalud.cl', True, False,
     '14.141.414-3', 'ADMINISTRATIVO', 'FONASA', '+56922222222'),
    ('paciente', 'Paciente12345!', 'Pedro', 'Pérez', 'paciente@correo.cl', False, False,
     '12.345.678-5', 'PACIENTE', 'FONASA', '+56933333333'),
]


def generar_imagen(texto, color):
    """Imagen JPEG de ejemplo (800x500) con el nombre de la prestación."""
    img = Image.new('RGB', (800, 500), color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 380, 800, 500], fill=tuple(max(c - 40, 0) for c in color))
    try:
        fuente = ImageFont.load_default(size=40)
    except TypeError:  # Pillow antiguo sin parámetro size
        fuente = ImageFont.load_default()
    y = 140
    for linea in textwrap.wrap(texto, 24):
        draw.text((50, y), linea, fill='white', font=fuente)
        y += 55
    buffer = BytesIO()
    img.save(buffer, 'JPEG', quality=85)
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = 'Carga especialidades, prestaciones y usuarios de prueba (se puede ejecutar varias veces).'

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        colores, especialidades = {}, {}

        for nombre, descripcion, icono, color in ESPECIALIDADES:
            esp, _ = EspecialidadMedica.objects.update_or_create(
                nombre=nombre, defaults={'descripcion': descripcion, 'icono': icono, 'activa': True})
            especialidades[nombre] = esp
            colores[nombre] = color
        self.stdout.write(self.style.SUCCESS(f'✓ {len(ESPECIALIDADES)} especialidades listas.'))

        for d in PRESTACIONES:
            prestacion, _ = PrestacionMedica.objects.update_or_create(
                codigo=d['codigo'],
                defaults={
                    'especialidad': especialidades[d['esp']], 'nombre': d['nombre'],
                    'descripcion': d['descripcion'], 'requisitos': d['requisitos'],
                    'arancel': d['arancel'], 'duracion_minutos': d['duracion'],
                    'cupos_diarios': d['cupos'], 'estado': d['estado'],
                    'destacada': d['destacada'], 'vigente': True,
                })
            if not prestacion.imagen:
                prestacion.imagen.save(
                    f"{d['codigo'].lower()}.jpg", generar_imagen(d['nombre'], colores[d['esp']]), save=True)
        self.stdout.write(self.style.SUCCESS(f'✓ {len(PRESTACIONES)} prestaciones listas.'))

        for (username, clave, nombre, apellido, email, staff, superuser,
             rut, rol, prevision, telefono) in USUARIOS:
            user, creado = User.objects.get_or_create(username=username, defaults={
                'first_name': nombre, 'last_name': apellido, 'email': email,
                'is_staff': staff, 'is_superuser': superuser})
            if creado:
                user.set_password(clave)
                user.save()
            PerfilUsuario.objects.update_or_create(user=user, defaults={
                'rut': rut, 'rol': rol, 'prevision': prevision, 'telefono': telefono})
        self.stdout.write(self.style.SUCCESS('✓ Usuarios de prueba listos (ver README para credenciales).'))
