import os
from .base import *

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

raw_allowed_hosts = os.getenv("ALLOWED_HOSTS", "")
env_hosts = [h.strip() for h in raw_allowed_hosts.split(",") if h.strip()]

ALLOWED_HOSTS = [
    "*",
    ".vercel.app",
    "*.vercel.app",
    "localhost",
    "127.0.0.1",
] + env_hosts
