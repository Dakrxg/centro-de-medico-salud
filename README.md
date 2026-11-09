## Evaluacion 3 Centro de Medico y Salud


## Nombre de la Organización o Plataforma: RedSalud Vital
## Modelo de Negocio / Giro: Centro de atención médica ambulatoria (exámenes, procedimientos y consultas de especialidad
## Integrantes del Equipo: Diego Monteleone – 22603297-5 | Ariel Venegas – 22-002-184-K
## Entidad de Contexto / Agrupación (ORM): EspecialidadMedica 
## Entidad Principal Gestionable (ORM): PrestacionMedica
## Propósito de la Sesión request.session: Pre-agendamiento de prestaciones (canasta de exámenes) con cálculo de copago estimado según previsión (Fonasa, Isapre y Particular) 

## Bitácora de Prompts de IA 

La herramienta que usamos a Gemini como apoyo técnico durante el desarrollo del proyecto, justificando críticamente la adaptación del código generado a nuestras reglas de negocio

## Caso 1: Arquitectura y Sesiones HTTP (request.session)

Enfoque: Manejo de colección transitoria para el pre-agendamiento.

Prompt utilizado: Actúa como experto en Django. Necesito crear un sistema de 'Canasta de Exámenes' usando `request.session` donde los pacientes puedan agregar prestaciones médicas temporalmente. ¿Cómo estructuro una clase de Python independiente para inicializar, agregar y vaciar esta sesión sin guardar aún en la base de datos?

Respuesta técnica de la IA: La IA sugirió crear un archivo separado definiendo una clase con un método `__init__` que inicializa `self.session = request.session` y verifica si existe la clave de la canasta. Además, proporcionó la estructura base para los métodos `agregar(producto)`, `eliminar(producto)`, `guardar()` (llamando a `self.session.modified = True`) y `limpiar()`.

Adaptación aplicada: En lugar de dejar el código genérico de un "carrito de compras", lo implementamos en `apps/agenda/canasta.py`. Modificamos los parámetros para que reciba nuestra entidad `Prestacion` (en lugar de un "producto" genérico) y ajustamos la lógica matemática interna para que, al iterar sobre los elementos, calcule el total del arancel y un subtotal de copago estimado según las reglas específicas de nuestro centro médico.

## Caso 2: ORM, Consultas y Validaciones

Enfoque: ntegridad relacional y validaciones numéricas en la Base de Datos.

Prompt utilizado: En Django ORM, tengo un modelo 'Prestacion' relacionado mediante ForeignKey a 'Especialidad'. ¿Cuál es la mejor práctica para evitar que un administrador elimine por error una Especialidad si ya tiene prestaciones clínicas asignadas, y cómo restrinjo a nivel de base de datos que el campo 'arancel' jamás reciba un valor negativo?

Respuesta técnica de la IA: La IA recomendó usar el argumento `on_delete=models.PROTECT` en la `ForeignKey` para levantar una excepción `ProtectedError` en lugar de borrar en cascada. Para el campo numérico, indicó importar `MinValueValidator` desde `django.core.validators` y añadirlo a la lista de validadores del campo `arancel`.

Adaptación aplicada: Se implementó `models.PROTECT` en el modelo `Prestacion` dentro de `apps/catalogo/models.py` para asegurar que el historial médico no se rompa por borrados accidentales en la entidad de contexto. Aplicamos el `MinValueValidator(0)` al campo `arancel`, pero lo complementamos nosotros mismos con un campo `vigente = models.BooleanField(default=True)` para cumplir con la regla de baja lógica exigida por la rúbrica, garantizando que el borrado sea solo visual.

## Caso 3: Seguridad y Autenticación por Roles

Enfoque: Protección de las rutas del CRUD operativo (Backoffice).

Prompt utilizado: Tengo vistas basadas en funciones en Django que realizan las operaciones Update y Delete para registros médicos. ¿Cómo puedo proteger estas rutas usando decoradores para que un usuario estándar no pueda acceder escribiendo la URL, y solo permita el paso a los usuarios que tengan perfil de administrador (is_staff)?

Respuesta técnica de la IA: La IA proporcionó un ejemplo anidando dos decoradores sobre la función de la vista: `@login_required(login_url='login')` para exigir que la sesión esté iniciada, y `@user_passes_test(lambda u: u.is_staff)` para validar el atributo del rol.

Adaptación aplicada: Integramos ambos decoradores en las vistas de modificación y baja lógica en `apps/catalogo/views.py`. Sin embargo, adaptamos el código para que, en caso de que un paciente (usuario autenticado pero sin rol staff) intente acceder al CRUD, la redirección de `@user_passes_test` no lo envíe al login de nuevo, sino que lo redirija a nuestra vista dedicada `sin_permiso` (ubicada en `apps/core/views.py`), mejorando así la seguridad y la experiencia de usuario de la plataforma.

Paso a paso(Instalacion)

# 1. Clonar el repositorio
git clone https://github.com/Dakrxg/centro-de-medico-salud.git

# 2. Crear y activar el entorno virtual
python -m venv .venv
#   Windows:      .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear el archivo de variables de entorno
#   Windows:      copy .env.example .env

# 5. Aplicar migraciones (ya vienen incluidas en el repositorio)
python manage.py migrate

# 6. Cargar datos de ejemplo: 4 especialidades, 8 prestaciones y 3 usuarios
python manage.py poblar_datos

# 7. Levantar el servidor
python manage.py runserver

Sitio: http://127.0.0.1:8000/ 
Catálogo: http://127.0.0.1:8000/catalogo/ 
Admin de Django: http://127.0.0.1:8000/admin/

## Credenciales de prueba

En python manage.py poblar_datos

Usuario	/ Contraseña	/Rol
admin	/Admin12345!	/Superusuario (staff): accede al Django Admin y a la gestión CRUD
recepcion/	Recepcion12345!/	Staff: accede a la gestión CRUD del sitio
paciente/	Paciente12345!/	Usuario estándar (previsión Fonasa)