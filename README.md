# GitHub Activity CLI

Aplicación de línea de comandos que muestra la actividad reciente de un usuario de GitHub,
usando la [API pública de GitHub](https://docs.github.com/en/rest/activity/events).

Hecha solo con la librería estándar de Python (sin dependencias externas), como parte del
[proyecto GitHub User Activity de roadmap.sh](https://roadmap.sh/projects/github-user-activity).

## Requisitos

- Python 3 (probado con Python 3.15)

## Uso

```bash
python github_activity.py <usuario>
```

Ejemplo:

```bash
python github_activity.py torvalds
```

```
- Hizo 10 pushes a torvalds/linux
- Creó la rama bluez-address-type en torvalds/subsurface-for-dirk
- Hizo push a torvalds/linux
- Fusionó un pull request en subsurface/subsurface
- Hizo 5 pushes a torvalds/linux
```

Los eventos consecutivos que son iguales se agrupan en una sola línea.

## Errores

El programa muestra un mensaje claro y termina con código `1` cuando:

- No se indica un usuario, o se indican varios.
- El nombre de usuario no tiene un formato válido (en ese caso no llega a consultar la API).
- El usuario no existe (`404`).
- Se agotó el límite de peticiones de GitHub. Sin autenticación son 60 por hora; el mensaje indica a qué hora se reinicia.
- No hay conexión o GitHub no responde.

## Limitaciones

La API de GitHub ya no incluye la cantidad de commits en los eventos de push,
por eso el programa muestra cuántos **pushes** se hicieron y no cuántos commits.

## Tests

```bash
python -m unittest -v
```

Los tests reemplazan las llamadas a la API por respuestas simuladas (mocks),
así que no necesitan internet ni consumen el límite de peticiones.

## Estructura del proyecto

```
github_activity.py        # Interfaz de línea de comandos: valida argumentos y muestra la actividad
github_api.py             # Consulta a la API de GitHub y manejo de errores
formatter.py              # Convierte los eventos en frases y agrupa los repetidos
test_github_activity.py   # Tests del formatter, la API y la CLI
```
