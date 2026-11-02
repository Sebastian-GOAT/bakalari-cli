import base64
import json
from pathlib import Path
from typing import Optional, Tuple
from uuid import uuid4

import keyring
import typer
from keyring.errors import KeyringError
from rich import print as stdout

CONFIG_FILE = Path('auth.json')
KEYRING_SERVICE = 'bakalari-cli'
ACCESS_TOKEN_ACCOUNT = 'access_token'
REFRESH_TOKEN_ACCOUNT = 'refresh_token'
LEGACY_KEYRING_ACCOUNT = 'tokens'
TOKEN_MANIFEST_ACCOUNT = 'tokens_manifest'
TOKEN_CHUNK_PREFIX = 'tokens_chunk_'
TOKEN_CHUNK_SIZE = 1000


def _delete_keyring_entry(account: str):
    if keyring.get_password(KEYRING_SERVICE, account) is not None:
        keyring.delete_password(KEYRING_SERVICE, account)


def _delete_token_chunks(generation: str, count: int):
    for index in range(count):
        _delete_keyring_entry(f'{TOKEN_CHUNK_PREFIX}{generation}_{index}')


def _parse_manifest(value: Optional[str]):
    if value is None:
        return None

    manifest = json.loads(value)
    generation = manifest['generation']
    count = manifest['count']
    if (
        not isinstance(generation, str)
        or not generation
        or not isinstance(count, int)
        or count < 1
        or count > 10000
    ):
        raise ValueError('Invalid token manifest')

    return manifest


def _store_tokens(access_token: str, refresh_token: str):
    try:
        old_manifest = keyring.get_password(KEYRING_SERVICE, TOKEN_MANIFEST_ACCOUNT)
        try:
            old_manifest = _parse_manifest(old_manifest)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            old_manifest = None
    except (KeyringError, OSError) as exc:
        stdout("[bold red]❌ ERROR: couldn't read existing credentials from the system keyring")
        raise typer.Exit(code=1) from exc

    encoded_tokens = base64.b64encode(json.dumps({
        'access_token': access_token,
        'refresh_token': refresh_token
    }).encode('utf-8')).decode('ascii')
    generation = uuid4().hex
    chunks = [
        encoded_tokens[index:index + TOKEN_CHUNK_SIZE]
        for index in range(0, len(encoded_tokens), TOKEN_CHUNK_SIZE)
    ]

    try:
        for index, chunk in enumerate(chunks):
            account = f'{TOKEN_CHUNK_PREFIX}{generation}_{index}'
            keyring.set_password(KEYRING_SERVICE, account, chunk)

        keyring.set_password(
            KEYRING_SERVICE,
            TOKEN_MANIFEST_ACCOUNT,
            json.dumps({'generation': generation, 'count': len(chunks)})
        )

        _delete_keyring_entry(ACCESS_TOKEN_ACCOUNT)
        _delete_keyring_entry(REFRESH_TOKEN_ACCOUNT)
        _delete_keyring_entry(LEGACY_KEYRING_ACCOUNT)
        if old_manifest:
            _delete_token_chunks(old_manifest['generation'], old_manifest['count'])
    except (KeyringError, OSError) as exc:
        stdout("[bold red]❌ ERROR: couldn't store credentials in the system keyring")
        raise typer.Exit(code=1) from exc


def save_config(access_token: str, refresh_token: str, school_url: str):
    _store_tokens(access_token, refresh_token)

    with CONFIG_FILE.open('w', encoding='utf-8') as file:
        json.dump({'school_url': school_url}, file, indent=4, ensure_ascii=False)


def _read_legacy_tokens() -> Optional[Tuple[str, str]]:
    try:
        stored_tokens = keyring.get_password(KEYRING_SERVICE, LEGACY_KEYRING_ACCOUNT)
    except (KeyringError, OSError) as exc:
        stdout("[bold red]❌ ERROR: couldn't retrieve credentials from the system keyring")
        raise typer.Exit(code=1) from exc

    if stored_tokens is None:
        return None

    try:
        tokens = json.loads(stored_tokens)
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        stdout("[bold red]❌ ERROR: stored credentials are invalid")
        raise typer.Exit(code=1) from exc

    if not isinstance(access_token, str) or not isinstance(refresh_token, str):
        stdout("[bold red]❌ ERROR: stored credentials are invalid")
        raise typer.Exit(code=1)

    _store_tokens(access_token, refresh_token)
    return (access_token, refresh_token)


def _read_chunked_tokens() -> Optional[Tuple[str, str]]:
    try:
        manifest_value = keyring.get_password(KEYRING_SERVICE, TOKEN_MANIFEST_ACCOUNT)
        manifest = _parse_manifest(manifest_value)
        if manifest is None:
            return None

        encoded_tokens = ''.join(
            keyring.get_password(
                KEYRING_SERVICE,
                f"{TOKEN_CHUNK_PREFIX}{manifest['generation']}_{index}"
            ) or ''
            for index in range(manifest['count'])
        )
    except (KeyringError, OSError) as exc:
        stdout("[bold red]❌ ERROR: couldn't retrieve credentials from the system keyring")
        raise typer.Exit(code=1) from exc
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        stdout("[bold red]❌ ERROR: stored credentials are invalid")
        raise typer.Exit(code=1) from exc

    try:
        tokens = json.loads(base64.b64decode(encoded_tokens, validate=True).decode('utf-8'))
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        stdout("[bold red]❌ ERROR: stored credentials are invalid")
        raise typer.Exit(code=1) from exc

    if not isinstance(access_token, str) or not access_token or not isinstance(refresh_token, str) or not refresh_token:
        stdout("[bold red]❌ ERROR: stored credentials are invalid")
        raise typer.Exit(code=1)

    return (access_token, refresh_token)


def load_config() -> Optional[Tuple[str, str, str]]:
    try:
        with CONFIG_FILE.open('r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError) as exc:
        stdout("[bold red]❌ ERROR: couldn't read auth.json")
        raise typer.Exit(code=1) from exc

    if not isinstance(data, dict):
        stdout("[bold red]❌ ERROR: auth.json has an invalid format")
        raise typer.Exit(code=1)

    school_url = data.get('school_url')
    if not isinstance(school_url, str) or not school_url:
        stdout("[bold red]❌ ERROR: auth.json is missing the school URL")
        raise typer.Exit(code=1)

    if 'access_token' in data or 'refresh_token' in data:
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        if (
            not isinstance(access_token, str)
            or not access_token
            or not isinstance(refresh_token, str)
            or not refresh_token
        ):
            stdout("[bold red]❌ ERROR: auth.json contains incomplete credentials")
            raise typer.Exit(code=1)

        _store_tokens(access_token, refresh_token)
        with CONFIG_FILE.open('w', encoding='utf-8') as file:
            json.dump({'school_url': school_url}, file, indent=4, ensure_ascii=False)
        return (access_token, refresh_token, school_url)

    tokens = _read_chunked_tokens()
    if tokens is not None:
        return (*tokens, school_url)

    try:
        access_token = keyring.get_password(KEYRING_SERVICE, ACCESS_TOKEN_ACCOUNT)
        refresh_token = keyring.get_password(KEYRING_SERVICE, REFRESH_TOKEN_ACCOUNT)
    except (KeyringError, OSError) as exc:
        stdout("[bold red]❌ ERROR: couldn't retrieve credentials from the system keyring")
        raise typer.Exit(code=1) from exc

    if access_token is None and refresh_token is None:
        legacy_tokens = _read_legacy_tokens()
        if legacy_tokens is None:
            return None
        return (*legacy_tokens, school_url)
    if access_token is None or refresh_token is None:
        stdout("[bold red]❌ ERROR: stored credentials are incomplete")
        raise typer.Exit(code=1)

    if not access_token or not refresh_token:
        stdout("[bold red]❌ ERROR: stored credentials are invalid")
        raise typer.Exit(code=1)

    _store_tokens(access_token, refresh_token)
    return (access_token, refresh_token, school_url)


def delete_config():
    try:
        manifest = _parse_manifest(
            keyring.get_password(KEYRING_SERVICE, TOKEN_MANIFEST_ACCOUNT)
        )
        if manifest:
            _delete_token_chunks(manifest['generation'], manifest['count'])

        for account in (
            TOKEN_MANIFEST_ACCOUNT,
            ACCESS_TOKEN_ACCOUNT,
            REFRESH_TOKEN_ACCOUNT,
            LEGACY_KEYRING_ACCOUNT
        ):
            if keyring.get_password(KEYRING_SERVICE, account) is not None:
                keyring.delete_password(KEYRING_SERVICE, account)
    except (KeyringError, OSError) as exc:
        stdout("[bold red]❌ ERROR: couldn't delete credentials from the system keyring")
        raise typer.Exit(code=1) from exc

    CONFIG_FILE.unlink(missing_ok=True)


def load_config_formatted():

    config = load_config()
    if config: return config
    else:
        stdout("[bold red]❌ ERROR: you are not logged in")
        raise typer.Exit(code=1)