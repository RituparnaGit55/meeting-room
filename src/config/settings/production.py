import os
from .base import *

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

hosts_env = os.getenv("ALLOWED_HOSTS", "")
extra_hosts = [h.strip() for h in hosts_env.split(",") if h.strip()]

ALLOWED_HOSTS = [
    ".vercel.app",
    "*.vercel.app",
    "localhost",
    "127.0.0.1",
] + extra_hosts
