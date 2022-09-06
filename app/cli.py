# Copyright (C) 2022 by Vd.
# This file is part of RollOut, the docker compose/docker stack deploy daemon
# RollOut is released under the MIT License (see LICENSE).
import json
import sys
from datetime import datetime
from hashlib import sha512
from io import FileIO, TextIOBase

import requests
import click
import jwt

JWT_TTL = 60 * 5  # 5 minutes


@click.command()
@click.option('-s', '--secret', required=True, help='Webhook deploy secret')
@click.option('-u', '--url', required=True, help='Webhook url')
@click.option('-n', '--name', required=True, help='Stack deployment name')
@click.option('-f', '--file', default='-', help='Stack file')
@click.option('-e', '--env', multiple=True, help='Environment variable')
def hello(secret, url, name, file, env):
    """Calls deploy webhook."""

    try:
        env = dict(e.split("=") for e in env)
    except:
        click.echo(click.style('Error: malformed env option. Must be "NAME=VALUE".', fg='red'))
        sys.exit(1)

    if file.strip() == '-':
        text = sys.stdin.read()
    else:
        with open(file, mode="rt") as f:
            text = f.read()

    data = json.dumps({
        'file': text,
        'name': name,
        'env': env
    }).encode()

    payload = {'exp': int(datetime.utcnow().timestamp()) + JWT_TTL, 'body_hash': sha512(data).hexdigest()}
    token = jwt.encode(payload, secret, algorithm="HS256")
    print(token)
    res = requests.post(url, data=data, headers={"Authorization": f"Bearer {token}"})

    if res.status_code == 401:
        click.echo(click.style('Error: unauthorized!', fg='red'))

    data = res.json()

    if res.status_code == 444:
        click.echo(click.style(f"Error status code {data['code']}!", fg='red'))
        click.echo("")

    click.echo("STDOUT:")
    click.echo("")
    click.echo(data["stdout"])

    click.echo("STDERR:")
    click.echo("")
    click.echo(data["stderr"])

    if res.status_code == 444:
        sys.exit(1)


if __name__ == '__main__':
    hello()
