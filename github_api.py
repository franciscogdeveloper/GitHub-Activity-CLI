import json
import urllib.request

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


# Devuelve la lista de eventos públicos recientes de un usuario
def fetch_events(username):
    url = f"{API_URL}/users/{username}/events"
    request = urllib.request.Request(url, headers=HEADERS)

    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.load(response)
