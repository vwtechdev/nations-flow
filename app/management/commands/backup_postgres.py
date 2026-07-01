import os
import glob
import subprocess
import gzip
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Backup diário do PostgreSQL via pg_dump (network Docker)"

    def handle(self, *args, **options):
        # =========================
        # CONFIGURAÇÕES
        # =========================
        backup_dir = "/backups"
        retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", 10))

        db_host = os.getenv("POSTGRES_HOST", "db")  # nome do service
        db_name = os.getenv("POSTGRES_DB")
        db_user = os.getenv("POSTGRES_USER")
        db_password = os.getenv("POSTGRES_PASSWORD")

        os.makedirs(backup_dir, exist_ok=True)

        env = os.environ.copy()
        env["PGPASSWORD"] = db_password

        # =========================
        # 1️⃣ LIMPAR BACKUPS ANTIGOS
        # =========================
        for file in glob.glob(f"{backup_dir}/backup_*.sql.gz"):
            file_time = datetime.fromtimestamp(os.path.getmtime(file))
            if datetime.now() - file_time > timedelta(days=retention_days):
                os.remove(file)
                self.stdout.write(f"🧹 Backup removido: {file}")

        # =========================
        # 2️⃣ CRIAR BACKUP
        # =========================
        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M")
        backup_file = f"{backup_dir}/backup_{timestamp}.sql.gz"

        command = [
            "pg_dump",
            "-h", db_host,
            "-U", db_user,
            db_name,
        ]

        try:
            with gzip.open(backup_file, "wt") as f:
                subprocess.run(
                    command,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    check=True,
                    env=env,
                    text=True
                )

            self.stdout.write(
                self.style.SUCCESS(f"✅ Backup criado com sucesso: {backup_file}")
            )

        except subprocess.CalledProcessError as e:
            self.stderr.write(
                self.style.ERROR(f"❌ Erro no backup:\n{e.stderr}")
            )
