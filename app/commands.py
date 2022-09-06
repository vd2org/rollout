# Copyright (C) 2022 by Vd.
# This file is part of RollOut, the docker compose/docker stack deploy daemon
# RollOut is released under the MIT License (see LICENSE).


from typing import NamedTuple

from sh import ErrorReturnCode
from sh import docker as d  # noqa


class Result(NamedTuple):
    stderr: str
    stdout: str


class Error(Exception):
    def __init__(self, code: int, stdout: str, stderr: str):
        self._code = code
        self._stdout = stdout
        self._stderr = stderr

    @property
    def code(self) -> int:
        return self._code

    @property
    def stdout(self) -> str:
        return self._stdout

    @property
    def stderr(self) -> str:
        return self._stderr


class docker:  # noqa
    class stack:  # noqa
        @staticmethod
        def deploy(file: str, name: str, env: dict[str, str] = None, prune: bool = True, auth: bool = True) -> Result:
            """\
            Calls docker stack deploy command:

            Usage:  docker stack deploy [OPTIONS] STACK

            Deploy a new stack or update an existing stack

            Aliases:
              deploy, up

            Options:
              -c, --compose-file strings   Path to a Compose file, or "-" to read from stdin
                  --orchestrator string    Orchestrator to use (swarm|kubernetes|all)
                  --prune                  Prune services that are no longer referenced
                  --resolve-image string   Query the registry to resolve image digest and supported platforms \
            ("always"|"changed"|"never") (default "always")
                  --with-registry-auth     Send registry authentication details to Swarm agents
            """

            env = env or dict()

            params = ["-c", "-"]

            if prune:
                params.append("--prune")

            if auth:
                params.append("--with-registry-auth")

            params.append(name)

            try:
                response = d.stack.deploy(_in=file, _env=env, *params)
                return Result(response.stdout.decode(), response.stderr.decode())
            except ErrorReturnCode as e:
                raise Error(e.exit_code, e.stdout.decode(), e.stderr.decode()) from None
