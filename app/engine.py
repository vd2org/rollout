# Copyright (C) 2022 by Vd.
# This file is part of RollOut, the docker compose/docker stack deploy daemon
# RollOut is released under the MIT License (see LICENSE).


import json
import sys
from hashlib import sha512
from hmac import compare_digest
from json import JSONDecodeError

import jwt
from jwt import InvalidTokenError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

from commands import docker, Error
from env import ENV


class AuthError(Exception):
    pass


JWT_OPTS = {"require": ["exp"]}


async def deploy(request: Request):
    try:
        body = await request.body()

        token = request.headers.get('Authorization', "").removeprefix("Bearer ")
        parsed_body_hash = jwt.decode(token, ENV.SECRET, algorithms="HS256", options=JWT_OPTS).get('body_hash', "")

        if not compare_digest(sha512(body).hexdigest(), parsed_body_hash):
            raise AuthError

        data = json.loads(body)

        file = data['file']
        name = data['name']
        env = data['env']

        res = docker.stack.deploy(file, name, env)

        res = {
            "stdout": res.stdout,
            "stderr": res.stderr
        }

        return JSONResponse(res)
    except Error as e:
        res = {
            "code": e.code,
            "stdout": e.stdout,
            "stderr": e.stderr
        }

        return JSONResponse(res, status_code=444)
    except (JSONDecodeError, KeyError):
        return PlainTextResponse("Malformed json", status_code=400)
    except (AuthError, InvalidTokenError):
        return PlainTextResponse("Unauthorized", status_code=401)


routes = [
    Route('/{path:path}', deploy, methods=['POST']),
]

app = Starlette(debug=True, routes=routes)
