"""
Loading environment variables from project-level .env file.
"""

import os
from dotenv import load_dotenv

env_vars = [
    'REDIS_HOST',
    'REDIS_PORT',
    'REDIS_DB',
]

class EnvVars:
    def __init__(self, envs=None):
        envs = envs if envs else os.environ.keys()
        for e in envs:
            setattr(self, e, os.getenv(e))
load_dotenv('.env-template')
env = EnvVars(env_vars)
