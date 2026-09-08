from django.core.management.base import BaseCommand
from django.conf import settings
from app.models import Transaction
import os


class Command(BaseCommand):
    help = "Remove arquivos de comprovante sem transação correspondente"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra o que seria removido, sem deletar',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Remove de fato os comprovantes órfãos (sem esta flag nada é apagado)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        delete = options['delete']

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

        if dry_run:
            self.stdout.write(
                self.style.WARNING('Modo DRY-RUN: nenhum arquivo será removido')
            )
        elif not delete:
            self.stdout.write(
                self.style.WARNING(
                    'Nenhum arquivo será removido sem --delete (use --dry-run para prévia)'
                )
            )

        for root, dirs, files in os.walk(proofs_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                relative = os.path.relpath(filepath, settings.MEDIA_ROOT)

                if relative in valid_paths:
                    kept_count += 1
                else:
                    deleted_count += 1
                    action = "WOULD DELETE" if dry_run or not delete else "DELETED"
                    self.stdout.write(f"  {action}: {relative}")
                    if delete and not dry_run:
                        os.remove(filepath)

        verb = "removeria" if dry_run or not delete else "removidos"
        self.stdout.write(
            self.style.SUCCESS(
                f"\nResultado: {deleted_count} {verb}, {kept_count} mantidos"
            )
        )