import os

from config.settings import *

DATABASES["default"]["HOST"] = os.getenv("TEST_DATABASE_HOST", "127.0.0.1")
DATABASES["default"]["PORT"] = os.getenv("TEST_DATABASE_PORT", "5434")
DATABASES["default"]["USER"] = os.getenv("TEST_DATABASE_USER", "default")
DATABASES["default"]["PASSWORD"] = os.getenv("TEST_DATABASE_PASSWORD", "qwerty123")
DATABASES["default"]["NAME"] = os.getenv("TEST_DATABASE_DB", "stripe_test")
