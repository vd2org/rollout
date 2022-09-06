# Copyright (C) 2022 by Vd.
# This file is part of RollOut, the docker compose/docker stack deploy daemon
# RollOut is released under the MIT License (see LICENSE).


from envreader import EnvReader, Field


class Settings(EnvReader):
    SECRET: str = Field(description="Deploy secret")


ENV = Settings()
