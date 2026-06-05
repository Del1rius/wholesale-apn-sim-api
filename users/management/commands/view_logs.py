"""
Management command to view application logs.

Usage:
    python manage.py view_logs [log_type] [--lines N]

Examples:
    python manage.py view_logs errors
    python manage.py view_logs api --lines 50
    python manage.py view_logs general --lines 100
"""

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'View application logs'

    def add_arguments(self, parser):
        parser.add_argument(
            'log_type',
            type=str,
            nargs='?',
            default='general',
            choices=['general', 'errors', 'django', 'celery', 'api', 'database'],
            help='Type of log to view'
        )
        parser.add_argument(
            '--lines',
            type=int,
            default=50,
            help='Number of lines to display (default: 50)'
        )

    def handle(self, *args, **options):
        log_type = options['log_type']
        lines = options['lines']

        log_file = settings.BASE_DIR / 'logs' / f'{log_type}.log'

        if not log_file.exists():
            self.stdout.write(self.style.WARNING(f'Log file not found: {log_file}'))
            self.stdout.write(self.style.WARNING('The log file will be created when the first log entry is written.'))
            return

        self.stdout.write(self.style.SUCCESS(f'\n📋 Viewing last {lines} lines of {log_type}.log:\n'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:]

                for line in last_lines:
                    # Color code based on log level
                    if '[ERROR]' in line or '[CRITICAL]' in line:
                        self.stdout.write(self.style.ERROR(line.rstrip()))
                    elif '[WARNING]' in line:
                        self.stdout.write(self.style.WARNING(line.rstrip()))
                    elif '[INFO]' in line:
                        self.stdout.write(self.style.SUCCESS(line.rstrip()))
                    else:
                        self.stdout.write(line.rstrip())

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading log file: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 80))
        self.stdout.write(self.style.SUCCESS(f'End of {log_type}.log\n'))
