"""
Serviço de Cálculo de Metas e Targets
"""

from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg
from decimal import Decimal
from ..models import Booking, Target


class TargetProgressCalculator:
    """Calcula o progresso das metas"""
    
    def __init__(self, tenant):
        self.tenant = tenant
        self.timezone = timezone.get_current_timezone()
    
    def get_all_targets_progress(self):
        """Retorna progresso de todas as metas ativas"""
        targets = Target.objects.filter(tenant=self.tenant, is_active=True)
        
        results = []
        for target in targets:
            progress = self.calculate_target_progress(target)
            results.append(progress)
        
        return results
    
    def calculate_target_progress(self, target):
        """Calcula o progresso de uma meta específica"""
        
        # Obter período
        start_date, end_date = self._get_period_dates(target.period)
        
        # Obter valor atual baseado no tipo
        current_value = self._get_current_value(target.target_type, start_date, end_date)
        
        # Calcular progresso
        target_value = float(target.target_value)
        progress_percentage = 0.0
        if target_value > 0:
            progress_percentage = (current_value / target_value) * 100
        
        # Determinar status
        status = 'on_track'
        if progress_percentage >= 100:
            status = 'completed'
        elif progress_percentage < 50:
            status = 'behind'
        elif progress_percentage < 80:
            status = 'caution'
        
        # Calcular dias restantes
        days_remaining = (end_date - timezone.now()).days
        
        return {
            'target': target,
            'target_id': target.id,
            'period': target.period,
            'period_label': target.get_period_label(),
            'target_type': target.target_type,
            'target_type_label': target.get_target_type_label(),
            'target_value': target_value,
            'current_value': current_value,
            'remaining_value': max(0, target_value - current_value),
            'progress_percentage': min(100, progress_percentage),
            'status': status,
            'days_remaining': max(0, days_remaining),
            'period_start': start_date.strftime('%d/%m/%Y'),
            'period_end': end_date.strftime('%d/%m/%Y'),
            'description': target.description,
        }
    
    def _get_period_dates(self, period):
        """Retorna start_date e end_date baseado no período"""
        now = timezone.now()
        
        if period == 'daily':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1) - timedelta(microseconds=1)
        
        elif period == 'weekly':
            # Semana: segunda a domingo
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7) - timedelta(microseconds=1)
        
        elif period == 'monthly':
            # Mês: 1º ao último dia do mês
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end = start.replace(year=now.year + 1, month=1)
            else:
                end = start.replace(month=now.month + 1)
            end = end - timedelta(microseconds=1)
        
        elif period == 'yearly':
            # Ano: 1º de janeiro ao 31 de dezembro
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        
        else:
            # Default: hoje
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1) - timedelta(microseconds=1)
        
        return start, end
    
    def _get_current_value(self, target_type, start_date, end_date):
        """Obtém o valor atual para o tipo de target"""
        
        bookings = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__range=(start_date, end_date)
        )
        
        if target_type == 'revenue':
            # Receita de agendamentos confirmados
            value = bookings.filter(status='confirmed').aggregate(Sum('price'))['price__sum'] or Decimal('0.00')
            return float(value)
        
        elif target_type == 'bookings':
            # Total de agendamentos confirmados
            return bookings.filter(status='confirmed').count()
        
        elif target_type == 'average_ticket':
            # Ticket médio
            confirmed = bookings.filter(status='confirmed')
            if confirmed.count() > 0:
                avg = confirmed.aggregate(avg_price=Sum('price') / confirmed.count())['avg_price'] or Decimal('0.00')
                return float(avg)
            return 0.0
        
        elif target_type == 'confirmed_rate':
            # Taxa de confirmação (%)
            total = bookings.count()
            if total > 0:
                confirmed = bookings.filter(status='confirmed').count()
                return (confirmed / total) * 100
            return 0.0
        
        return 0.0
    
    def get_summary_stats(self):
        """Retorna estatísticas resumidas das metas"""
        all_targets = self.get_all_targets_progress()
        
        if not all_targets:
            return {
                'total_targets': 0,
                'completed': 0,
                'on_track': 0,
                'caution': 0,
                'behind': 0,
                'overall_progress': 0.0,
            }
        
        total = len(all_targets)
        completed = sum(1 for t in all_targets if t['status'] == 'completed')
        on_track = sum(1 for t in all_targets if t['status'] == 'on_track')
        caution = sum(1 for t in all_targets if t['status'] == 'caution')
        behind = sum(1 for t in all_targets if t['status'] == 'behind')
        
        overall_progress = sum(t['progress_percentage'] for t in all_targets) / total if total > 0 else 0.0
        
        return {
            'total_targets': total,
            'completed': completed,
            'on_track': on_track,
            'caution': caution,
            'behind': behind,
            'overall_progress': overall_progress,
        }
