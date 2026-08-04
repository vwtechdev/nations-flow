from django.core.management.base import BaseCommand
from django.conf import settings
from app.models import Transaction
import os


class Command(BaseCommand):
    help = "Remove arquivos de comprovante sem transação correspondente"

    def handle(self, *args, **options):
        proofs_dir = os.path.join(settings.MEDIA_ROOT, "proofs")
        if not os.path.isdir(proofs_dir):
            self.stdout.write("Diretório de comprovantes não encontrado.")
            return

        valid_paths = set(
            Transaction.objects.filter(proof__isnull=False).values_list(
                "proof", flat=True
            )
        )

        deleted_count = 0
        kept_count = 0

        for root, dirs, files in os.walk(proofs_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                relative = os.path.relpath(filepath, settings.MEDIA_ROOT)

                if relative in valid_paths:
                    kept_count += 1
                else:
                    os.remove(filepath)
                    deleted_count += 1
                    self.stdout.write(f"  DELETED: {relative}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nResultado: {deleted_count} removidos, {kept_count} mantidos"
            )
        )
