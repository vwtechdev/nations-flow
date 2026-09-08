from django.core.management.base import BaseCommand
from django.conf import settings
from app.models import Transaction, Church, Shepherd
import os


class Command(BaseCommand):
    help = "Remove arquivos de mídia órfãos (comprovantes e contratos) sem registro correspondente"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra o que seria removido, sem deletar',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Remove de fato os arquivos órfãos (sem esta flag nada é apagado)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        delete = options['delete']

        # (subdiretório de MEDIA_ROOT, modelo, campo FileField)
        targets = [
            ("proofs", Transaction, "proof"),
            ("churches", Church, "contract"),
            ("shepherds", Shepherd, "contract"),
        ]

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

        total_deleted = 0
        total_kept = 0

        for subdir, model, field in targets:
            media_dir = os.path.join(settings.MEDIA_ROOT, subdir)
            if not os.path.isdir(media_dir):
                continue

            valid_paths = set(
                model.objects.filter(**{f'{field}__isnull': False}).values_list(
                    field, flat=True
                )
            )

            deleted_count = 0
            kept_count = 0

            for root, dirs, files in os.walk(media_dir):
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
                    f"[{subdir}] {deleted_count} {verb}, {kept_count} mantidos"
                )
            )
            total_deleted += deleted_count
            total_kept += kept_count

        verb = "removeria" if dry_run or not delete else "removidos"
        self.stdout.write(
            self.style.SUCCESS(
                f"\nResultado: {total_deleted} {verb}, {total_kept} mantidos"
            )
        )