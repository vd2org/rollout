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

    class compose:  # noqa
        @staticmethod
        def up(file: str, name: str, env: dict[str, str] = None, remove_orphans: bool = True) -> Result:
            """\
            Calls docker compose up command:

            Usage:  docker compose up [OPTIONS] [SERVICE...]

            Create and start containers

            Options:
                  --abort-on-container-exit   Stops all containers if any container was stopped. Incompatible with -d
                  --always-recreate-deps      Recreate dependent containers. Incompatible with --no-recreate.
                  --attach stringArray        Attach to service output.
                  --attach-dependencies       Attach to dependent containers.
                  --build                     Build images before starting containers.
              -d, --detach                    Detached mode: Run containers in the background
                  --exit-code-from string     Return the exit code of the selected service container. Implies \
            --abort-on-container-exit
                  --force-recreate            Recreate containers even if their configuration and image haven't changed.
                  --no-build                  Don't build an image, even if it's missing.
                  --no-color                  Produce monochrome output.
                  --no-deps                   Don't start linked services.
                  --no-log-prefix             Don't print prefix in logs.
                  --no-recreate               If containers already exist, don't recreate them. Incompatible with \
            --force-recreate.
                  --no-start                  Don't start the services after creating them.
                  --pull string               Pull image before running ("always"|"missing"|"never") (default "missing")
                  --quiet-pull                Pull without printing progress information.
                  --remove-orphans            Remove containers for services not defined in the Compose file.
              -V, --renew-anon-volumes        Recreate anonymous volumes instead of retrieving data from the \
            previous containers.
                  --scale scale               Scale SERVICE to NUM instances. Overrides the scale setting in the \
            Compose file if present.
              -t, --timeout int               Use this timeout in seconds for container shutdown when attached or \
            when containers are already running. (default 10)
                  --wait                      Wait for services to be running|healthy. Implies detached mode.
            """

            env = env or dict()

            params = ["-f", "-", "-p", name, "up", "--no-build", "-d"]

            if remove_orphans:
                params.append("--remove-orphans")

            try:
                response = d.compose(_in=file, _env=env, *params)
                return Result(response.stdout.decode(), response.stderr.decode())
            except ErrorReturnCode as e:
                raise Error(e.exit_code, e.stdout.decode(), e.stderr.decode()) from None
