"""
Test custom Django managment commands
"""
from unittest.mock import patch # Helps replacing db methods by mocking code hta simulates db behaviors. # noqa

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

@patch('core.management.commands.wait_for_db.Command.check') # This is the real code that's going to be  patched (temporarily replaced) for mocking # noqa
class CommandTests(SimpleTestCase):
    """Test commands."""
    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database is ready."""
        patched_check.return_value = True
        call_command('wait_for_db') # This tests also the command is setup correctly (it's a custom manage.py command) # noqa
        patched_check.assert_called_once_with(databases=['default']) # Check we're calling the right database # noqa

    @patch('time.sleep')  # Mocks sleep so the test doesn't actually wait.
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """
            Test waiting for database when getting OperationalError. # noqa
            1. The first argument: patched_sleep matches the immediate decorator which is patch sleep. # noqa
            2. The second argument patched_check matches the following operator which is patch core wait for db command check. # noqa
        """
        # Check db -> Wait (sleep) -> Check again # noqa
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True] # 6 outcomes # noqa

        call_command('wait_for_db') # Tests the command # noqa

        self.assertEqual(patched_check.call_count, 6) # Checks 6 outcomes # noqa
        patched_check.assert_called_with(databases=['default']) # Use default db # noqa