from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
import time

class Command(BaseCommand):
	def handle(self, *args, **options):
		self.stdout.write('Waiting for database...')
		database_up = False
		while database_up is False:
			try:
				self.check(databases=['default'])
				database_up = True
			except (OperationalError):
				self.stdout.write('Database down, waiting 5 second...')
				time.sleep(5)

		self.stdout.write(self.style.SUCCESS('Database ready.'))