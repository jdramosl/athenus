"""
Django command to wait for the database to be available.

This is necessary to correclt orchestrate Athenus DB and Django Backend App.
"""
import time
from psycopg2 import OperationalError as Psycopg2OpError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write('Waiting for database...')
        db_up = False

        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True

            except(Psycopg2OpError, OperationalError):
                self.stdout.write('Datbase unavailable, waiting for 1 second...')  # noqa
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
