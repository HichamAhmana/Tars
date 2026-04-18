"""
Django management command: python manage.py run_engine

Starts the TARS voice engine in the foreground so it can be launched
from the dashboard or CLI without needing a separate terminal.
"""
import signal
import sys

from django.core.management.base import BaseCommand

from api.engine_manager import start_engine, stop_engine, is_running
from api.models import EngineSettings


class Command(BaseCommand):
    help = 'Start the TARS voice engine as a managed subprocess.'

    def handle(self, *args, **options):
        settings = EngineSettings.get()
        settings.engine_running = True
        settings.save()

        self.stdout.write(self.style.SUCCESS('Starting TARS voice engine...'))

        started = start_engine()
        if not started:
            self.stdout.write(self.style.WARNING('Engine was already running.'))
            return

        self.stdout.write('Engine running. Press Ctrl+C to stop.\n')

        def _shutdown(sig, frame):
            self.stdout.write('\nStopping TARS engine...')
            stop_engine()
            settings.engine_running = False
            settings.save()
            sys.exit(0)

        signal.signal(signal.SIGINT,  _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)

        # Keep the management command alive while the engine runs
        import time
        while is_running():
            time.sleep(1)

        settings.engine_running = False
        settings.save()
        self.stdout.write(self.style.SUCCESS('Engine stopped.'))
