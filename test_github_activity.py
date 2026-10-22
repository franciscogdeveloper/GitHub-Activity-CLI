import io
import json
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

import formatter
import github_api
from github_activity import main


# Crea un evento de prueba con el tipo, repositorio y payload indicados
def make_event(event_type, repo="user/repo", payload=None):
    return {"type": event_type, "repo": {"name": repo}, "payload": payload or {}}


class TestFormatter(unittest.TestCase):
    # Cada tipo conocido genera su frase
    def test_format_event_known_types(self):
        self.assertEqual(formatter.format_event(make_event("PushEvent")), "Hizo push a user/repo")
        self.assertEqual(
            formatter.format_event(make_event("IssuesEvent", payload={"action": "opened"})),
            "Abrió un issue en user/repo",
        )
        self.assertEqual(
            formatter.format_event(make_event("CreateEvent", payload={"ref_type": "branch", "ref": "dev"})),
            "Creó la rama dev en user/repo",
        )

    # Un tipo sin mensaje propio muestra su nombre
    def test_format_event_unknown_type(self):
        self.assertEqual(formatter.format_event(make_event("GollumEvent")), "GollumEvent en user/repo")

    # Agrupa solo los eventos consecutivos con el mismo mensaje
    def test_summarize_groups_consecutive_events(self):
        push = make_event("PushEvent")
        issue = make_event("IssuesEvent", payload={"action": "opened"})

        self.assertEqual(
            formatter.summarize([push, push, push, issue, issue, push]),
            [
                "Hizo 3 pushes a user/repo",
                "Abrió un issue en user/repo (2 veces)",
                "Hizo push a user/repo",
            ],
        )


# Respuesta falsa de urlopen con el JSON indicado
def fake_response(data):
    return io.BytesIO(json.dumps(data).encode("utf-8"))


# Error HTTP falso con el código y las cabeceras indicadas
def fake_http_error(code, headers=None):
    return urllib.error.HTTPError("https://api.github.com", code, "error", headers or {}, None)


# Durante cada test, urlopen se reemplaza por un mock
@patch("urllib.request.urlopen")
class TestGitHubApi(unittest.TestCase):
    # Devuelve los eventos cuando GitHub responde bien
    def test_fetch_events_returns_events(self, mock_urlopen):
        mock_urlopen.return_value = fake_response([make_event("PushEvent")])

        self.assertEqual(github_api.fetch_events("octocat"), [make_event("PushEvent")])

    # Rechaza nombres inválidos sin llamar a la API
    def test_invalid_username_does_not_call_api(self, mock_urlopen):
        with self.assertRaises(github_api.GitHubApiError):
            github_api.fetch_events("mal usuario!")

        mock_urlopen.assert_not_called()

    # Un 404 se informa como usuario inexistente
    def test_user_not_found(self, mock_urlopen):
        mock_urlopen.side_effect = fake_http_error(404)

        with self.assertRaisesRegex(github_api.GitHubApiError, "no existe"):
            github_api.fetch_events("octocat")

    # Un 403 con el límite en cero se informa como límite agotado
    def test_rate_limit_exceeded(self, mock_urlopen):
        headers = {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1700000000"}
        mock_urlopen.side_effect = fake_http_error(403, headers)

        with self.assertRaisesRegex(github_api.GitHubApiError, "límite"):
            github_api.fetch_events("octocat")

    # Un fallo de red se informa como problema de conexión
    def test_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("sin red")

        with self.assertRaisesRegex(github_api.GitHubApiError, "conectar"):
            github_api.fetch_events("octocat")


@patch("urllib.request.urlopen")
class TestCli(unittest.TestCase):
    # Ejecuta la CLI y devuelve el código de salida y lo que imprimió
    def run_cli(self, *argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(argv))
        return code, stdout.getvalue(), stderr.getvalue()

    # Muestra la actividad agrupada y termina con código 0
    def test_shows_activity(self, mock_urlopen):
        push = make_event("PushEvent")
        mock_urlopen.return_value = fake_response([push, push])

        code, out, _ = self.run_cli("octocat")

        self.assertEqual(code, 0)
        self.assertIn("- Hizo 2 pushes a user/repo", out)

    # Sin eventos muestra un mensaje en lugar de una lista vacía
    def test_no_activity(self, mock_urlopen):
        mock_urlopen.return_value = fake_response([])

        code, out, _ = self.run_cli("octocat")

        self.assertEqual(code, 0)
        self.assertIn("No hay actividad reciente", out)

    # Sin argumentos o con argumentos de más muestra el uso y termina con código 1
    def test_wrong_arguments_show_usage(self, mock_urlopen):
        for argv in ([], ["uno", "dos"]):
            with self.subTest(argv=argv):
                code, _, err = self.run_cli(*argv)
                self.assertEqual(code, 1)
                self.assertIn("Uso:", err)

        mock_urlopen.assert_not_called()

    # Los errores de la API se muestran en stderr con código 1
    def test_api_error_returns_error_code(self, mock_urlopen):
        mock_urlopen.side_effect = fake_http_error(404)

        code, _, err = self.run_cli("octocat")

        self.assertEqual(code, 1)
        self.assertIn("Error:", err)
