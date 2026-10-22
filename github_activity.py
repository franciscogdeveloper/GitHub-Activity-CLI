import sys

import github_api

USAGE = "Uso: python github_activity.py <usuario>"


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 1

    # Muestra los errores de la API como un mensaje limpio, sin traceback
    try:
        events = github_api.fetch_events(argv[0])
    except github_api.GitHubApiError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if not events:
        print("No hay actividad reciente.")
        return 0

    # Tipo de evento y repositorio
    for event in events:
        print(f"- {event['type']} en {event['repo']['name']}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
