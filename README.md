# Guía de Desarrollo Backend Paso a Paso: RedSalud Vital
### Construcción de una Aplicación Web Completa con Django y Bootstrap 5

Esta guía técnica explica paso a paso cómo construir desde cero la plataforma de gestión de prestaciones y pre-agendamiento de **RedSalud Vital**, un centro de atención médica ambulatoria. En cada etapa se detallan los comandos, el código fuente y los fundamentos técnicos que justifican cada decisión de arquitectura en Django.

> Proyecto de la **Evaluación Sumativa N° 3 – Programación Back End (TI3041)**, Unidad 2: Framework Back End.

---

## 🧾 Ficha de Registro y Aprobación de la Propuesta

| Campo | Detalle |
| :--- | :--- |
| **Nombre de la Organización o Plataforma** | RedSalud Vital |
| **Modelo de Negocio / Giro** | Centro de atención médica ambulatoria (exámenes, procedimientos y consultas de especialidad) |
| **Integrantes del Equipo** | **[COMPLETAR: Nombre Apellido – RUT]** \| Ariel Venegas – **[COMPLETAR: RUT]** |
| **Entidad de Contexto / Agrupación (ORM)** | `EspecialidadMedica` |
| **Entidad Principal Gestionable (ORM)** | `PrestacionMedica` |
| **Propósito de la Sesión (`request.session`)** | Pre-agendamiento de prestaciones (canasta de exámenes) con cálculo de copago estimado según previsión (Fonasa / Isapre / Particular) |

---

## 📑 Tabla de Contenidos

1. [Cumplimiento de la Rúbrica](#cumplimiento-de-la-rúbrica)
2. [Arquitectura y Fundamentos de Django](#1-arquitectura-y-fundamentos-de-django)
3. [Paso 1: Entorno de Desarrollo y Dependencias](#paso-1-entorno-de-desarrollo-y-dependencias)
4. [Paso 2: Inicialización del Proyecto Django](#paso-2-inicialización-del-proyecto-django)
5. [Paso 3: Arquitectura Modular y Aplicaciones (`apps/`)](#paso-3-arquitectura-modular-y-aplicaciones-apps)
6. [Paso 4: Configuración Central (`config/settings.py`)](#paso-4-configuración-central-configsettingspy)
7. [Paso 5: Capa de Datos — Django ORM y Modelos Relacionales](#paso-5-capa-de-datos--django-orm-y-modelos-relacionales)
8. [Paso 6: Panel de Administración de Django (`admin.py`)](#paso-6-panel-de-administración-de-django-adminpy)
9. [Paso 7: Formularios y Operaciones CRUD en el Catálogo](#paso-7-formularios-y-operaciones-crud-en-el-catálogo)
10. [Paso 8: Manejo de Estado y Sesiones HTTP (Canasta de Exámenes)](#paso-8-manejo-de-estado-y-sesiones-http-canasta-de-exámenes)
11. [Paso 9: Autenticación de Usuarios y Control de Acceso](#paso-9-autenticación-de-usuarios-y-control-de-acceso)
12. [Paso 10: Capa de Presentación con DTL y Bootstrap 5](#paso-10-capa-de-presentación-con-dtl-y-bootstrap-5)
13. [Paso 11: Enrutamiento Principal con Namespaces (`config/urls.py`)](#paso-11-enrutamiento-principal-con-namespaces-configurlspy)
14. [Paso 12: Carga Inicial de Datos y Verificación del Sistema](#paso-12-carga-inicial-de-datos-y-verificación-del-sistema)
15. [Bitácora de Prompts (Uso Técnico y Ético de IA)](#bitácora-de-prompts-uso-técnico-y-ético-de-ia)
16. [Control de Versiones en Pareja (Git y GitHub)](#control-de-versiones-en-pareja-git-y-github)
17. [Glosario de Conceptos Técnicos](#glosario-de-conceptos-técnicos)

---

## ⚡ Instalación Rápida (para quien clona el repositorio)

```bash
git clone <URL-DEL-REPOSITORIO>
cd redsalud_vital

python -m venv .venv
#   Windows:      .venv\Scripts\activate
#   macOS/Linux:  source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env          # Windows: copy .env.example .env  (y edita SECRET_KEY)

python manage.py makemigrations
python manage.py migrate
python manage.py poblar_datos
python manage.py runserver
```

**Credenciales de prueba** (creadas por `poblar_datos`):

| Usuario | Contraseña | Rol |
| :--- | :--- | :--- |
| `admin` | `Admin12345!` | Superusuario (staff, accede al Django Admin) |
| `recepcion` | `Recepcion12345!` | Staff (accede a Gestión CRUD) |
| `paciente` | `Paciente12345!` | Usuario estándar (previsión Fonasa) |

* **Portada y catálogo:** http://127.0.0.1:8000/ y http://127.0.0.1:8000/catalogo/
* **Gestión interna:** http://127.0.0.1:8000/catalogo/gestion/
* **Django Admin:** http://127.0.0.1:8000/admin/

---

## Cumplimiento de la Rúbrica

| Criterio | Dónde se cumple | Paso |
| :--- | :--- | :--- |
| 2.1.1 Entorno, `.venv`, `requirements.txt`, `.gitignore`, `.env` + `.env.example` | Raíz del proyecto | 1 |
| 2.1.1 Modelado: FK `PROTECT`, `MinValueValidator`, `choices`, `ImageField`, baja lógica | `apps/catalogo/models.py` | 5 |
| 2.1.1 Migraciones y comando `poblar_datos` (4 especialidades, 8 prestaciones, usuarios) | `apps/catalogo/management/commands/poblar_datos.py` | 5 y 12 |
| 2.1.2 Títulos corporativos del admin | `apps/catalogo/admin.py` | 6 |
| 2.1.2 `list_display`, `list_filter`, `search_fields`, `list_editable`, `fieldsets` | `apps/catalogo/admin.py` | 6 |
| 2.1.3 C: `ModelForm` + Bootstrap + `request.FILES` + `clean_*()` | `apps/catalogo/forms.py`, `views.py` | 7 |
| 2.1.3 R: tarjetas, búsqueda con `Q`, filtro, orden, `Paginator`, detalle por slug | `apps/catalogo/views.py` | 7 |
| 2.1.3 U y D: edición precargada y baja lógica con confirmación | `apps/catalogo/views.py` | 7 |
| 2.1.4 Sesión: agregar/modificar/quitar/vaciar, cupos, desglose, context processor, comprobante | `apps/agenda/` | 8 |
| 2.1.4 Registro, login, logout, `@login_required`, `@user_passes_test`, CSRF, perfil con RUT | `apps/usuarios/`, `apps/catalogo/views.py` | 9 |
| 2.1.4 Bitácora de IA (3 casos) | Este README | Final |
| UI: `base.html`, navbar responsivo, messages, Bootstrap 5 | `templates/` | 10 |
| Git y trabajo en pareja | Repositorio GitHub | Final |

---

## 1. Arquitectura y Fundamentos de Django

Django estructura el desarrollo web bajo el patrón **MTV (Model - Template - View)**:

```text
[Navegador Web]
       │ 1. Petición HTTP (Request)
       ▼
[Enrutador: urls.py]
       │ 2. Asocia la URL a una función o clase
       ▼
[Vista: views.py] ◄────────► [Modelo / ORM: models.py] ◄──► [Base de Datos]
       │                          (Consultas y lógica de datos)
       │ 3. Inyecta diccionario de contexto
       ▼
[Plantilla: templates (.html)]
       │ 4. Renderiza HTML con DTL
       ▼
[Navegador Web] ◄── 5. Respuesta HTTP (Response)
```

* **Modelo (`models.py`):** define las tablas como clases de Python; el ORM las traduce a SQL.
* **Vista (`views.py`):** contiene la lógica de negocio. Recibe `request`, interactúa con los modelos y retorna una respuesta.
* **Plantilla (`templates`):** HTML procesado por el *Django Template Language (DTL)*.
* **Enrutador (`urls.py`):** asocia rutas HTTP con vistas.

---

## Paso 1: Entorno de Desarrollo y Dependencias

### Fundamento Técnico: Aislamiento del Entorno
Instalar librerías de forma global provoca conflictos de versiones entre proyectos. Un entorno virtual crea un directorio aislado con su propio intérprete y `site-packages`, garantizando portabilidad y estabilidad.

### Comandos de Ejecución

1. Crea la carpeta principal y accede a ella:
   ```bash
   mkdir redsalud_vital
   cd redsalud_vital
   ```

2. Crea y activa el entorno virtual `.venv`:
   * **Windows:**
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Instala las dependencias:
   ```bash
   pip install django pillow python-dotenv
   ```
   * **`django`:** el framework web backend.
   * **`pillow`:** requerida por Django para los campos `ImageField`.
   * **`python-dotenv`:** desacopla variables sensibles (`SECRET_KEY`, credenciales de BD) en un archivo `.env`.

4. Fija las versiones en `requirements.txt` (la rúbrica exige versiones fijadas):
   ```bash
   pip freeze > requirements.txt
   ```
   El archivo del proyecto contiene (puedes ajustarlo a las versiones que tengas instaladas):


**`requirements.txt`**
```text
django==5.1.4
pillow==11.0.0
python-dotenv==1.0.1
```


### Variables de entorno y archivos de seguridad

El archivo `.env` **nunca se sube a GitHub**. En su lugar se entrega `.env.example` como plantilla para pruebas locales:


**`.env.example`**
```ini
# Copia este archivo como ".env" y ajusta los valores (NO subas .env a GitHub)
SECRET_KEY=cambia-esta-clave-por-una-larga-y-aleatoria
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
NOMBRE_ORGANIZACION=RedSalud Vital

# Base de datos: "sqlite" (por defecto) o "postgresql"
DB_ENGINE=sqlite
# Solo si usas PostgreSQL (requiere: pip install psycopg2-binary)
DB_NAME=redsalud
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
```


Y el `.gitignore` que excluye entorno virtual, cachés, secretos, base de datos y archivos subidos:


**`.gitignore`**
```gitignore
# Entorno virtual
.venv/
venv/
env/

# Python
__pycache__/
*.py[cod]

# Secretos
.env

# Base de datos local, archivos subidos y estáticos recolectados
db.sqlite3
*.sqlite3
media/*
!media/.gitkeep
staticfiles/

# IDE / SO
.vscode/
.idea/
.DS_Store
```


---

## Paso 2: Inicialización del Proyecto Django

Crea el esqueleto inicial del proyecto:
```bash
django-admin startproject config .
```

> **Detalle técnico:** el punto final (`.`) inicializa la configuración dentro del directorio actual, evitando una doble carpeta redundante.

### Estructura generada
* **`manage.py`:** interfaz de línea de comandos (migraciones, servidor local, usuarios).
* **`config/settings.py`:** configuración central.
* **`config/urls.py`:** tabla maestra de rutas.
* **`config/wsgi.py` / `asgi.py`:** interfaces para despliegue en producción.

### Estructura final del proyecto

```text
redsalud_vital/
├── manage.py
├── requirements.txt
├── .env.example          (el .env real NO se versiona)
├── .gitignore
├── config/               settings, urls, wsgi, asgi
├── apps/
│   ├── core/             portada, quiénes somos, acceso restringido
│   ├── usuarios/         registro, login, logout, perfil (RUT, rol, previsión)
│   ├── catalogo/         especialidades, prestaciones, CRUD, admin, poblar_datos
│   └── agenda/           canasta de exámenes en sesión y comprobante
├── templates/            base.html + plantillas por módulo
├── static/               css, js, img
└── media/                imágenes subidas (no versionadas)
```

---

## Paso 3: Arquitectura Modular y Aplicaciones (`apps/`)

### Fundamento Técnico: ¿Por qué un directorio contenedor `apps/`?
Colocar todas las aplicaciones en la raíz mezcla archivos de infraestructura (`manage.py`, `.env`, `requirements.txt`) con lógica de negocio. Usar `apps/` aporta:
1. **Directorio raíz limpio.**
2. **Espacio de nombres seguro:** evita colisiones con paquetes de terceros o de Python.
3. **Modularidad:** cada módulo encapsula un dominio del sistema.

### Aplicaciones del proyecto
1. **`apps/core`:** páginas generales (portada, quiénes somos, acceso restringido).
2. **`apps/usuarios`:** registro, login, logout y perfil complementario del usuario.
3. **`apps/catalogo`:** modelos de especialidades y prestaciones, panel de gestión y operaciones CRUD.
4. **`apps/agenda`:** canasta de exámenes almacenada en la sesión del usuario y comprobante simulado.

### Comandos de creación

* **Windows (PowerShell):**
  ```powershell
  mkdir apps, static/js, static/img, media/prestaciones
  mkdir templates/core, templates/usuarios, templates/catalogo, templates/agenda
  New-Item apps/__init__.py
  python manage.py startapp core apps/core
  python manage.py startapp usuarios apps/usuarios
  python manage.py startapp catalogo apps/catalogo
  python manage.py startapp agenda apps/agenda
  ```
* **macOS / Linux:**
  ```bash
  mkdir -p apps static/js static/img media/prestaciones templates/core templates/usuarios templates/catalogo templates/agenda
  touch apps/__init__.py
  python3 manage.py startapp core apps/core
  python3 manage.py startapp usuarios apps/usuarios
  python3 manage.py startapp catalogo apps/catalogo
  python3 manage.py startapp agenda apps/agenda
  ```

### Configuración del nombre de cada aplicación en `apps.py`
Como las apps viven dentro de `apps/`, se actualiza el atributo `name`:


**`apps/core/apps.py`**
```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Núcleo del Sitio'
```

**`apps/usuarios/apps.py`**
```python
from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'
    verbose_name = 'Usuarios y Pacientes'
```

**`apps/catalogo/apps.py`**
```python
from django.apps import AppConfig


class CatalogoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.catalogo'
    verbose_name = 'Catálogo de Prestaciones'
```

**`apps/agenda/apps.py`**
```python
from django.apps import AppConfig


class AgendaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.agenda'
    verbose_name = 'Canasta de Exámenes y Pre-agendamiento'
```


---

## Paso 4: Configuración Central (`config/settings.py`)

Puntos clave del archivo:
* Carga de `.env` con `python-dotenv` (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, base de datos y nombre de la organización).
* **Conexión a la base de datos** configurable: SQLite por defecto o PostgreSQL con `DB_ENGINE=postgresql`.
* Registro de las cuatro apps y de dos *context processors* propios.
* Idioma `es-cl`, zona horaria `America/Santiago` y separador de miles.
* Rutas de autenticación con namespaces y mapeo de mensajes flash a clases de Bootstrap.


**`config/settings.py`**
```python
"""Configuración central del proyecto RedSalud Vital (Evaluación Sumativa N° 3)."""
import os
from pathlib import Path

from django.contrib.messages import constants as messages
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Variables sensibles desacopladas en .env (ver .env.example)
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'clave-insegura-solo-para-desarrollo')
DEBUG = os.getenv('DEBUG', 'True').strip().lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]

# Identidad corporativa (la usan el admin y las plantillas)
NOMBRE_ORGANIZACION = os.getenv('NOMBRE_ORGANIZACION', 'RedSalud Vital')

# 1. Registro de Aplicaciones
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Módulos del Proyecto
    'apps.core',
    'apps.usuarios',
    'apps.catalogo',
    'apps.agenda',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# 2. Plantillas y Context Processors
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Directorio global de plantillas
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                # Nombre de la organización disponible en todas las plantillas
                'apps.core.context_processors.organizacion',
                # Contador global de la canasta de exámenes (navbar)
                'apps.agenda.context_processors.agenda_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# 3. Conexión a la base de datos (Criterio 2.1.1)
DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite').strip().lower()

if DB_ENGINE == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'redsalud'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 4. Idioma y Zona Horaria
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True  # 25000 -> 25.000

# 5. Archivos Estáticos (diseño) y Multimedia (subidas)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 6. Autenticación y sesiones
LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'catalogo:lista'
LOGOUT_REDIRECT_URL = 'core:inicio'
SESSION_COOKIE_AGE = 60 * 60 * 2  # la canasta vive 2 horas
SESSION_COOKIE_HTTPONLY = True

# 7. Mensajes flash -> clases de Bootstrap 5
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.ERROR: 'danger',
}
```


### Context Processors del proyecto
Inyectan variables en **todas** las plantillas. El primero expone el nombre de la organización; el segundo (de la app `agenda`) el contador de la canasta que se muestra en el navbar:


**`apps/core/context_processors.py`**
```python
from django.conf import settings


def organizacion(request):
    """Expone el nombre de la organización a todas las plantillas."""
    return {'NOMBRE_ORGANIZACION': settings.NOMBRE_ORGANIZACION}
```

**`apps/agenda/context_processors.py`**
```python
from .canasta import Canasta


def agenda_context(request):
    """Permite acceder al número de exámenes en la canasta desde cualquier plantilla."""
    return {'canasta_cantidad': len(Canasta(request))}
```


---

## Paso 5: Capa de Datos — Django ORM y Modelos Relacionales

### Fundamento Técnico: Django ORM y Claves Foráneas
El ORM traduce clases de Python en tablas relacionales. En este modelo:
* **`EspecialidadMedica`:** entidad de contexto/agrupación (Cardiología, Laboratorio, etc.).
* **`PrestacionMedica`:** entidad principal gestionable. La relación `ForeignKey` vincula muchas prestaciones a una especialidad.
* **`on_delete=models.PROTECT`:** impide borrar una especialidad si existen prestaciones vinculadas, evitando registros huérfanos.
* **`MinValueValidator`:** impide valores negativos en arancel, duración y cupos.
* **`TextChoices` (`Estado`):** estado operativo con opciones cerradas.
* **`ImageField`:** soporte multimedia para la fotografía del recurso.
* **`vigente`:** baja lógica; el registro se desactiva sin destruirse.

Edita `apps/catalogo/models.py`:


**`apps/catalogo/models.py`**
```python
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
```


### Perfil de usuario (RUT, teléfono, rol institucional y previsión)
La previsión del perfil determina el porcentaje de bonificación que se usa al calcular el copago. El RUT se valida con el algoritmo **módulo 11**:


**`apps/usuarios/validators.py`**
```python
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
```

**`apps/usuarios/models.py`**
```python
from django.conf import settings
from django.db import models

from .validators import validar_rut


class PerfilUsuario(models.Model):
    """Datos complementarios del usuario: RUT, teléfono, rol institucional y previsión."""

    class Rol(models.TextChoices):
        PACIENTE = 'PACIENTE', 'Paciente'
        ADMINISTRATIVO = 'ADMINISTRATIVO', 'Personal administrativo'
        MEDICO = 'MEDICO', 'Profesional de la salud'

    class Prevision(models.TextChoices):
        FONASA = 'FONASA', 'Fonasa'
        ISAPRE = 'ISAPRE', 'Isapre'
        PARTICULAR = 'PARTICULAR', 'Particular (sin previsión)'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    rut = models.CharField('RUT', max_length=12, unique=True, validators=[validar_rut])
    telefono = models.CharField('teléfono', max_length=20, blank=True)
    rol = models.CharField('rol institucional', max_length=15, choices=Rol.choices, default=Rol.PACIENTE)
    prevision = models.CharField(
        'previsión', max_length=12, choices=Prevision.choices, default=Prevision.PARTICULAR)

    class Meta:
        verbose_name = 'perfil de usuario'
        verbose_name_plural = 'perfiles de usuario'

    def __str__(self):
        return f'{self.user.get_username()} ({self.rut})'
```


### Ejecutar Migraciones
Crea los archivos de migración y aplícalos a la base de datos:
```bash
python manage.py makemigrations
python manage.py migrate
```

> Las apps `usuarios` y `catalogo` incluyen su carpeta `migrations/` (con `__init__.py`), por lo que `makemigrations` genera las migraciones iniciales de ambas.

---

## Paso 6: Panel de Administración de Django (`admin.py`)

Se personaliza la identidad corporativa del panel (`site_header`, `site_title`, `index_title`) y se configura `ModelAdmin` con `@admin.register`, `list_display`, `list_filter`, `search_fields`, `list_editable` y `fieldsets`:


**`apps/catalogo/admin.py`**
```python
from django.conf import settings
from django.contrib import admin

from .models import EspecialidadMedica, PrestacionMedica

# Identidad corporativa del panel de administración
admin.site.site_header = f'{settings.NOMBRE_ORGANIZACION} - Panel de Control'
admin.site.site_title = f'{settings.NOMBRE_ORGANIZACION} Admin'
admin.site.index_title = 'Gestión Operativa de Recursos y Servicios'


@admin.register(EspecialidadMedica)
class EspecialidadMedicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'icono', 'activa', 'creada_en')
    list_filter = ('activa',)
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ('activa',)


@admin.register(PrestacionMedica)
class PrestacionMedicaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'especialidad', 'arancel', 'cupos_diarios', 'estado', 'vigente')
    list_display_links = ('codigo', 'nombre')
    list_filter = ('especialidad', 'estado', 'vigente')
    search_fields = ('codigo', 'nombre', 'descripcion')
    list_editable = ('arancel', 'estado', 'vigente')
    list_select_related = ('especialidad',)
    list_per_page = 15
    readonly_fields = ('slug', 'fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Identificación', {'fields': ('especialidad', 'codigo', 'slug', 'nombre')}),
        ('Descripción clínica', {'fields': ('descripcion', 'requisitos', 'imagen')}),
        ('Valores y capacidad', {'fields': ('arancel', 'duracion_minutos', 'cupos_diarios')}),
        ('Estado operativo', {'fields': ('estado', 'vigente', 'destacada')}),
        ('Auditoría', {'classes': ('collapse',), 'fields': ('fecha_creacion', 'fecha_actualizacion')}),
    )
```


Admin del perfil de usuario:


**`apps/usuarios/admin.py`**
```python
from django.contrib import admin

from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rut', 'telefono', 'rol', 'prevision')
    list_filter = ('rol', 'prevision')
    search_fields = ('user__username', 'rut', 'user__email')
    list_select_related = ('user',)
```


Crea el usuario administrador (o usa el que genera `poblar_datos` en el Paso 12):
```bash
python manage.py createsuperuser
```

---

## Paso 7: Formularios y Operaciones CRUD en el Catálogo

### Fundamento Técnico: Uso de `ModelForm` y Seguridad
`forms.ModelForm` inspecciona el modelo, deduce los tipos de campo y agrega validaciones automáticas. Los métodos `clean_<campo>()` suman reglas de negocio: código único (sin distinguir mayúsculas), arancel y cupos no negativos, e imagen de máximo 2 MB.

### Utilidad para estilos Bootstrap 5

**`apps/core/utils.py`**
```python
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
```


### Formulario `PrestacionForm`


**`apps/catalogo/forms.py`**
```python
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
```


### Vistas del catálogo (`apps/catalogo/views.py`)
* **R (Read):** `prestacion_lista` aplica búsqueda multicampo con `Q`, filtro por especialidad, ordenamiento validado con una lista blanca y paginación con `Paginator`; usa `select_related` y `annotate(Count)` para evitar consultas N+1. `prestacion_detalle` entrega la ficha por *slug*.
* **C / U (Create / Update):** formularios con `request.FILES` y mensajes del *messages framework*.
* **D (Delete):** pantalla de confirmación previa y **baja lógica** (`vigente=False`), con vista para reactivar.
* **Seguridad:** todas las vistas administrativas usan `@login_required` y `@user_passes_test(es_administrador)`.


**`apps/catalogo/views.py`**
```python
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PrestacionForm
from .models import EspecialidadMedica, PrestacionMedica

ORDENES = {
    'nombre_asc': 'nombre',
    'arancel_asc': 'arancel',
    'arancel_desc': '-arancel',
    'duracion': 'duracion_minutos',
}


def es_administrador(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# Rutas administrativas: @login_required + @solo_staff
solo_staff = user_passes_test(es_administrador, login_url='core:sin_permiso')


# ---------------------------------------------------------------- Público (R)
def prestacion_lista(request):
    query = request.GET.get('q', '').strip()
    especialidad_slug = request.GET.get('especialidad', '')
    orden = request.GET.get('orden', 'nombre_asc')

    prestaciones = PrestacionMedica.objects.filter(
        vigente=True, especialidad__activa=True).select_related('especialidad')

    if especialidad_slug:
        prestaciones = prestaciones.filter(especialidad__slug=especialidad_slug)

    if query:
        prestaciones = prestaciones.filter(
            Q(nombre__icontains=query) | Q(codigo__icontains=query) | Q(descripcion__icontains=query))

    prestaciones = prestaciones.order_by(ORDENES.get(orden, 'nombre'))
    total_resultados = prestaciones.count()

    pagina = Paginator(prestaciones, 6).get_page(request.GET.get('page'))
    parametros = request.GET.copy()
    parametros.pop('page', None)

    especialidades = EspecialidadMedica.objects.filter(activa=True).annotate(
        total=Count('prestaciones', filter=Q(prestaciones__vigente=True)))

    return render(request, 'catalogo/prestacion_lista.html', {
        'prestaciones': pagina,
        'especialidades': especialidades,
        'especialidad_sel': especialidad_slug,
        'query_actual': query,
        'orden_actual': orden,
        'total_resultados': total_resultados,
        'querystring': parametros.urlencode(),
    })


def prestacion_detalle(request, slug):
    prestacion = get_object_or_404(
        PrestacionMedica.objects.select_related('especialidad'), slug=slug)
    if not prestacion.vigente and not es_administrador(request.user):
        raise Http404('Prestación no disponible.')
    relacionadas = PrestacionMedica.objects.filter(
        especialidad=prestacion.especialidad, vigente=True
    ).exclude(pk=prestacion.pk).select_related('especialidad')[:3]
    return render(request, 'catalogo/prestacion_detalle.html', {
        'p': prestacion, 'relacionadas': relacionadas})


# ------------------------------------------------------------ Backoffice (CRUD)
@login_required
@solo_staff
def gestion_prestaciones(request):
    query = request.GET.get('q', '').strip()
    prestaciones = PrestacionMedica.objects.select_related('especialidad')
    if query:
        prestaciones = prestaciones.filter(
            Q(nombre__icontains=query) | Q(codigo__icontains=query) | Q(descripcion__icontains=query))
    pagina = Paginator(prestaciones, 10).get_page(request.GET.get('page'))
    return render(request, 'catalogo/gestion_prestaciones.html', {'prestaciones': pagina, 'query': query})


@login_required
@solo_staff
def prestacion_crear(request):
    form = PrestacionForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        prestacion = form.save()
        messages.success(request, f"Prestación '{prestacion.nombre}' creada correctamente.")
        return redirect('catalogo:gestion')
    return render(request, 'catalogo/prestacion_form.html', {
        'form': form, 'titulo_accion': 'Ingresar Nueva Prestación', 'boton_texto': 'Guardar'})


@login_required
@solo_staff
def prestacion_editar(request, slug):
    prestacion = get_object_or_404(PrestacionMedica, slug=slug)
    form = PrestacionForm(request.POST or None, request.FILES or None, instance=prestacion)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Prestación '{prestacion.nombre}' actualizada.")
        return redirect('catalogo:gestion')
    return render(request, 'catalogo/prestacion_form.html', {
        'form': form, 'p': prestacion, 'titulo_accion': 'Editar Prestación', 'boton_texto': 'Actualizar'})


@login_required
@solo_staff
def prestacion_eliminar(request, slug):
    """Pantalla de confirmación + baja lógica (no se borra físicamente)."""
    prestacion = get_object_or_404(PrestacionMedica, slug=slug)
    if request.method == 'POST':
        prestacion.vigente = False
        prestacion.save(update_fields=['vigente', 'fecha_actualizacion'])
        messages.warning(request, f"'{prestacion.nombre}' fue dada de baja (puedes reactivarla).")
        return redirect('catalogo:gestion')
    return render(request, 'catalogo/prestacion_confirmar_baja.html', {'p': prestacion})


@login_required
@solo_staff
@require_POST
def prestacion_reactivar(request, slug):
    prestacion = get_object_or_404(PrestacionMedica, slug=slug)
    prestacion.vigente = True
    prestacion.save(update_fields=['vigente', 'fecha_actualizacion'])
    messages.success(request, f"'{prestacion.nombre}' fue reactivada.")
    return redirect('catalogo:gestion')
```


### URLs (`apps/catalogo/urls.py`)


**`apps/catalogo/urls.py`**
```python
from django.urls import path

from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.prestacion_lista, name='lista'),
    path('prestacion/<slug:slug>/', views.prestacion_detalle, name='detalle'),
    path('gestion/', views.gestion_prestaciones, name='gestion'),
    path('gestion/nueva/', views.prestacion_crear, name='crear'),
    path('gestion/editar/<slug:slug>/', views.prestacion_editar, name='editar'),
    path('gestion/eliminar/<slug:slug>/', views.prestacion_eliminar, name='eliminar'),
    path('gestion/reactivar/<slug:slug>/', views.prestacion_reactivar, name='reactivar'),
]
```


---

## Paso 8: Manejo de Estado y Sesiones HTTP (Canasta de Exámenes)

### Fundamento Técnico: Sesiones en Arquitecturas Web
HTTP es un protocolo sin estado (*stateless*). Para que el servidor recuerde los exámenes seleccionados sin escribir en la base de datos, Django provee `request.session`, respaldado por una cookie en el navegador.

La clase `Canasta` encapsula toda la lógica:
* **Agregar** con validación de disponibilidad y cupos diarios.
* **Modificar** cantidades (validadas en el servidor).
* **Quitar** ítems y **vaciar** la canasta.
* **Desglose económico:** subtotal, bonificación según previsión, copago, recargo de gestión (3 %) y total.
* `session.modified = True` avisa a Django que el diccionario de sesión cambió.


**`apps/agenda/canasta.py`**
```python
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
```


### Vistas de la canasta y comprobante simulado
Las operaciones que modifican la sesión se aceptan solo por **POST** (`@require_POST`) con token CSRF. La confirmación revalida disponibilidad, genera un folio, **vacía la sesión** y muestra un comprobante simulado:


**`apps/agenda/views.py`**
```python
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.catalogo.models import PrestacionMedica
from apps.usuarios.models import PerfilUsuario

from .canasta import COBERTURA_PCT, Canasta


def _volver(request, defecto='agenda:ver'):
    siguiente = request.POST.get('next', '')
    if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
        return redirect(siguiente)
    return redirect(defecto)


def _entero(valor, defecto=1):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return defecto


def canasta_ver(request):
    contexto = Canasta(request).detalle()
    contexto['previsiones'] = [
        (valor, etiqueta, COBERTURA_PCT[valor]) for valor, etiqueta in PerfilUsuario.Prevision.choices]
    return render(request, 'agenda/canasta.html', contexto)


@require_POST
def canasta_agregar(request, pk):
    prestacion = get_object_or_404(PrestacionMedica.objects.select_related('especialidad'), pk=pk)
    ok, mensaje = Canasta(request).agregar(prestacion, _entero(request.POST.get('cantidad'), 1))
    (messages.success if ok else messages.error)(request, mensaje)
    return _volver(request, 'catalogo:lista')


@require_POST
def canasta_actualizar(request, pk):
    prestacion = get_object_or_404(PrestacionMedica, pk=pk)
    ok, mensaje = Canasta(request).actualizar(prestacion, _entero(request.POST.get('cantidad'), 0))
    (messages.success if ok else messages.error)(request, mensaje)
    return redirect('agenda:ver')


@require_POST
def canasta_quitar(request, pk):
    if Canasta(request).quitar(pk):
        messages.warning(request, 'Examen eliminado de tu canasta.')
    return redirect('agenda:ver')


@require_POST
def canasta_vaciar(request):
    Canasta(request).vaciar()
    messages.info(request, 'Tu canasta quedó vacía.')
    return redirect('agenda:ver')


@require_POST
def canasta_prevision(request):
    if Canasta(request).set_prevision(request.POST.get('prevision')):
        messages.success(request, 'Previsión actualizada; el copago fue recalculado.')
    else:
        messages.error(request, 'Previsión no válida.')
    return redirect('agenda:ver')


@login_required
@require_POST
def checkout_simulado(request):
    """Genera un comprobante simulado y vacía la canasta de la sesión."""
    canasta = Canasta(request)
    detalle = canasta.detalle()

    if not detalle['lineas']:
        messages.warning(request, 'Tu canasta está vacía.')
        return redirect('catalogo:lista')

    # Revalida disponibilidad y cupos justo antes de confirmar
    for linea in detalle['lineas']:
        p = linea['prestacion']
        if not p.disponible or linea['cantidad'] > p.cupos_diarios:
            messages.error(request, f"'{p.nombre}' ya no tiene disponibilidad suficiente. Revisa tu canasta.")
            return redirect('agenda:ver')

    ahora = timezone.localtime()
    folio = f'RSV-{ahora:%Y%m%d%H%M%S}-{request.user.pk}'
    canasta.vaciar()
    return render(request, 'agenda/comprobante.html', {
        **detalle, 'folio': folio, 'fecha': ahora, 'paciente': request.user})
```


### URLs (`apps/agenda/urls.py`)


**`apps/agenda/urls.py`**
```python
from django.urls import path

from . import views

app_name = 'agenda'

urlpatterns = [
    path('canasta/', views.canasta_ver, name='ver'),
    path('canasta/agregar/<int:pk>/', views.canasta_agregar, name='agregar'),
    path('canasta/actualizar/<int:pk>/', views.canasta_actualizar, name='actualizar'),
    path('canasta/quitar/<int:pk>/', views.canasta_quitar, name='quitar'),
    path('canasta/vaciar/', views.canasta_vaciar, name='vaciar'),
    path('canasta/prevision/', views.canasta_prevision, name='prevision'),
    path('confirmar/', views.checkout_simulado, name='checkout'),
]
```


---

## Paso 9: Autenticación de Usuarios y Control de Acceso

### Fundamento Técnico: Seguridad y Hashing de Contraseñas
Django utiliza PBKDF2 con sal (SHA-256) para proteger contraseñas; nunca las almacena en texto claro. El cierre de sesión se hace por **POST** con CSRF, y el parámetro `next` se valida con `url_has_allowed_host_and_scheme` para evitar redirecciones abiertas.

El formulario de registro crea el `User` y su `PerfilUsuario` (RUT, teléfono, previsión y rol) dentro de una transacción atómica.


**`apps/usuarios/forms.py`**
```python
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from apps.core.utils import aplicar_estilos_bootstrap

from .models import PerfilUsuario
from .validators import formatear_rut, validar_rut


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label='Nombres', max_length=150)
    last_name = forms.CharField(label='Apellidos', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    rut = forms.CharField(label='RUT', max_length=12, validators=[validar_rut],
                          help_text='Ej: 12.345.678-5')
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)
    prevision = forms.ChoiceField(label='Previsión', choices=PerfilUsuario.Prevision.choices)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos_bootstrap(self)

    def clean_rut(self):
        rut = formatear_rut(self.cleaned_data['rut'])
        if PerfilUsuario.objects.filter(rut=rut).exists():
            raise forms.ValidationError('Ya existe un usuario registrado con ese RUT.')
        return rut

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=True)
        PerfilUsuario.objects.create(
            user=user,
            rut=self.cleaned_data['rut'],
            telefono=self.cleaned_data['telefono'],
            prevision=self.cleaned_data['prevision'],
            rol=PerfilUsuario.Rol.PACIENTE,
        )
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos_bootstrap(self)
```

**`apps/usuarios/views.py`**
```python
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegistroForm


def registro_usuario(request):
    if request.user.is_authenticated:
        return redirect('catalogo:lista')
    form = RegistroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'¡Bienvenido/a, {user.first_name}! Tu cuenta fue creada.')
        return redirect('catalogo:lista')
    return render(request, 'usuarios/registro.html', {'form': form})


def login_usuario(request):
    if request.user.is_authenticated:
        return redirect('catalogo:lista')
    siguiente = request.POST.get('next') or request.GET.get('next', '')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, 'Sesión iniciada correctamente.')
        # Evita "open redirect": solo se aceptan destinos del mismo sitio
        if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
            return redirect(siguiente)
        return redirect('catalogo:lista')
    return render(request, 'usuarios/login.html', {'form': form, 'next': siguiente})


@require_POST  # el cierre de sesión se hace por POST + CSRF
def logout_usuario(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión.')
    return redirect('core:inicio')


@login_required
def perfil_usuario(request):
    perfil = getattr(request.user, 'perfil', None)
    return render(request, 'usuarios/perfil.html', {'usuario': request.user, 'perfil': perfil})
```

**`apps/usuarios/urls.py`**
```python
from django.urls import path

from . import views

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('perfil/', views.perfil_usuario, name='perfil'),
]
```


---

## Paso 10: Capa de Presentación con DTL y Bootstrap 5

### Plantilla Maestra (`templates/base.html`)
Centraliza el diseño, el navbar responsivo (con contador de canasta, menú de administración para `is_staff` y logout por POST), el contenedor de mensajes y el pie de página:


**`templates/base.html`**
```html
{% load static %}<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ NOMBRE_ORGANIZACION }}{% endblock %}</title>
    <!-- Bootstrap 5.3 CSS & Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <link rel="stylesheet" href="{% static 'css/estilos.css' %}">
</head>
<body class="d-flex flex-column min-vh-100">

    <!-- Barra de Navegación -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-rs sticky-top shadow-sm py-3">
        <div class="container">
            <a class="navbar-brand fw-bold fs-4" href="{% url 'core:inicio' %}">
                <i class="bi bi-heart-pulse-fill me-2"></i>{{ NOMBRE_ORGANIZACION }}
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#menu"
                    aria-controls="menu" aria-expanded="false" aria-label="Abrir menú">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="menu">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item"><a class="nav-link" href="{% url 'core:inicio' %}">Inicio</a></li>
                    <li class="nav-item"><a class="nav-link" href="{% url 'catalogo:lista' %}">Prestaciones</a></li>
                    <li class="nav-item"><a class="nav-link" href="{% url 'core:nosotros' %}">Quiénes Somos</a></li>
                    {% if user.is_staff %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle text-info" href="#" data-bs-toggle="dropdown">Administración</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{% url 'catalogo:gestion' %}">Gestión de prestaciones</a></li>
                            <li><a class="dropdown-item" href="{% url 'catalogo:crear' %}">Nueva prestación</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{% url 'admin:index' %}">Admin de Django</a></li>
                        </ul>
                    </li>
                    {% endif %}
                </ul>
                <div class="d-flex align-items-center gap-2 flex-wrap">
                    <a href="{% url 'agenda:ver' %}" class="btn btn-outline-light position-relative">
                        <i class="bi bi-basket3"></i> Mi canasta
                        {% if canasta_cantidad > 0 %}
                        <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">{{ canasta_cantidad }}</span>
                        {% endif %}
                    </a>
                    {% if user.is_authenticated %}
                        <a href="{% url 'usuarios:perfil' %}" class="btn btn-light btn-sm"><i class="bi bi-person-circle"></i> {{ user.username }}</a>
                        <form method="post" action="{% url 'usuarios:logout' %}" class="d-inline">
                            {% csrf_token %}
                            <button type="submit" class="btn btn-outline-light btn-sm">Salir</button>
                        </form>
                    {% else %}
                        <a href="{% url 'usuarios:login' %}" class="btn btn-outline-light btn-sm">Ingresar</a>
                        <a href="{% url 'usuarios:registro' %}" class="btn btn-light btn-sm fw-semibold">Registrarse</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </nav>

    <!-- Contenedor de Mensajes Flash de Django -->
    <div class="container mt-3">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
        </div>
        {% endfor %}
    </div>

    <!-- Contenido Principal -->
    <main class="container my-4 flex-grow-1">
        {% block content %}{% endblock %}
    </main>

    <!-- Pie de Página -->
    <footer class="bg-dark text-white py-4 mt-auto">
        <div class="container text-center">
            <small>&copy; 2026 {{ NOMBRE_ORGANIZACION }} · Proyecto académico – Programación Back End (TI3041)</small>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```


### Partial reutilizable para campos de formulario


**`templates/_campo.html`**
```html
<div class="mb-3">
  {% if campo.field.widget.input_type == 'checkbox' %}
    <div class="form-check form-switch">
      {{ campo }}
      <label class="form-check-label fw-semibold" for="{{ campo.id_for_label }}">{{ campo.label }}</label>
    </div>
  {% else %}
    <label class="form-label fw-semibold" for="{{ campo.id_for_label }}">{{ campo.label }}</label>
    {{ campo }}
  {% endif %}
  {% if campo.help_text %}<div class="form-text">{{ campo.help_text }}</div>{% endif %}
  {% for error in campo.errors %}<div class="text-danger small mt-1">{{ error }}</div>{% endfor %}
</div>
```


### Vistas de la aplicación general (`apps/core`)


**`apps/core/views.py`**
```python
from django.db.models import Count, Q
from django.shortcuts import render

from apps.catalogo.models import EspecialidadMedica, PrestacionMedica


def inicio(request):
    """Portada: prestaciones destacadas y especialidades con su cantidad de prestaciones."""
    destacadas = PrestacionMedica.objects.filter(
        vigente=True, destacada=True, especialidad__activa=True
    ).select_related('especialidad')[:4]

    especialidades = EspecialidadMedica.objects.filter(activa=True).annotate(
        total=Count('prestaciones', filter=Q(prestaciones__vigente=True)))

    return render(request, 'core/inicio.html', {
        'destacadas': destacadas,
        'especialidades': especialidades,
        'total_prestaciones': PrestacionMedica.objects.filter(vigente=True).count(),
        'total_especialidades': especialidades.count(),
    })


def nosotros(request):
    """Información institucional del centro médico."""
    return render(request, 'core/nosotros.html')


def sin_permiso(request):
    """Destino de @user_passes_test cuando el usuario no tiene rol staff."""
    return render(request, 'core/sin_permiso.html', status=403)
```

**`apps/core/urls.py`**
```python
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('sin-permiso/', views.sin_permiso, name='sin_permiso'),
]
```


### Plantillas de la aplicación Core


**`templates/core/inicio.html`**
```html
{% extends 'base.html' %}
{% block title %}Inicio | {{ NOMBRE_ORGANIZACION }} - Centro Médico{% endblock %}

{% block content %}
<!-- Banner principal -->
<div class="p-5 mb-5 rounded-4 hero text-white shadow">
  <div class="row align-items-center">
    <div class="col-lg-8">
      <span class="badge bg-light text-dark px-3 py-2 fw-bold mb-3 fs-6"><i class="bi bi-calendar2-heart me-1"></i>Pre-agenda tus exámenes en línea</span>
      <h1 class="display-5 fw-bold mb-3">Tu salud, con atención oportuna y transparente</h1>
      <p class="lead opacity-75 mb-4">Explora nuestras prestaciones, arma tu canasta de exámenes y conoce tu copago estimado según tu previsión antes de agendar.</p>
      <div class="d-flex flex-wrap gap-2">
        <a href="{% url 'catalogo:lista' %}" class="btn btn-light btn-lg fw-bold px-4"><i class="bi bi-search me-2"></i>Ver prestaciones</a>
        <a href="{% url 'core:nosotros' %}" class="btn btn-outline-light btn-lg px-4"><i class="bi bi-info-circle me-2"></i>Sobre nosotros</a>
      </div>
    </div>
    <div class="col-lg-4 text-center d-none d-lg-block"><i class="bi bi-hospital opacity-75" style="font-size: 8rem;"></i></div>
  </div>
</div>

<!-- Beneficios -->
<div class="row g-3 mb-5 text-center">
  <div class="col-md-4"><div class="p-4 bg-white rounded-3 shadow-sm border h-100">
    <i class="bi bi-calculator text-rs display-5 mb-2"></i><h5 class="fw-bold mb-1">Copago estimado</h5>
    <p class="text-muted small mb-0">Simula tu bonificación Fonasa o Isapre antes de confirmar.</p></div></div>
  <div class="col-md-4"><div class="p-4 bg-white rounded-3 shadow-sm border h-100">
    <i class="bi bi-clipboard2-check text-success display-5 mb-2"></i><h5 class="fw-bold mb-1">Requisitos claros</h5>
    <p class="text-muted small mb-0">Cada examen indica su preparación: ayuno, orden médica y más.</p></div></div>
  <div class="col-md-4"><div class="p-4 bg-white rounded-3 shadow-sm border h-100">
    <i class="bi bi-clock-history text-warning display-5 mb-2"></i><h5 class="fw-bold mb-1">Cupos en línea</h5>
    <p class="text-muted small mb-0">Verás la disponibilidad real de cada prestación.</p></div></div>
</div>

<!-- Especialidades -->
{% if especialidades %}
<div class="mb-5">
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h2 class="h4 fw-bold mb-0"><i class="bi bi-collection-fill text-rs me-2"></i>Especialidades</h2>
    <a href="{% url 'catalogo:lista' %}" class="text-decoration-none fw-semibold">Ver todas &rarr;</a>
  </div>
  <div class="row g-3">
    {% for esp in especialidades %}
    <div class="col-6 col-md-3">
      <a href="{% url 'catalogo:lista' %}?especialidad={{ esp.slug }}" class="text-decoration-none">
        <div class="card border text-center p-3 h-100 shadow-sm bg-white tarjeta-prestacion">
          <i class="bi {{ esp.icono }} text-rs fs-2 mb-2"></i>
          <h6 class="fw-bold text-dark mb-1">{{ esp.nombre }}</h6>
          <span class="badge bg-light text-secondary border">{{ esp.total }} prestaciones</span>
        </div>
      </a>
    </div>
    {% endfor %}
  </div>
</div>
{% endif %}

<!-- Prestaciones destacadas -->
<div class="mb-5">
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h2 class="h4 fw-bold mb-0"><i class="bi bi-star-fill text-warning me-2"></i>Prestaciones destacadas</h2>
    <a href="{% url 'catalogo:lista' %}" class="btn btn-outline-dark btn-sm">Ver todo el catálogo</a>
  </div>
  <div class="row g-4">
    {% for p in destacadas %}
    <div class="col-md-6 col-lg-3">{% include 'catalogo/_tarjeta.html' %}</div>
    {% empty %}
    <div class="col-12 text-center py-5">
      <div class="card p-5 bg-white shadow-sm border">
        <i class="bi bi-box-seam display-3 text-muted mb-3"></i>
        <h5 class="text-secondary">Pronto tendremos prestaciones destacadas.</h5>
      </div>
    </div>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

**`templates/core/nosotros.html`**
```html
{% extends 'base.html' %}
{% block title %}Quiénes Somos | {{ NOMBRE_ORGANIZACION }}{% endblock %}

{% block content %}
<div class="row justify-content-center">
  <div class="col-lg-10">
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-5">
      <div class="hero text-white p-5 text-center">
        <i class="bi bi-heart-pulse display-3 mb-2"></i>
        <h1 class="fw-bold mb-2">Sobre {{ NOMBRE_ORGANIZACION }}</h1>
        <p class="lead opacity-75 mb-0">Centro de atención médica ambulatoria comprometido con tu bienestar.</p>
      </div>
      <div class="card-body p-4 p-md-5">
        <div class="row gy-4 mb-5">
          <div class="col-md-6">
            <h4 class="fw-bold mb-3"><i class="bi bi-heart-fill text-danger me-2"></i>Nuestra misión</h4>
            <p class="text-secondary">Facilitar el acceso a exámenes, procedimientos y consultas de especialidad con información clara de aranceles, requisitos y coberturas, para que cada paciente decida con tranquilidad.</p>
          </div>
          <div class="col-md-6">
            <h4 class="fw-bold mb-3"><i class="bi bi-patch-check-fill text-rs me-2"></i>Nuestros compromisos</h4>
            <ul class="list-group list-group-flush">
              <li class="list-group-item px-0"><i class="bi bi-check-circle-fill text-success me-2"></i><strong>Transparencia:</strong> aranceles y copagos estimados a la vista.</li>
              <li class="list-group-item px-0"><i class="bi bi-check-circle-fill text-success me-2"></i><strong>Preparación guiada:</strong> requisitos por cada examen.</li>
              <li class="list-group-item px-0"><i class="bi bi-check-circle-fill text-success me-2"></i><strong>Datos protegidos:</strong> acceso por roles y sesiones seguras.</li>
            </ul>
          </div>
        </div>
        <hr class="my-4">
        <div class="row g-4 text-center">
          <div class="col-md-4"><div class="p-3 bg-light rounded-3 border"><i class="bi bi-geo-alt text-rs fs-2 mb-2"></i><h6 class="fw-bold">Ubicación</h6><p class="small text-muted mb-0">Chillán, Región de Ñuble</p></div></div>
          <div class="col-md-4"><div class="p-3 bg-light rounded-3 border"><i class="bi bi-envelope-at text-info fs-2 mb-2"></i><h6 class="fw-bold">Correo</h6><p class="small text-muted mb-0">contacto@redsalud.cl</p></div></div>
          <div class="col-md-4"><div class="p-3 bg-light rounded-3 border"><i class="bi bi-telephone text-success fs-2 mb-2"></i><h6 class="fw-bold">Teléfono</h6><p class="small text-muted mb-0">+56 42 000 0000</p></div></div>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

**`templates/core/sin_permiso.html`**
```html
{% extends 'base.html' %}
{% block title %}Acceso restringido | {{ NOMBRE_ORGANIZACION }}{% endblock %}
{% block content %}
<div class="text-center py-5">
  <i class="bi bi-shield-lock text-danger" style="font-size:4rem"></i>
  <h1 class="h3 mt-3">Acceso restringido</h1>
  <p class="text-muted">Esta sección es solo para personal autorizado (rol staff).</p>
  <a href="{% url 'catalogo:lista' %}" class="btn btn-rs">Volver a las prestaciones</a>
</div>
{% endblock %}
```


### Plantillas del Catálogo


**`templates/catalogo/_estado.html`**
```html
{% if p.estado == 'DISPONIBLE' and p.cupos_diarios > 0 %}
  <span class="badge bg-success-subtle text-success border border-success-subtle">Disponible</span>
{% elif p.estado == 'SUSPENDIDO' %}
  <span class="badge bg-warning-subtle text-warning-emphasis border border-warning-subtle">Suspendido</span>
{% else %}
  <span class="badge bg-secondary-subtle text-secondary border">Sin cupos</span>
{% endif %}
```

**`templates/catalogo/_tarjeta.html`**
```html
<div class="card h-100 shadow-sm border tarjeta-prestacion bg-white">
  <div class="position-relative">
    {% if p.imagen %}
      <img src="{{ p.imagen.url }}" class="card-img-top imagen-prestacion" alt="{{ p.nombre }}">
    {% else %}
      <div class="imagen-vacia"><i class="bi bi-image"></i></div>
    {% endif %}
    {% if p.destacada %}
      <span class="position-absolute top-0 start-0 m-2 badge bg-warning text-dark fw-bold"><i class="bi bi-star-fill me-1"></i>Destacada</span>
    {% endif %}
  </div>
  <div class="card-body p-3 d-flex flex-column">
    <div class="d-flex justify-content-between align-items-center small text-muted mb-1">
      <span><i class="bi {{ p.especialidad.icono }}"></i> {{ p.especialidad.nombre }}</span>
      <span class="fw-semibold text-secondary">{{ p.codigo }}</span>
    </div>
    <h5 class="card-title fs-6 fw-bold mb-2" title="{{ p.nombre }}">{{ p.nombre }}</h5>
    <p class="card-text text-muted small flex-grow-1">{{ p.descripcion|truncatechars:90 }}</p>
    <div class="d-flex justify-content-between align-items-center pt-2 mt-2 border-top">
      <span class="fs-5 fw-bold text-dark">{{ p.arancel_formateado }}</span>
      {% include 'catalogo/_estado.html' %}
    </div>
    <div class="d-grid gap-2 mt-3">
      <a href="{{ p.get_absolute_url }}" class="btn btn-outline-dark btn-sm"><i class="bi bi-eye me-1"></i>Ver ficha</a>
      {% if p.disponible %}
      <form method="post" action="{% url 'agenda:agregar' p.pk %}">
        {% csrf_token %}
        <input type="hidden" name="cantidad" value="1">
        <input type="hidden" name="next" value="{{ request.get_full_path }}">
        <button class="btn btn-rs btn-sm fw-semibold w-100" type="submit"><i class="bi bi-basket3 me-1"></i>Agregar a la canasta</button>
      </form>
      {% else %}
      <button class="btn btn-secondary btn-sm" disabled>No disponible</button>
      {% endif %}
    </div>
  </div>
</div>
```

**`templates/catalogo/prestacion_lista.html`**
```html
{% extends 'base.html' %}
{% block title %}Prestaciones Médicas | {{ NOMBRE_ORGANIZACION }}{% endblock %}

{% block content %}
<div class="row g-4">
  <!-- Filtros laterales (especialidades) -->
  <div class="col-lg-3">
    <div class="card border shadow-sm rounded-3 mb-4 bg-white">
      <div class="card-header bg-rs text-white py-3 fw-bold"><i class="bi bi-funnel-fill me-2"></i>Especialidades</div>
      <div class="list-group list-group-flush">
        <a href="{% url 'catalogo:lista' %}{% if query_actual %}?q={{ query_actual|urlencode }}{% endif %}"
           class="list-group-item list-group-item-action d-flex justify-content-between align-items-center {% if not especialidad_sel %}active fw-bold{% endif %}">
          <span>Todas</span>
        </a>
        {% for esp in especialidades %}
        <a href="{% url 'catalogo:lista' %}?especialidad={{ esp.slug }}{% if query_actual %}&q={{ query_actual|urlencode }}{% endif %}"
           class="list-group-item list-group-item-action d-flex justify-content-between align-items-center {% if especialidad_sel == esp.slug %}active fw-bold{% endif %}">
          <span><i class="bi {{ esp.icono }} me-1"></i>{{ esp.nombre }}</span>
          <span class="badge rounded-pill bg-light text-dark border">{{ esp.total }}</span>
        </a>
        {% endfor %}
      </div>
    </div>

    {% if user.is_staff %}
    <div class="card bg-dark text-white p-3 rounded-3 shadow-sm mb-4">
      <h6 class="fw-bold text-info mb-2"><i class="bi bi-shield-lock me-1"></i>Personal autorizado</h6>
      <p class="small text-secondary mb-3">Puedes agregar nuevas prestaciones o editar las existentes.</p>
      <a href="{% url 'catalogo:crear' %}" class="btn btn-light btn-sm w-100 fw-bold"><i class="bi bi-plus-circle me-1"></i>Nueva prestación</a>
    </div>
    {% endif %}
  </div>

  <!-- Búsqueda, orden y grilla -->
  <div class="col-lg-9">
    <div class="card border shadow-sm p-3 mb-4 rounded-3 bg-white">
      <form method="get" class="row g-2 align-items-center">
        {% if especialidad_sel %}<input type="hidden" name="especialidad" value="{{ especialidad_sel }}">{% endif %}
        <div class="col-md-7">
          <div class="input-group">
            <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
            <input type="text" name="q" class="form-control border-start-0" placeholder="Buscar por nombre, código o descripción..." value="{{ query_actual }}">
          </div>
        </div>
        <div class="col-md-3">
          <select name="orden" class="form-select" onchange="this.form.submit()" aria-label="Ordenar por">
            <option value="nombre_asc" {% if orden_actual == 'nombre_asc' %}selected{% endif %}>Nombre: A-Z</option>
            <option value="arancel_asc" {% if orden_actual == 'arancel_asc' %}selected{% endif %}>Arancel: menor a mayor</option>
            <option value="arancel_desc" {% if orden_actual == 'arancel_desc' %}selected{% endif %}>Arancel: mayor a menor</option>
            <option value="duracion" {% if orden_actual == 'duracion' %}selected{% endif %}>Duración</option>
          </select>
        </div>
        <div class="col-md-2 d-grid"><button type="submit" class="btn btn-rs">Buscar</button></div>
      </form>
    </div>

    <p class="text-muted small">{{ total_resultados }} prestación(es) encontrada(s).</p>

    <div class="row g-4 mb-4">
      {% for p in prestaciones %}
      <div class="col-md-6 col-xl-4">{% include 'catalogo/_tarjeta.html' %}</div>
      {% empty %}
      <div class="col-12 text-center py-5">
        <div class="p-4 bg-white rounded-3 border shadow-sm">
          <i class="bi bi-search display-4 text-muted mb-2"></i>
          <h5 class="text-secondary">No se encontraron prestaciones con los filtros seleccionados.</h5>
          <a href="{% url 'catalogo:lista' %}" class="btn btn-outline-dark btn-sm mt-2">Ver todas las prestaciones</a>
        </div>
      </div>
      {% endfor %}
    </div>

    <!-- Paginación (conserva búsqueda, filtro y orden) -->
    {% if prestaciones.has_other_pages %}
    <nav aria-label="Navegación de páginas">
      <ul class="pagination justify-content-center flex-wrap">
        {% if prestaciones.has_previous %}
        <li class="page-item"><a class="page-link text-dark" href="?{% if querystring %}{{ querystring }}&{% endif %}page={{ prestaciones.previous_page_number }}">Anterior</a></li>
        {% else %}
        <li class="page-item disabled"><span class="page-link">Anterior</span></li>
        {% endif %}

        {% for i in prestaciones.paginator.page_range %}
          {% if prestaciones.number == i %}
          <li class="page-item active"><span class="page-link bg-rs border-0">{{ i }}</span></li>
          {% else %}
          <li class="page-item"><a class="page-link text-dark" href="?{% if querystring %}{{ querystring }}&{% endif %}page={{ i }}">{{ i }}</a></li>
          {% endif %}
        {% endfor %}

        {% if prestaciones.has_next %}
        <li class="page-item"><a class="page-link text-dark" href="?{% if querystring %}{{ querystring }}&{% endif %}page={{ prestaciones.next_page_number }}">Siguiente</a></li>
        {% else %}
        <li class="page-item disabled"><span class="page-link">Siguiente</span></li>
        {% endif %}
      </ul>
    </nav>
    {% endif %}
  </div>
</div>
{% endblock %}
```

**`templates/catalogo/prestacion_detalle.html`**
```html
{% extends 'base.html' %}
{% block title %}{{ p.nombre }} | {{ NOMBRE_ORGANIZACION }}{% endblock %}

{% block content %}
<nav aria-label="breadcrumb" class="mb-4">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="{% url 'core:inicio' %}" class="text-decoration-none text-dark">Inicio</a></li>
    <li class="breadcrumb-item"><a href="{% url 'catalogo:lista' %}" class="text-decoration-none text-dark">Prestaciones</a></li>
    <li class="breadcrumb-item"><a href="{% url 'catalogo:lista' %}?especialidad={{ p.especialidad.slug }}" class="text-decoration-none text-dark">{{ p.especialidad.nombre }}</a></li>
    <li class="breadcrumb-item active" aria-current="page">{{ p.nombre }}</li>
  </ol>
</nav>

{% if not p.vigente %}<div class="alert alert-warning">Esta prestación está dada de baja y solo es visible para el personal.</div>{% endif %}

<div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-5 bg-white">
  <div class="row g-0">
    <div class="col-md-6 d-flex align-items-center justify-content-center p-4 p-md-5 border-end">
      {% if p.imagen %}
        <img src="{{ p.imagen.url }}" alt="{{ p.nombre }}" class="img-fluid rounded-3" style="max-height: 420px; object-fit: contain;">
      {% else %}
        <div class="text-center py-5 text-muted"><i class="bi bi-image display-1"></i><p class="mt-2 mb-0 small">Fotografía no disponible</p></div>
      {% endif %}
    </div>

    <div class="col-md-6 p-4 p-md-5 d-flex flex-column justify-content-between">
      <div>
        <div class="d-flex justify-content-between align-items-start mb-2">
          <span class="badge bg-rs px-3 py-2 fw-semibold"><i class="bi {{ p.especialidad.icono }} me-1"></i>{{ p.especialidad.nombre }}</span>
          {% if user.is_staff %}
          <div class="btn-group btn-group-sm">
            <a href="{% url 'catalogo:editar' p.slug %}" class="btn btn-outline-primary"><i class="bi bi-pencil me-1"></i>Editar</a>
            {% if p.vigente %}<a href="{% url 'catalogo:eliminar' p.slug %}" class="btn btn-outline-danger"><i class="bi bi-trash me-1"></i>Dar de baja</a>{% endif %}
          </div>
          {% endif %}
        </div>

        <h1 class="h2 fw-bold text-dark mb-2">{{ p.nombre }}</h1>
        <div class="mb-3 text-muted">
          <span class="me-3"><i class="bi bi-upc-scan me-1"></i>Código: <strong>{{ p.codigo }}</strong></span>
          <span><i class="bi bi-clock me-1"></i>Duración: <strong>{{ p.duracion_minutos }} min</strong></span>
        </div>

        <div class="mb-3">
          <span class="display-5 fw-bold text-dark">{{ p.arancel_formateado }}</span>
          <span class="text-muted small ms-2">CLP arancel referencial</span>
        </div>

        <div class="mb-4">
          {% include 'catalogo/_estado.html' %}
          <span class="ms-2 small text-muted">Cupos diarios: <strong>{{ p.cupos_diarios }}</strong></span>
        </div>

        <h5 class="fw-bold fs-6 text-uppercase text-secondary">Descripción</h5>
        <p class="text-muted" style="white-space: pre-line;">{{ p.descripcion }}</p>

        {% if p.requisitos %}
        <div class="alert alert-light border"><strong><i class="bi bi-clipboard2-check me-1"></i>Requisitos / preparación:</strong><br>{{ p.requisitos|linebreaksbr }}</div>
        {% endif %}
      </div>

      <div class="border-top pt-4">
        {% if p.disponible %}
        <form method="post" action="{% url 'agenda:agregar' p.pk %}" class="row g-2 align-items-end">
          {% csrf_token %}
          <input type="hidden" name="next" value="{% url 'agenda:ver' %}">
          <div class="col-4"><label class="form-label small" for="cantidad">Cantidad</label>
            <input type="number" id="cantidad" name="cantidad" value="1" min="1" max="{{ p.cupos_diarios }}" class="form-control"></div>
          <div class="col-8 d-grid"><button class="btn btn-rs btn-lg fw-bold" type="submit"><i class="bi bi-basket3 me-2"></i>Agregar a la canasta</button></div>
        </form>
        {% else %}
        <button class="btn btn-secondary btn-lg w-100" disabled><i class="bi bi-slash-circle me-2"></i>No disponible por el momento</button>
        {% endif %}
      </div>
    </div>
  </div>
</div>

{% if relacionadas %}
<div class="mb-5">
  <h3 class="h4 fw-bold mb-3"><i class="bi bi-grid-3x3-gap-fill text-rs me-2"></i>Más de {{ p.especialidad.nombre }}</h3>
  <div class="row g-4">
    {% for rel in relacionadas %}
    <div class="col-md-4">
      <div class="card h-100 shadow-sm border bg-white">
        <div class="card-body p-3">
          <h6 class="fw-bold mb-1">{{ rel.nombre }}</h6>
          <span class="fw-bold text-dark">{{ rel.arancel_formateado }}</span>
          <div class="mt-2"><a href="{{ rel.get_absolute_url }}" class="btn btn-outline-dark btn-sm w-100">Ver ficha</a></div>
        </div>
      </div>
    </div>
    {% endfor %}
  </div>
</div>
{% endif %}
{% endblock %}
```

**`templates/catalogo/gestion_prestaciones.html`**
```html
{% extends 'base.html' %}
{% block title %}Gestión de Prestaciones | {{ NOMBRE_ORGANIZACION }}{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
  <div>
    <h1 class="h3 fw-bold mb-1"><i class="bi bi-clipboard2-pulse text-rs me-2"></i>Gestión de prestaciones</h1>
    <p class="text-muted small mb-0">Panel operativo para administrar el catálogo, aranceles, cupos y vigencia.</p>
  </div>
  <div class="d-flex gap-2">
    <a href="{% url 'catalogo:crear' %}" class="btn btn-rs fw-semibold"><i class="bi bi-plus-circle me-1"></i>Nueva prestación</a>
    <a href="{% url 'admin:catalogo_prestacionmedica_changelist' %}" target="_blank" class="btn btn-outline-dark"><i class="bi bi-shield-lock me-1"></i>Panel de control</a>
  </div>
</div>

<div class="card border shadow-sm p-3 mb-4 rounded-3 bg-white">
  <form method="get" class="row g-2">
    <div class="col-md-10"><input type="text" name="q" class="form-control" placeholder="Buscar por nombre, código o descripción..." value="{{ query }}"></div>
    <div class="col-md-2 d-grid"><button type="submit" class="btn btn-dark">Filtrar</button></div>
  </form>
</div>

<div class="card border-0 shadow-sm rounded-4 overflow-hidden bg-white">
  <div class="table-responsive">
    <table class="table table-hover align-middle mb-0">
      <thead class="table-dark">
        <tr><th>Código</th><th style="width:70px">Foto</th><th>Nombre</th><th>Especialidad</th><th>Arancel</th><th>Cupos</th><th>Estado</th><th>Vigencia</th><th class="text-end">Acciones</th></tr>
      </thead>
      <tbody>
        {% for p in prestaciones %}
        <tr {% if not p.vigente %}class="table-secondary"{% endif %}>
          <td class="fw-bold text-muted">{{ p.codigo }}</td>
          <td>
            {% if p.imagen %}<img src="{{ p.imagen.url }}" alt="{{ p.nombre }}" class="rounded border" style="width:48px;height:48px;object-fit:cover;">
            {% else %}<div class="bg-light rounded border d-flex align-items-center justify-content-center" style="width:48px;height:48px;"><i class="bi bi-image text-muted"></i></div>{% endif %}
          </td>
          <td>
            <a href="{{ p.get_absolute_url }}" class="fw-bold text-dark text-decoration-none">{{ p.nombre }}</a>
            {% if p.destacada %}<span class="badge bg-warning text-dark ms-1" style="font-size:.65rem;">Destacada</span>{% endif %}
          </td>
          <td><span class="badge bg-light text-dark border">{{ p.especialidad.nombre }}</span></td>
          <td class="fw-bold">{{ p.arancel_formateado }}</td>
          <td>{{ p.cupos_diarios }}</td>
          <td>{{ p.get_estado_display }}</td>
          <td>{% if p.vigente %}<span class="badge bg-success">Vigente</span>{% else %}<span class="badge bg-secondary">De baja</span>{% endif %}</td>
          <td class="text-end text-nowrap">
            <a href="{% url 'catalogo:editar' p.slug %}" class="btn btn-outline-primary btn-sm" title="Editar"><i class="bi bi-pencil"></i></a>
            {% if p.vigente %}
            <a href="{% url 'catalogo:eliminar' p.slug %}" class="btn btn-outline-danger btn-sm" title="Dar de baja"><i class="bi bi-trash"></i></a>
            {% else %}
            <form method="post" action="{% url 'catalogo:reactivar' p.slug %}" class="d-inline">
              {% csrf_token %}
              <button class="btn btn-outline-success btn-sm" type="submit" title="Reactivar"><i class="bi bi-arrow-counterclockwise"></i></button>
            </form>
            {% endif %}
          </td>
        </tr>
        {% empty %}
        <tr><td colspan="9" class="text-center py-5 text-muted"><i class="bi bi-inbox display-4 d-block mb-2"></i>No hay prestaciones registradas.</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  {% if prestaciones.has_other_pages %}
  <div class="card-footer bg-white py-3">
    <ul class="pagination pagination-sm justify-content-center mb-0">
      {% if prestaciones.has_previous %}<li class="page-item"><a class="page-link text-dark" href="?page={{ prestaciones.previous_page_number }}{% if query %}&q={{ query|urlencode }}{% endif %}">Anterior</a></li>{% endif %}
      {% for i in prestaciones.paginator.page_range %}
      <li class="page-item {% if prestaciones.number == i %}active{% endif %}"><a class="page-link {% if prestaciones.number != i %}text-dark{% endif %}" href="?page={{ i }}{% if query %}&q={{ query|urlencode }}{% endif %}">{{ i }}</a></li>
      {% endfor %}
      {% if prestaciones.has_next %}<li class="page-item"><a class="page-link text-dark" href="?page={{ prestaciones.next_page_number }}{% if query %}&q={{ query|urlencode }}{% endif %}">Siguiente</a></li>{% endif %}
    </ul>
  </div>
  {% endif %}
</div>
{% endblock %}
```

**`templates/catalogo/prestacion_form.html`**
```html
{% extends 'base.html' %}
{% block title %}{{ titulo_accion }} | {{ NOMBRE_ORGANIZACION }}{% endblock %}

{% block content %}
<div class="row justify-content-center">
  <div class="col-lg-8">
    <nav aria-label="breadcrumb" class="mb-3">
      <ol class="breadcrumb small">
        <li class="breadcrumb-item"><a href="{% url 'core:inicio' %}" class="text-decoration-none text-dark">Inicio</a></li>
        <li class="breadcrumb-item"><a href="{% url 'catalogo:gestion' %}" class="text-decoration-none text-dark">Gestión</a></li>
        <li class="breadcrumb-item active">{{ titulo_accion }}</li>
      </ol>
    </nav>

    <div class="card shadow-sm border-0 rounded-4 p-4 p-md-5 bg-white">
      <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3">
        <div>
          <h2 class="h4 fw-bold mb-1">{{ titulo_accion }}</h2>
          <p class="text-muted small mb-0">Completa la ficha para publicar o actualizar la prestación.</p>
        </div>
        <a href="{% url 'catalogo:gestion' %}" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left me-1"></i>Volver</a>
      </div>

      <!-- enctype multipart: necesario para subir la imagen (request.FILES) -->
      <form method="post" enctype="multipart/form-data" novalidate>
        {% csrf_token %}
        {% if form.non_field_errors %}<div class="alert alert-danger py-2 small">{{ form.non_field_errors }}</div>{% endif %}

        {% for campo in form %}
          {% include '_campo.html' with campo=campo %}
          {% if campo.name == 'imagen' and p and p.imagen %}
          <div class="mb-3 p-2 bg-light rounded d-flex align-items-center gap-3 border">
            <img src="{{ p.imagen.url }}" alt="Vista previa" style="width:50px;height:50px;object-fit:cover;" class="rounded border">
            <span class="small text-muted">Imagen cargada actualmente.</span>
          </div>
          {% endif %}
        {% endfor %}

        <div class="d-flex justify-content-end gap-2">
          <a href="{% url 'catalogo:gestion' %}" class="btn btn-outline-secondary">Cancelar</a>
          <button type="submit" class="btn btn-rs fw-bold px-4"><i class="bi bi-save me-1"></i>{{ boton_texto }}</button>
        </div>
      </form>
    </div>
  </div>
</div>
{% endblock %}
```

**`templates/catalogo/prestacion_confirmar_baja.html`**
```html
{% extends 'base.html' %}
{% block title %}Confirmar baja | {{ NOMBRE_ORGANIZACION }}{% endblock %}

{% block content %}
<div class="row justify-content-center">
  <div class="col-md-6">
    <div class="card border-danger shadow-sm rounded-4 overflow-hidden bg-white">
      <div class="card-header bg-danger text-white py-3">
        <h5 class="card-title mb-0"><i class="bi bi-exclamation-triangle-fill me-2"></i>Confirmar baja de prestación</h5>
      </div>
      <div class="card-body p-4 p-md-5 text-center">
        <i class="bi bi-trash3-fill text-danger display-3 mb-3"></i>
        <h4 class="fw-bold mb-2">¿Dar de baja esta prestación?</h4>
        <p class="text-muted mb-4">Se desactivará y dejará de mostrarse en el catálogo público. <strong>No se borra de la base de datos</strong> y podrás reactivarla después.</p>
        <div class="p-3 bg-light rounded-3 border mb-4 text-start">
          <ul class="list-unstyled mb-0">
            <li><strong>Código:</strong> {{ p.codigo }}</li>
            <li><strong>Nombre:</strong> {{ p.nombre }}</li>
            <li><strong>Especialidad:</strong> {{ p.especialidad.nombre }}</li>
            <li><strong>Arancel:</strong> {{ p.arancel_formateado }}</li>
          </ul>
        </div>
        <form method="post">
          {% csrf_token %}
          <div class="d-flex justify-content-center gap-2">
            <a href="{% url 'catalogo:gestion' %}" class="btn btn-outline-secondary px-4">Cancelar</a>
            <button type="submit" class="btn btn-danger px-4 fw-semibold"><i class="bi bi-trash-fill me-1"></i>Sí, dar de baja</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```


### Plantillas de la Canasta y el Comprobante


**`templates/agenda/canasta.html`**
```html
{% extends 'base.html' %}
{% block title %}Mi Canasta de Exámenes | {{ NOMBRE_ORGANIZACION }}{% endblock %}

{% block content %}
<div class="mb-4">
  <h1 class="h3 fw-bold mb-1"><i class="bi bi-basket3 text-rs me-2"></i>Canasta de exámenes</h1>
  <p class="text-muted small">Selección temporal guardada en tu sesión: no se registra en la base de datos hasta que confirmes.</p>
</div>

{% if not lineas %}
<div class="card border-0 shadow-sm rounded-4 text-center py-5 bg-white">
  <div class="card-body py-5">
    <i class="bi bi-basket text-muted display-1 mb-3"></i>
    <h3 class="fw-bold text-secondary">Tu canasta está vacía</h3>
    <p class="text-muted mb-4">Aún no has agregado prestaciones.</p>
    <a href="{% url 'catalogo:lista' %}" class="btn btn-rs px-4 py-2 fw-bold"><i class="bi bi-grid-3x3-gap me-2"></i>Explorar prestaciones</a>
  </div>
</div>
{% else %}
<div class="row g-4">
  <div class="col-lg-8">
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-3 bg-white">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-dark">
            <tr><th>Prestación</th><th>Arancel</th><th class="text-center" style="width:170px">Cantidad</th><th class="text-end">Subtotal</th><th style="width:60px"></th></tr>
          </thead>
          <tbody>
            {% for l in lineas %}
            <tr>
              <td>
                <a href="{{ l.prestacion.get_absolute_url }}" class="fw-bold text-dark text-decoration-none">{{ l.prestacion.nombre }}</a>
                <small class="text-muted d-block">{{ l.prestacion.especialidad.nombre }} · {{ l.prestacion.codigo }}</small>
                {% if not l.prestacion.disponible %}<span class="badge text-bg-danger">Ya no disponible</span>{% endif %}
              </td>
              <td class="text-muted">{{ l.prestacion.arancel_formateado }}</td>
              <td>
                <form method="post" action="{% url 'agenda:actualizar' l.prestacion.pk %}" class="d-flex gap-1">
                  {% csrf_token %}
                  <input type="number" name="cantidad" value="{{ l.cantidad }}" min="1" max="{{ l.maximo }}" class="form-control form-control-sm" aria-label="Cantidad">
                  <button class="btn btn-outline-primary btn-sm" type="submit" title="Actualizar"><i class="bi bi-check2"></i></button>
                </form>
              </td>
              <td class="text-end fw-bold">${{ l.total }}</td>
              <td class="text-end">
                <form method="post" action="{% url 'agenda:quitar' l.prestacion.pk %}">
                  {% csrf_token %}
                  <button class="btn btn-link text-danger p-0" type="submit" title="Quitar"><i class="bi bi-trash fs-5"></i></button>
                </form>
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
      <div class="card-footer bg-white p-3 d-flex justify-content-between align-items-center">
        <a href="{% url 'catalogo:lista' %}" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left me-1"></i>Seguir explorando</a>
        <form method="post" action="{% url 'agenda:vaciar' %}" onsubmit="return confirm('¿Deseas vaciar la canasta?');">
          {% csrf_token %}
          <button class="btn btn-outline-danger btn-sm" type="submit"><i class="bi bi-x-circle me-1"></i>Vaciar canasta</button>
        </form>
      </div>
    </div>
  </div>

  <div class="col-lg-4">
    <div class="card border-0 shadow-sm rounded-4 p-4 bg-white">
      <h5 class="fw-bold mb-3"><i class="bi bi-receipt me-2 text-rs"></i>Estimación de copago</h5>

      <form method="post" action="{% url 'agenda:prevision' %}" class="mb-3">
        {% csrf_token %}
        <label class="form-label small fw-semibold" for="prevision">Previsión</label>
        <div class="input-group">
          <select name="prevision" id="prevision" class="form-select">
            {% for valor, etiqueta, pct in previsiones %}
            <option value="{{ valor }}" {% if valor == prevision %}selected{% endif %}>{{ etiqueta }} ({{ pct }}%)</option>
            {% endfor %}
          </select>
          <button class="btn btn-outline-primary" type="submit">Aplicar</button>
        </div>
      </form>

      <div class="d-flex justify-content-between text-muted mb-2"><span>Subtotal aranceles ({{ unidades }} un.):</span><span>${{ subtotal }}</span></div>
      <div class="d-flex justify-content-between text-success mb-2"><span>Bonificación {{ prevision_label }} ({{ pct_cobertura }}%):</span><span>-${{ bonificacion }}</span></div>
      <div class="d-flex justify-content-between text-muted mb-2"><span>Copago:</span><span>${{ copago }}</span></div>
      <div class="d-flex justify-content-between text-muted mb-3"><span>Recargo de gestión ({{ pct_recargo }}%):</span><span>${{ recargo }}</span></div>
      <hr>
      <div class="d-flex justify-content-between align-items-center mb-1">
        <span class="fs-5 fw-bold">Total estimado:</span><span class="fs-4 fw-bold">${{ total }}</span>
      </div>
      <p class="small text-muted mb-4">Valores referenciales de simulación.</p>

      {% if user.is_authenticated %}
      <form method="post" action="{% url 'agenda:checkout' %}" class="d-grid">
        {% csrf_token %}
        <button class="btn btn-rs py-3 fw-bold" type="submit"><i class="bi bi-calendar-check me-2"></i>Confirmar pre-agendamiento</button>
      </form>
      {% else %}
      <div class="alert alert-warning small mb-3"><i class="bi bi-info-circle me-1"></i>Inicia sesión para confirmar tu solicitud.</div>
      <a href="{% url 'usuarios:login' %}?next={% url 'agenda:ver' %}" class="btn btn-rs w-100 py-3 fw-bold"><i class="bi bi-box-arrow-in-right me-2"></i>Iniciar sesión</a>
      {% endif %}
    </div>
  </div>
</div>
{% endif %}
{% endblock %}
```

**`templates/agenda/comprobante.html`**
```html
{% extends 'base.html' %}
{% block title %}Comprobante {{ folio }} | {{ NOMBRE_ORGANIZACION }}{% endblock %}

{% block content %}
<div class="row justify-content-center">
  <div class="col-lg-8">
    <div class="card border-0 shadow-sm rounded-4 p-4 p-md-5 bg-white">
      <div class="text-center mb-4">
        <i class="bi bi-check-circle-fill text-success display-1"></i>
        <h1 class="h2 fw-bold mt-3">Solicitud de pre-agendamiento registrada</h1>
        <p class="text-muted">Gracias, {{ paciente.first_name|default:paciente.username }}. Este es un comprobante simulado.</p>
        <span class="badge bg-dark fs-6 px-3 py-2">Folio: {{ folio }}</span>
      </div>

      <p class="mb-1"><strong>Paciente:</strong> {{ paciente.get_full_name|default:paciente.username }}{% if paciente.perfil %} · RUT {{ paciente.perfil.rut }}{% endif %}</p>
      <p><strong>Emitido:</strong> {{ fecha|date:"d/m/Y H:i" }} · <strong>Previsión:</strong> {{ prevision_label }}</p>

      <div class="text-start border rounded-3 p-3 p-md-4 mb-4 bg-light">
        <h5 class="fw-bold mb-3"><i class="bi bi-clipboard2-pulse me-2 text-rs"></i>Prestaciones solicitadas</h5>
        <ul class="list-group list-group-flush mb-3">
          {% for l in lineas %}
          <li class="list-group-item bg-transparent d-flex justify-content-between align-items-center px-0">
            <div><strong>{{ l.prestacion.nombre }}</strong>
              <span class="text-muted small d-block">{{ l.prestacion.codigo }} · {{ l.cantidad }} x {{ l.prestacion.arancel_formateado }}</span></div>
            <span class="fw-bold">${{ l.total }}</span>
          </li>
          {% endfor %}
        </ul>
        <div class="d-flex justify-content-between pt-2 border-top"><span>Subtotal aranceles:</span><span>${{ subtotal }}</span></div>
        <div class="d-flex justify-content-between text-success"><span>Bonificación ({{ pct_cobertura }}%):</span><span>-${{ bonificacion }}</span></div>
        <div class="d-flex justify-content-between text-muted"><span>Copago:</span><span>${{ copago }}</span></div>
        <div class="d-flex justify-content-between text-muted"><span>Recargo de gestión ({{ pct_recargo }}%):</span><span>${{ recargo }}</span></div>
        <div class="d-flex justify-content-between fs-5 fw-bold pt-2 border-top mt-2"><span>Total estimado:</span><span>${{ total }}</span></div>
      </div>

      <div class="d-flex justify-content-center gap-3">
        <a href="{% url 'catalogo:lista' %}" class="btn btn-rs fw-bold px-4">Seguir explorando</a>
        <a href="{% url 'usuarios:perfil' %}" class="btn btn-outline-secondary px-4">Ver mi cuenta</a>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```


### Plantillas de Usuarios


**`templates/usuarios/login.html`**
```html
{% extends 'base.html' %}
{% block title %}Iniciar Sesión | {{ NOMBRE_ORGANIZACION }}{% endblock %}

{% block content %}
<div class="row justify-content-center">
  <div class="col-md-6 col-lg-5">
    <div class="card shadow-sm border-0 rounded-4 p-4 p-md-5 bg-white">
      <div class="text-center mb-4">
        <i class="bi bi-person-lock text-rs display-4"></i>
        <h2 class="h4 fw-bold mt-2">Acceso a tu cuenta</h2>
        <p class="text-muted small">Ingresa tus datos para continuar</p>
      </div>
      <form method="post" novalidate>
        {% csrf_token %}
        <input type="hidden" name="next" value="{{ next }}">
        {% if form.non_field_errors %}<div class="alert alert-danger py-2 small">{{ form.non_field_errors }}</div>{% endif %}
        {% for campo in form %}{% include '_campo.html' with campo=campo %}{% endfor %}
        <div class="d-grid"><button type="submit" class="btn btn-rs py-2 fw-bold"><i class="bi bi-box-arrow-in-right me-1"></i>Iniciar sesión</button></div>
      </form>
      <hr class="my-4">
      <p class="text-center text-muted small mb-0">¿Eres nuevo? <a href="{% url 'usuarios:registro' %}" class="fw-semibold text-decoration-none">Regístrate gratis</a></p>
    </div>
  </div>
</div>
{% endblock %}
```

**`templates/usuarios/registro.html`**
```html
{% extends 'base.html' %}
{% block title %}Crear Cuenta | {{ NOMBRE_ORGANIZACION }}{% endblock %}

{% block content %}
<div class="row justify-content-center">
  <div class="col-md-8 col-lg-6">
    <div class="card shadow-sm border-0 rounded-4 p-4 p-md-5 bg-white">
      <div class="text-center mb-4">
        <i class="bi bi-person-plus-fill text-rs display-4"></i>
        <h2 class="h4 fw-bold mt-2">Crear cuenta de paciente</h2>
        <p class="text-muted small">Guarda tu información y confirma tus pre-agendamientos</p>
      </div>
      <form method="post" novalidate>
        {% csrf_token %}
        {% if form.non_field_errors %}<div class="alert alert-danger py-2 small">{{ form.non_field_errors }}</div>{% endif %}
        {% for campo in form %}{% include '_campo.html' with campo=campo %}{% endfor %}
        <div class="d-grid"><button type="submit" class="btn btn-rs py-2 fw-bold"><i class="bi bi-check-circle me-1"></i>Registrarme</button></div>
      </form>
      <hr class="my-4">
      <p class="text-center text-muted small mb-0">¿Ya tienes cuenta? <a href="{% url 'usuarios:login' %}" class="fw-semibold text-decoration-none">Inicia sesión</a></p>
    </div>
  </div>
</div>
{% endblock %}
```

**`templates/usuarios/perfil.html`**
```html
{% extends 'base.html' %}
{% block title %}Mi Cuenta | {{ NOMBRE_ORGANIZACION }}{% endblock %}

{% block content %}
<div class="row justify-content-center">
  <div class="col-lg-8">
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden bg-white">
      <div class="hero text-white p-4 p-md-5">
        <div class="d-flex align-items-center gap-3">
          <i class="bi bi-person-circle fs-1"></i>
          <div>
            <h2 class="h3 fw-bold mb-0">{{ usuario.get_full_name|default:usuario.username }}</h2>
            <span class="badge bg-light text-dark fw-bold mt-1">@{{ usuario.username }}</span>
            {% if usuario.is_staff %}<span class="badge bg-warning text-dark fw-bold mt-1 ms-1">Personal autorizado</span>{% endif %}
          </div>
        </div>
      </div>
      <div class="card-body p-4 p-md-5">
        <h5 class="fw-bold mb-3"><i class="bi bi-person-lines-fill me-2 text-rs"></i>Datos del usuario</h5>
        <div class="table-responsive">
          <table class="table table-bordered">
            <tbody>
              <tr><th class="bg-light text-muted w-25">Nombre completo</th><td>{{ usuario.get_full_name|default:"No especificado" }}</td></tr>
              <tr><th class="bg-light text-muted">Correo</th><td>{{ usuario.email|default:"No registrado" }}</td></tr>
              {% if perfil %}
              <tr><th class="bg-light text-muted">RUT</th><td>{{ perfil.rut }}</td></tr>
              <tr><th class="bg-light text-muted">Teléfono</th><td>{{ perfil.telefono|default:"No registrado" }}</td></tr>
              <tr><th class="bg-light text-muted">Rol institucional</th><td>{{ perfil.get_rol_display }}</td></tr>
              <tr><th class="bg-light text-muted">Previsión</th><td>{{ perfil.get_prevision_display }}</td></tr>
              {% endif %}
              <tr><th class="bg-light text-muted">Miembro desde</th><td>{{ usuario.date_joined|date:"d/m/Y" }}</td></tr>
            </tbody>
          </table>
        </div>
        <div class="mt-4 d-flex gap-2 flex-wrap">
          <a href="{% url 'catalogo:lista' %}" class="btn btn-rs fw-semibold"><i class="bi bi-grid me-1"></i>Explorar prestaciones</a>
          {% if usuario.is_staff %}<a href="{% url 'catalogo:gestion' %}" class="btn btn-dark"><i class="bi bi-clipboard2-pulse me-1"></i>Gestionar prestaciones</a>{% endif %}
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```


### Estilos (`static/css/estilos.css`)


**`static/css/estilos.css`**
```css
:root { --rs-primario: #0b6e8a; --rs-primario-oscuro: #08546a; --rs-acento: #7fe0d0; }
body { background-color: #f4f7f9; }
.bg-rs { background-color: var(--rs-primario) !important; }
.btn-rs { background-color: var(--rs-primario); border-color: var(--rs-primario); color: #fff; }
.btn-rs:hover { background-color: var(--rs-primario-oscuro); border-color: var(--rs-primario-oscuro); color: #fff; }
.text-rs { color: var(--rs-primario) !important; }
.navbar-brand i { color: var(--rs-acento); }
.tarjeta-prestacion { transition: transform .15s ease, box-shadow .15s ease; }
.tarjeta-prestacion:hover { transform: translateY(-3px); box-shadow: 0 .5rem 1rem rgba(0,0,0,.12); }
.imagen-prestacion { height: 180px; object-fit: cover; }
.imagen-vacia { height: 180px; display: flex; align-items: center; justify-content: center; background: #e9ecef; color: #adb5bd; font-size: 3rem; }
.hero { background: linear-gradient(135deg, var(--rs-primario) 0%, #0f8aa8 100%); }
```


---

## Paso 11: Enrutamiento Principal con Namespaces (`config/urls.py`)

Conecta todas las aplicaciones mediante `include` y *namespaces*, que permiten invocar rutas de forma única (`catalogo:lista`, `agenda:ver`, etc.):


**`config/urls.py`**
```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls', namespace='core')),
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),
    path('catalogo/', include('apps.catalogo.urls', namespace='catalogo')),
    path('agenda/', include('apps.agenda.urls', namespace='agenda')),
]

# Servir archivos multimedia durante el desarrollo local
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```


---

## Paso 12: Carga Inicial de Datos y Verificación del Sistema

### Comando personalizado `poblar_datos`
Crea **4 especialidades**, **8 prestaciones** coherentes con el giro (con imágenes de ejemplo generadas con Pillow, una prestación suspendida para demostrar los estados) y **3 usuarios de prueba** (administrador, personal de recepción y paciente). Es idempotente: puede ejecutarse varias veces.


**`apps/catalogo/management/commands/poblar_datos.py`**
```python
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
```


### Ejecución
```bash
python manage.py poblar_datos
python manage.py runserver
```

### Checklist de verificación manual
1. Entrar a `/` y revisar la portada y las prestaciones destacadas.
2. En `/catalogo/` probar búsqueda (`hemograma`), filtro por especialidad, orden y paginación.
3. Agregar exámenes a la canasta sin iniciar sesión y observar el contador del navbar.
4. Intentar agregar más unidades que los cupos disponibles (debe mostrar un error).
5. Cambiar la previsión y comprobar que el copago se recalcula.
6. Iniciar sesión como `paciente` y confirmar: se muestra el comprobante y la canasta queda vacía.
7. Con `paciente`, abrir `/catalogo/gestion/`: debe redirigir a “Acceso restringido”.
8. Con `recepcion`: crear una prestación con imagen, editarla, darla de baja y reactivarla.
9. Con `admin`: abrir `/admin/` y revisar títulos, filtros, búsqueda y edición rápida en grilla.

---

## Bitácora de Prompts (Uso Técnico y Ético de IA)

Herramienta utilizada: **Claude (Anthropic)**. Cada respuesta fue revisada, probada y adaptada por el equipo.

### Caso 1 – Arquitectura y modelado ORM
* **Prompt:** «Necesito modelar un centro médico en Django: una entidad de clasificación (especialidad) y una entidad principal (prestación) con ForeignKey protegida, código único, valores no negativos, estados cerrados, imagen y baja lógica. Sigue una arquitectura modular con una carpeta `apps/`.»
* **Respuesta técnica:** propuso `EspecialidadMedica` y `PrestacionMedica` con `on_delete=PROTECT`, `MinValueValidator`, `TextChoices` para el estado, `ImageField` y un booleano `vigente` para la baja lógica, separados en apps (`catalogo`, `usuarios`, `agenda`, `core`).
* **Adaptación aplicada:** se usó `IntegerField` en CLP (sin decimales) para el arancel; el `slug` se genera automáticamente desde el código en `save()`; se agregó la propiedad `disponible` para centralizar la regla de qué se puede agregar a la canasta y el campo `destacada` para la portada.

### Caso 2 – Optimización de consultas y búsqueda
* **Prompt:** «¿Cómo evito consultas N+1 en el catálogo que muestra la especialidad de cada prestación y cómo implemento búsqueda multicampo con paginación que conserve los filtros?»
* **Respuesta técnica:** recomendó `select_related('especialidad')`, objetos `Q` con `icontains`, `annotate(Count(..., filter=Q(...)))` para contar prestaciones por especialidad y reconstruir el *querystring* sin el parámetro `page` en los enlaces del paginador.
* **Adaptación aplicada:** se aplicó `select_related` también en la canasta y en el admin (`list_select_related`); el orden se valida con un diccionario (lista blanca) para evitar campos arbitrarios desde la URL.

### Caso 3 – Seguridad y sesiones
* **Prompt:** «¿Cómo protejo las vistas de gestión por rol y qué cuidados debo tener con la canasta guardada en `request.session`?»
* **Respuesta técnica:** sugirió `@login_required` + `@user_passes_test(is_staff)`, operaciones de la canasta solo por POST con CSRF, validar cantidades en el servidor y revalidar cupos al confirmar.
* **Adaptación aplicada:** se creó la vista `sin_permiso` (403) para evitar bucles de redirección con usuarios autenticados sin rol staff; se validó el parámetro `next` con `url_has_allowed_host_and_scheme`; el logout se hace por POST (requisito de Django 5).

---

## Control de Versiones en Pareja (Git y GitHub)

```bash
git init
git add .
git commit -m "feat: estructura inicial del proyecto y configuración"
git branch -M main
git remote add origin <URL-DEL-REPOSITORIO>
git push -u origin main
```

Recomendación de trabajo equitativo (cada integrante en su rama y *Pull Requests* revisados por el otro):

| Integrante | Módulos sugeridos |
| :--- | :--- |
| Integrante 1 | `config`, `apps/catalogo` (modelos, admin, CRUD), `poblar_datos` |
| Ariel Venegas | `apps/agenda` (canasta y comprobante), `apps/usuarios`, plantillas y README |

Usa mensajes de commit descriptivos (`feat:`, `fix:`, `docs:`) y hagan commits frecuentes y repartidos entre ambos.

---

## 📚 Glosario de Conceptos Técnicos

| Concepto | Definición Técnica |
| :--- | :--- |
| **ORM (Object-Relational Mapping)** | Capa de abstracción que mapea tablas relacionales a clases de Python, gestionando consultas sin escribir SQL directo. |
| **Migración** | Archivo de registro secuencial que versiona y sincroniza los cambios de estructura de datos en el motor SQL. |
| **Slug** | Texto simplificado (alfanumérico y guiones) que reemplaza identificadores numéricos en las URLs. |
| **CSRF (Cross-Site Request Forgery)** | Protección que exige un token criptográfico en peticiones POST para garantizar que provienen del propio sitio. |
| **Sesión HTTP** | Almacenamiento temporal del lado del servidor referenciado mediante cookies, que persiste estado entre peticiones. |
| **Context Processor** | Función de Django que inyecta variables globales en el contexto de todas las plantillas. |
| **Integridad Referencial (`PROTECT`)** | Política de clave foránea que bloquea la eliminación de un registro padre mientras existan dependientes. |
| **Baja lógica** | Desactivar un registro (`vigente=False`) en lugar de borrarlo físicamente, conservando el historial. |
| **Namespaces de URL** | Prefijos que permiten invocar rutas de forma única (`app_name:ruta`), evitando colisiones entre aplicaciones. |
| **N+1 queries** | Problema de rendimiento donde se ejecuta una consulta adicional por cada fila; se evita con `select_related` / `prefetch_related`. |
| **Módulo 11** | Algoritmo para calcular el dígito verificador del RUT chileno. |
