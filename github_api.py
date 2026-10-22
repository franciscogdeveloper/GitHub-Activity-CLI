import json
import urllib.request
import re
import urllib.error
from datetime import datetime

# Dirección base de la API de GitHub
API_URL = "https://api.github.com"

# Segundos máximos de espera por una respuesta
TIMEOUT = 10

# Cabeceras que se envían en cada petición
HEADERS = {
    "User-Agent": "github-activity-cli",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


# Formato válido de usuario en GitHub: 1 a 39 caracteres, letras, números
# y guiones, sin guion al inicio ni al final
USERNAME_PATTERN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?")


# Error al consultar la API de GitHub
class GitHubApiError(Exception):
    pass


# Devuelve la lista de eventos públicos recientes de un usuario
def fetch_events(username):
    if not USERNAME_PATTERN.fullmatch(username):
        raise GitHubApiError(f"'{username}' no es un nombre de usuario válido de GitHub.")
    
    url = f"{API_URL}/users/{username}/events"
    request = urllib.request.Request(url, headers=HEADERS)

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise GitHubApiError(describe_http_error(error, username))
    except (urllib.error.URLError, TimeoutError):
        raise GitHubApiError("No se pudo conectar con GitHub. Revisa tu conexión.")
    except json.JSONDecodeError:
        raise GitHubApiError("La respuesta de GitHub no es válida.")


# Traduce un error HTTP de GitHub a un mensaje claro
def describe_http_error(error, username):
    if error.code == 404:
        return f"El usuario '{username}' no existe en GitHub."

    # Límite de peticiones agotado: GitHub indica cuándo se reinicia
    if error.code in (403, 429) and error.headers.get("X-RateLimit-Remaining") == "0":
        reset = int(error.headers.get("X-RateLimit-Reset", 0))
        reset_time = datetime.fromtimestamp(reset).strftime("%H:%M")
        return f"Se agotó el límite de peticiones a GitHub. Intenta de nuevo después de las {reset_time}."

    return f"GitHub respondió con error {error.code}."
