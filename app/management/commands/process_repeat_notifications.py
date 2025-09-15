from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from app.models import Notification, User
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Processa notificações repetitivas e cria novas notificações baseadas na frequência'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa o comando sem criar notificações, apenas mostra o que seria feito',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Modo DRY-RUN: Nenhuma notificação será criada')
            )
        
        # Buscar notificações que precisam ser repetidas
        now = timezone.now()
        
        # Notificações originais que têm repetição ativa e a próxima data já passou
        notifications_to_repeat = Notification.objects.filter(
            repeat=True,
            repeat_frequency__in=['daily', 'weekly', 'monthly', 'annually'],
            original_notification__isnull=True,  # Apenas notificações originais
            next_repeat_date__lte=now
        ).select_related('created_by')
        
        created_count = 0
        
        for notification in notifications_to_repeat:
            try:
                # Calcular a nova data baseada na frequência
                new_date = self.calculate_next_date(notification)
                
                if new_date:
                    if not dry_run:
                        # Criar nova notificação
                        new_notification = Notification.objects.create(
                            title=notification.title,
                            body=notification.body,
                            date=new_date,
                            is_read=False,
                            repeat=notification.repeat,
                            repeat_frequency=notification.repeat_frequency,
                            original_notification=notification,
                            created_by=notification.created_by
                        )
                        
                        # Atualizar a próxima data de repetição da notificação original
                        notification.next_repeat_date = new_notification.calculate_next_repeat_date()
                        notification.save(update_fields=['next_repeat_date'])
                        
                        self.stdout.write(
                            f'Criada notificação repetitiva: {new_notification.title} '
                            f'para {new_date.strftime("%d/%m/%Y %H:%M")}'
                        )
                    else:
                        self.stdout.write(
                            f'[DRY-RUN] Criaria notificação: {notification.title} '
                            f'para {new_date.strftime("%d/%m/%Y %H:%M")}'
                        )
                    
                    created_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Não foi possível calcular próxima data para: {notification.title}'
                        )
                    )
                    
            except Exception as e:
                logger.error(f'Erro ao processar notificação {notification.id}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(
                        f'Erro ao processar notificação {notification.id}: {str(e)}'
                    )
                )
        
        # Processar notificações que não têm next_repeat_date definida
        notifications_without_next_date = Notification.objects.filter(
            repeat=True,
            repeat_frequency__in=['daily', 'weekly', 'monthly', 'annually'],
            original_notification__isnull=True,
            next_repeat_date__isnull=True
        )
        
        for notification in notifications_without_next_date:
            try:
                next_date = notification.calculate_next_repeat_date()
                if next_date:
                    if not dry_run:
                        notification.next_repeat_date = next_date
                        notification.save(update_fields=['next_repeat_date'])
                        self.stdout.write(
                            f'Definida próxima data para: {notification.title} '
                            f'-> {next_date.strftime("%d/%m/%Y %H:%M")}'
                        )
                    else:
                        self.stdout.write(
                            f'[DRY-RUN] Definiria próxima data para: {notification.title} '
                            f'-> {next_date.strftime("%d/%m/%Y %H:%M")}'
                        )
            except Exception as e:
                logger.error(f'Erro ao definir próxima data para notificação {notification.id}: {str(e)}')
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'[DRY-RUN] Total de notificações que seriam criadas: {created_count}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Total de notificações criadas: {created_count}')
            )

    def calculate_next_date(self, notification):
        """Calcula a próxima data baseada na frequência e data atual"""
        if notification.repeat_frequency == 'daily':
            return notification.next_repeat_date + timedelta(days=1)
        elif notification.repeat_frequency == 'weekly':
            return notification.next_repeat_date + timedelta(weeks=1)
        elif notification.repeat_frequency == 'monthly':
            # Para mensal, adicionar 1 mês mantendo o mesmo dia e hora
            current_month = notification.next_repeat_date.month
            current_year = notification.next_repeat_date.year
            
            # Calcular próximo mês e ano
            if current_month == 12:
                next_month = 1
                next_year = current_year + 1
            else:
                next_month = current_month + 1
                next_year = current_year
            
            # Verificar se o dia existe no próximo mês
            import calendar
            last_day_of_next_month = calendar.monthrange(next_year, next_month)[1]
            day = min(notification.next_repeat_date.day, last_day_of_next_month)
            
            try:
                return notification.next_repeat_date.replace(year=next_year, month=next_month, day=day)
            except ValueError:
                # Se ainda houver erro, usar o último dia do mês
                return notification.next_repeat_date.replace(year=next_year, month=next_month, day=last_day_of_next_month)
        elif notification.repeat_frequency == 'annually':
            # Para anual, adicionar 1 ano mantendo o mesmo dia e hora
            next_year = notification.next_repeat_date.year + 1
            try:
                return notification.next_repeat_date.replace(year=next_year)
            except ValueError:
                # Se o dia não existe no próximo ano (ex: 29/02), usar o último dia do mês
                import calendar
                last_day = calendar.monthrange(next_year, notification.next_repeat_date.month)[1]
                day = min(notification.next_repeat_date.day, last_day)
                return notification.next_repeat_date.replace(year=next_year, day=day)
        
        return None
