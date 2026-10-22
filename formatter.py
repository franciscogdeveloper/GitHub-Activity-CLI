# Tipos de referencia de Git traducidos
REF_TYPES = {
    "branch": "la rama",
    "tag": "la etiqueta",
}

# Acciones sobre issues y pull requests traducidas
ACTIONS = {
    "opened": "Abrió",
    "closed": "Cerró",
    "reopened": "Reabrió",
    "merged": "Fusionó",
}


def push_message(repo, payload):
    return f"Hizo push a {repo}"


# CreateEvent puede ser un repositorio nuevo, una rama o una etiqueta
def create_message(repo, payload):
    if payload.get("ref_type") == "repository":
        return f"Creó el repositorio {repo}"
    ref_type = REF_TYPES.get(payload.get("ref_type"), payload.get("ref_type"))
    return f"Creó {ref_type} {payload.get('ref')} en {repo}"


def delete_message(repo, payload):
    ref_type = REF_TYPES.get(payload.get("ref_type"), payload.get("ref_type"))
    return f"Eliminó {ref_type} {payload.get('ref')} en {repo}"


def issue_message(repo, payload):
    action = ACTIONS.get(payload.get("action"), "Actualizó")
    return f"{action} un issue en {repo}"


def pull_request_message(repo, payload):
    action = ACTIONS.get(payload.get("action"), "Actualizó")
    return f"{action} un pull request en {repo}"


def issue_comment_message(repo, payload):
    return f"Comentó en un issue de {repo}"


def watch_message(repo, payload):
    return f"Dio una estrella a {repo}"


def fork_message(repo, payload):
    return f"Hizo fork de {repo}"


def release_message(repo, payload):
    return f"Publicó una versión en {repo}"


# Tipo de evento y función que genera su mensaje
EVENT_MESSAGES = {
    "PushEvent": push_message,
    "CreateEvent": create_message,
    "DeleteEvent": delete_message,
    "IssuesEvent": issue_message,
    "PullRequestEvent": pull_request_message,
    "IssueCommentEvent": issue_comment_message,
    "WatchEvent": watch_message,
    "ForkEvent": fork_message,
    "ReleaseEvent": release_message,
}


# Convierte un evento en una frase; los tipos sin mensaje propio muestran su nombre
def format_event(event):
    repo = event["repo"]["name"]
    build_message = EVENT_MESSAGES.get(event["type"])
    if build_message is None:
        return f"{event['type']} en {repo}"
    return build_message(repo, event.get("payload", {}))


# Agrupa los eventos consecutivos que generan el mismo mensaje
def summarize(events):
    groups = []
    for event in events:
        message = format_event(event)
        if groups and groups[-1]["message"] == message:
            groups[-1]["count"] += 1
        else:
            groups.append({"message": message, "event": event, "count": 1})

    return [format_group(group) for group in groups]


# Agrega la cantidad cuando hay más de un evento
def format_group(group):
    if group["count"] == 1:
        return group["message"]

    event = group["event"]
    if event["type"] == "PushEvent":
        return f"Hizo {group['count']} pushes a {event['repo']['name']}"
    return f"{group['message']} ({group['count']} veces)"
