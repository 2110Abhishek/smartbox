"""
WSGI config for smartbox project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os
import logging
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Safe auto-migration on deployment startup
try:
    from django.core.management import call_command
    call_command("migrate", interactive=False)
    from inventory.models import Product
    if not Product.objects.exists():
        call_command("seed_demo_data")
except Exception as e:
    logging.warning("Auto-migration during WSGI startup skipped or failed: %s", e)
