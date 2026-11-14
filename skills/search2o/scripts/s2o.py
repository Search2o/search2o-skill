"""search and execAgent against the Search2o REST API.

Usage:
    python3 s2o.py search '{"query": "..."}'
    python3 s2o.py execAgent '{"agentName": "...", "inputs": {"query": "..."}}'

Reads the server address from SEARCH2O_SERVER, and the integration token from
SEARCH2O_TOKEN or ~/.search2o/token. Prints one JSON object on success. On failure it
prints a message to stderr and exits non-zero, so the assistant sees what went wrong.
"""

import json
import os
import sys
import urllib.error
import urllib.request

TIMEOUT = 600
TOKEN_FILE = "~/.search2o/token"
SERVER_FILE = "~/.search2o/server"


def stop(message):
    print(message, file=sys.stderr)
    raise SystemExit(1)


def server():
    value = (os.environ.get("SEARCH2O_SERVER") or "").strip() or read(SERVER_FILE)
    if not value:
        stop(f"No agent server address. Set SEARCH2O_SERVER, or put the address in "
             f"{SERVER_FILE}, such as https://search2o.example.com.")
    return value.rstrip("/")


def read(where):
    try:
        return open(os.path.expanduser(where), encoding="utf-8").read().strip()
    except OSError:
        return ""


def token():
    value = (os.environ.get("SEARCH2O_TOKEN") or "").strip() or read(TOKEN_FILE)
    if not value:
        stop(f"No integration token. Set SEARCH2O_TOKEN, or put the token in {TOKEN_FILE}. "
             "Create one from your profile in the Search2o GUI.")
    return value


def call(path, body):
    request = urllib.request.Request(
        f"{server()}/api/exec/{path}",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        stop(http_message(error))
    except urllib.error.URLError as error:
        stop(f"Could not reach the Search2o agent server at {server()}: {error.reason}")
    except TimeoutError:
        stop(f"The agent did not finish within {TIMEOUT} seconds.")


def http_message(error):
    try:
        payload = json.loads(error.read().decode())
    except Exception:
        payload = {}
    message = ((payload.get("error") or {}).get("message") or str(error.reason)).rstrip(".")
    if error.code == 401:
        return f"The Search2o token was refused: {message}. Ask the person for a new token."
    if error.code == 403:
        return (f"The Search2o token is not allowed to do this: {message}. An integration "
                "token can search, run agents and manage that person's own conversations.")
    return f"Search2o refused the call ({error.code}): {message}"


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("search", "execAgent"):
        stop('Usage: s2o.py search \'{"query": "..."}\' | '
             's2o.py execAgent \'{"agentName": "...", "inputs": {"query": "..."}}\'')
    try:
        body = json.loads(sys.argv[2])
    except json.JSONDecodeError as error:
        stop(f"The second argument must be a JSON object: {error}")
    result = call(sys.argv[1], body)
    if result.get("resultCode") == "mustLogin":
        stop("The Search2o token expired during the run. Ask the person for a new token.")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
