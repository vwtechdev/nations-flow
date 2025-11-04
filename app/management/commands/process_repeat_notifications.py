from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from app.models import Notification, User
import logging
import calendar

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
        
        self.stdout.write(f'🔍 Encontradas {notifications_to_repeat.count()} notificações para processar')
        
        created_count = 0
        
        for notification in notifications_to_repeat:
            try:
                self.stdout.write(f'📋 Processando: {notification.title} (ID: {notification.id})')
                self.stdout.write(f'   Data original: {notification.date.strftime("%d/%m/%Y %H:%M")}')
                self.stdout.write(f'   Próxima data atual: {notification.next_repeat_date.strftime("%d/%m/%Y %H:%M") if notification.next_repeat_date else "Não definida"}')
                self.stdout.write(f'   Frequência: {notification.repeat_frequency}')
                
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
                        notification.next_repeat_date = self.calculate_next_repeat_date(new_date, notification.repeat_frequency)
                        notification.save(update_fields=['next_repeat_date'])
                        
                        self.stdout.write(
                            f'✅ Criada notificação repetitiva: {new_notification.title} '
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
                            f'⚠️ Não foi possível calcular próxima data para: {notification.title}'
                        )
                    )
                    
            except Exception as e:
                logger.error(f'Erro ao processar notificação {notification.id}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Erro ao processar notificação {notification.id}: {str(e)}'
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
                next_date = self.calculate_next_repeat_date(notification.date, notification.repeat_frequency)
                if next_date:
                    if not dry_run:
                        notification.next_repeat_date = next_date
                        notification.save(update_fields=['next_repeat_date'])
                        self.stdout.write(
                            f'📅 Definida próxima data para: {notification.title} '
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
                self.style.SUCCESS(f'✅ Total de notificações criadas: {created_count}')
            )

    def calculate_next_date(self, notification):
        """Calcula a próxima data baseada na frequência e data original da notificação"""
        # Usar a data original da notificação como base para manter consistência
        base_date = notification.date
        
        if notification.repeat_frequency == 'daily':
            # Diário: somar + 1 dia
            return base_date + timedelta(days=1)
        elif notification.repeat_frequency == 'weekly':
            # Semanal: somar + 7 dias
            return base_date + timedelta(days=7)
        elif notification.repeat_frequency == 'monthly':
            # Mensal: somar + 1 mês
            return self.add_months(base_date, 1)
        elif notification.repeat_frequency == 'annually':
            # Anual: somar + 1 ano
            return self.add_years(base_date, 1)
        
        return None

    def calculate_next_repeat_date(self, base_date, frequency):
        """Calcula a próxima data de repetição baseada na frequência"""
        if frequency == 'daily':
            return base_date + timedelta(days=1)
        elif frequency == 'weekly':
            return base_date + timedelta(days=7)
        elif frequency == 'monthly':
            return self.add_months(base_date, 1)
        elif frequency == 'annually':
            return self.add_years(base_date, 1)
        
        return None

    def add_months(self, date, months):
        """
        Adiciona meses a uma data, considerando casos especiais de fevereiro e anos bissextos.
        
        Regras implementadas:
        - 28/02 + 1 mês = 31/03 (último dia de março)
        - 29/02 + 1 mês = 31/03 (último dia de março)
        - 30/01 + 1 mês = 28/02 (ou 29/02 se ano bissexto)
        - 31/01 + 1 mês = 28/02 (ou 29/02 se ano bissexto)
        """
        year = date.year
        month = date.month
        day = date.day
        
        # Calcular o próximo mês e ano
        month += months
        while month > 12:
            month -= 12
            year += 1
        
        # Verificar se o dia existe no próximo mês
        last_day_of_month = calendar.monthrange(year, month)[1]
        
        # Se o dia original não existe no próximo mês, usar o último dia do mês
        if day > last_day_of_month:
            day = last_day_of_month
        
        try:
            return date.replace(year=year, month=month, day=day)
        except ValueError:
            # Fallback: usar o último dia do mês
            return date.replace(year=year, month=month, day=last_day_of_month)

    def add_years(self, date, years):
        """
        Adiciona anos a uma data, considerando anos bissextos.
        
        Regras implementadas:
        - 29/02/2020 + 1 ano = 28/02/2021 (2021 não é bissexto)
        - 29/02/2020 + 4 anos = 29/02/2024 (2024 é bissexto)
        """
        year = date.year + years
        month = date.month
        day = date.day
        
        # Verificar se o dia existe no próximo ano
        last_day_of_month = calendar.monthrange(year, month)[1]
        
        # Se o dia não existe no próximo ano (ex: 29/02 em ano não bissexto), usar o último dia do mês
        if day > last_day_of_month:
            day = last_day_of_month
        
        try:
            return date.replace(year=year, day=day)
        except ValueError:
            # Fallback: usar o último dia do mês
            return date.replace(year=year, day=last_day_of_month)

    def is_leap_year(self, year):
        """Verifica se um ano é bissexto"""
        return calendar.isleap(year)
