"""
WSGI config for project_electron project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

path = '/data/htdocs/aurora/aurora'

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bag_transfer.settings")
except ModuleNotFoundError:
    if path not in sys.path:
        sys.path.append(path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bag_transfer.settings")

application = get_wsgi_application()
