import os
from .base import *

DEBUG = True

raw_allowed_hosts = os.getenv("ALLOWED_HOSTS", "")
env_hosts = [h.strip() for h in raw_allowed_hosts.split(",") if h.strip()]

ALLOWED_HOSTS = [
    "*",
    ".vercel.app",
    "*.vercel.app",
    "localhost",
    "127.0.0.1",
] + env_hosts

INTERNAL_IPS = ["127.0.0.1"]
