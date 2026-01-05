from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import Notification
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Processa notificações repetitivas e atualiza o mesmo objeto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa o comando sem processar notificações, apenas mostra o que seria feito',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Modo DRY-RUN: Nenhuma notificação será processada')
            )
        
        now = timezone.now()
        notifications = Notification.objects.filter(repeat=True, is_read=True, date__lte=now)
        
        self.stdout.write(f'🔍 Encontradas {notifications.count()} notificações para processar')
        
        processed_count = 0
        
        for notification in notifications:
            try:
                self.stdout.write(f'📋 Processando: {notification.title} (ID: {notification.id})')
                self.stdout.write(f'   Data atual: {notification.date.strftime("%d/%m/%Y %H:%M")}')
                self.stdout.write(f'   Frequência: {notification.get_repeat_frequency_display()}')
                
                if not dry_run:
                    
                    # Reagendar próxima execução
                    notification.schedule_next()
                    
                    self.stdout.write(
                        f'✅ Notificação processada e reagendada para: {notification.date.strftime("%d/%m/%Y %H:%M")}'
                    )
                else:
                    self.stdout.write(
                        f'[DRY-RUN] Processaria notificação: {notification.title}'
                    )
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f'Erro ao processar notificação {notification.id}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Erro ao processar notificação {notification.id}: {str(e)}'
                    )
                )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'[DRY-RUN] Total de notificações que seriam processadas: {processed_count}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Total de notificações processadas: {processed_count}')
            )
