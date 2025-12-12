"""
Serviço de Análise Operacional para Dashboard
"""

from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg, F, Case, When, DecimalField
from decimal import Decimal
from ..models import Booking, Service, Professional


class OperationalAnalytics:
    """Calcula métricas operacionais do dashboard"""
    
    def __init__(self, tenant):
        self.tenant = tenant
        self.timezone = timezone.get_current_timezone()
    
    # ==================== MÉTRICAS BÁSICAS ====================
    
    def get_total_bookings(self, days=30):
        """Total de agendamentos no período"""
        start_date = timezone.now() - timedelta(days=days)
        return Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__gte=start_date
        ).count()
    
    def get_confirmed_bookings(self, days=30):
        """Agendamentos confirmados"""
        start_date = timezone.now() - timedelta(days=days)
        return Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed',
            scheduled_for__gte=start_date
        ).count()
    
    def get_pending_bookings(self, days=30):
        """Agendamentos pendentes"""
        start_date = timezone.now() - timedelta(days=days)
        return Booking.objects.filter(
            tenant=self.tenant,
            status='pending',
            scheduled_for__gte=start_date
        ).count()
    
    def get_cancelled_bookings(self, days=30):
        """Agendamentos cancelados"""
        start_date = timezone.now() - timedelta(days=days)
        return Booking.objects.filter(
            tenant=self.tenant,
            status='cancelled',
            scheduled_for__gte=start_date
        ).count()
    
    def get_rescheduled_bookings(self, days=30):
        """Agendamentos remarcados (que têm notas com 'Reagendado')"""
        start_date = timezone.now() - timedelta(days=days)
        return Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__gte=start_date,
            notes__icontains='Reagendado'
        ).count()
    
    def get_completed_bookings(self, days=30):
        """Agendamentos concluídos (passados e confirmados)"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        return Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed',
            scheduled_for__range=(start_date, end_date)
        ).count()
    
    def get_no_show_bookings(self, days=30):
        """Agendamentos não comparecidos (no-show)"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        return Booking.objects.filter(
            tenant=self.tenant,
            status='no_show',
            scheduled_for__range=(start_date, end_date)
        ).count()
    
    def get_today_bookings(self):
        """Agendamentos de hoje"""
        today = timezone.now()
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        return Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__range=(today_start, today_end)
        ).count()
    
    def get_today_confirmed(self):
        """Confirmados para hoje"""
        today = timezone.now()
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        return Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed',
            scheduled_for__range=(today_start, today_end)
        ).count()
    
    def get_today_pending(self):
        """Pendentes para hoje"""
        today = timezone.now()
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        return Booking.objects.filter(
            tenant=self.tenant,
            status='pending',
            scheduled_for__range=(today_start, today_end)
        ).count()
    
    def get_cancellation_rate(self, days=30):
        """Taxa de cancelamento (%)"""
        start_date = timezone.now() - timedelta(days=days)
        total = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__gte=start_date
        ).count()
        
        if total == 0:
            return 0.0
        
        cancelled = Booking.objects.filter(
            tenant=self.tenant,
            status='cancelled',
            scheduled_for__gte=start_date
        ).count()
        
        return (cancelled / total) * 100
    
    def get_conversion_rate(self, days=30):
        """Taxa de conversão (%) - percentual de agendamentos confirmados em relação ao total"""
        start_date = timezone.now() - timedelta(days=days)
        total = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__gte=start_date
        ).count()
        
        if total == 0:
            return 0.0
        
        confirmed = Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed',
            scheduled_for__gte=start_date
        ).count()
        
        return (confirmed / total) * 100
    
    def get_no_show_rate(self, days=30):
        """Taxa de no-show (%)"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        total = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__range=(start_date, end_date)
        ).count()
        
        if total == 0:
            return 0.0
        
        no_show = Booking.objects.filter(
            tenant=self.tenant,
            status='no_show',
            scheduled_for__range=(start_date, end_date)
        ).count()
        
        return (no_show / total) * 100
    
    def get_average_bookings_per_day(self, days=30):
        """Média de agendamentos por dia com agendamentos"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        bookings = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__range=(start_date, end_date)
        )
        
        total = bookings.count()
        
        if total == 0:
            return 0.0
        
        # Calcular número de dias distintos com agendamentos
        from django.db.models.functions import TruncDate
        days_with_bookings = bookings.annotate(
            booking_date=TruncDate('scheduled_for')
        ).values('booking_date').distinct().count()
        
        # Se não houver dias, usar 1 para evitar divisão por zero
        days_with_bookings = max(days_with_bookings, 1)
        
        return round(total / days_with_bookings, 2)
    
    def get_average_bookings_per_professional(self, days=30):
        """Média de agendamentos por profissional"""
        start_date = timezone.now() - timedelta(days=days)
        professionals_count = Professional.objects.filter(tenant=self.tenant, is_active=True).count()
        
        if professionals_count == 0:
            return 0.0
        
        total_bookings = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__gte=start_date
        ).count()
        
        return round(total_bookings / professionals_count, 2)
    
    def get_average_bookings_per_professional_by_range(self, start_date, end_date):
        """Média de agendamentos por profissional - período customizado"""
        professionals_count = Professional.objects.filter(tenant=self.tenant, is_active=True).count()
        
        if professionals_count == 0:
            return 0.0
        
        total_bookings = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__range=(start_date, end_date)
        ).count()
        
        return round(total_bookings / professionals_count, 2)
    
    def get_peak_hours(self, days=30):
        """Horas de pico (mais agendamentos) - últimos X dias"""
        start_date = timezone.now() - timedelta(days=days)
        
        bookings = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__gte=start_date
        ).values('scheduled_for__hour').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        total_bookings = self.get_total_bookings(days=days)
        
        return [
            {
                'hour': f"{b['scheduled_for__hour']:02d}:00",
                'count': b['count'],
                'percentage': (b['count'] / total_bookings * 100) if total_bookings > 0 else 0
            }
            for b in bookings
        ]
    
    def get_peak_hours_by_range(self, start_date, end_date):
        """Horas de pico (mais agendamentos) - período customizado"""
        bookings = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__range=(start_date, end_date)
        ).values('scheduled_for__hour').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        total_bookings = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__range=(start_date, end_date)
        ).count()
        
        return [
            {
                'hour': f"{b['scheduled_for__hour']:02d}:00",
                'count': b['count'],
                'percentage': (b['count'] / total_bookings * 100) if total_bookings > 0 else 0
            }
            for b in bookings
        ]
    
    def get_peak_days(self, days=30):
        """Dias da semana com mais agendamentos"""
        start_date = timezone.now() - timedelta(days=days)
        
        WEEKDAY_NAMES = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']
        
        bookings = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__gte=start_date
        ).values('scheduled_for__week_day').annotate(
            count=Count('id')
        ).order_by('scheduled_for__week_day')
        
        total_bookings = self.get_total_bookings(days=days)
        
        return [
            {
                'day': WEEKDAY_NAMES[b['scheduled_for__week_day'] - 1] if b['scheduled_for__week_day'] <= 7 else 'Dom',
                'count': b['count'],
                'percentage': (b['count'] / total_bookings * 100) if total_bookings > 0 else 0
            }
            for b in bookings
        ]
    
    def get_peak_days_by_range(self, start_date, end_date):
        """Dias da semana com mais agendamentos - período customizado"""
        WEEKDAY_NAMES = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']
        
        bookings = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__range=(start_date, end_date)
        ).values('scheduled_for__week_day').annotate(
            count=Count('id')
        ).order_by('scheduled_for__week_day')
        
        total_bookings = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__range=(start_date, end_date)
        ).count()
        
        return [
            {
                'day': WEEKDAY_NAMES[b['scheduled_for__week_day'] - 1] if b['scheduled_for__week_day'] <= 7 else 'Dom',
                'count': b['count'],
                'percentage': (b['count'] / total_bookings * 100) if total_bookings > 0 else 0
            }
            for b in bookings
        ]
    
    def get_bookings_by_status_last_7_days(self):
        """Agendamentos por status nos últimos 7 dias"""
        data = []
        
        for i in range(6, -1, -1):
            date = timezone.now() - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)
            
            confirmed = Booking.objects.filter(
                tenant=self.tenant,
                status='confirmed',
                scheduled_for__range=(date_start, date_end)
            ).count()
            
            pending = Booking.objects.filter(
                tenant=self.tenant,
                status='pending',
                scheduled_for__range=(date_start, date_end)
            ).count()
            
            cancelled = Booking.objects.filter(
                tenant=self.tenant,
                status='cancelled',
                scheduled_for__range=(date_start, date_end)
            ).count()
            
            data.append({
                'date': date.strftime('%d/%m'),
                'confirmed': confirmed,
                'pending': pending,
                'cancelled': cancelled,
                'total': confirmed + pending + cancelled
            })
        
        return data
    
    def get_bookings_by_professional(self, days=30, limit=10):
        """Ranking de profissionais por agendamentos"""
        start_date = timezone.now() - timedelta(days=days)
        
        professionals = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__gte=start_date
        ).values('professional__display_name').annotate(
            total=Count('id'),
            confirmed=Count('id', filter=Q(status='confirmed')),
            cancelled=Count('id', filter=Q(status='cancelled')),
            pending=Count('id', filter=Q(status='pending'))
        ).order_by('-total')[:limit]
        
        return list(professionals)
    
    def get_bookings_by_service(self, days=30, limit=10):
        """Ranking de serviços por agendamentos"""
        start_date = timezone.now() - timedelta(days=days)
        
        services = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__gte=start_date
        ).values('service__name').annotate(
            total=Count('id'),
            confirmed=Count('id', filter=Q(status='confirmed')),
            cancelled=Count('id', filter=Q(status='cancelled')),
            pending=Count('id', filter=Q(status='pending'))
        ).order_by('-total')[:limit]
        
        return list(services)
    
    def get_dashboard_summary(self, days=30):
        """Resumo completo para o dashboard operacional"""
        return {
            # Totais
            'total_bookings': self.get_total_bookings(days),
            'confirmed_bookings': self.get_confirmed_bookings(days),
            'pending_bookings': self.get_pending_bookings(days),
            'cancelled_bookings': self.get_cancelled_bookings(days),
            'rescheduled_bookings': self.get_rescheduled_bookings(days),
            'completed_bookings': self.get_completed_bookings(days),
            'no_show_bookings': self.get_no_show_bookings(days),
            
            # Hoje
            'today_bookings': self.get_today_bookings(),
            'today_confirmed': self.get_today_confirmed(),
            'today_pending': self.get_today_pending(),
            
            # Taxas e médias
            'conversion_rate': self.get_conversion_rate(days),
            'cancellation_rate': self.get_cancellation_rate(days),
            'no_show_rate': self.get_no_show_rate(days),
            'average_bookings_per_day': self.get_average_bookings_per_day(days),
            'average_bookings_per_professional': self.get_average_bookings_per_professional(days),
            
            # Picos
            'peak_hours': self.get_peak_hours(days),
            'peak_days': self.get_peak_days(days),
            
            # Gráficos
            'bookings_by_status_last_7_days': self.get_bookings_by_status_last_7_days(),
            
            # Rankings
            'top_professionals': self.get_bookings_by_professional(days, 5),
            'top_services': self.get_bookings_by_service(days, 5),
        }
    
    def get_occupation_rate_by_range(self, start_date, end_date):
        """Taxa de ocupação (%) - percentual do tempo disponível ocupado baseado em horários reais dos profissionais"""
        from django.db.models.functions import TruncDate
        from datetime import date, time
        from ..models import AvailabilityRule
        
        # Buscar agendamentos confirmados no período
        bookings = Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed',
            scheduled_for__range=(start_date, end_date)
        )
        
        if not bookings.exists():
            return 0.0
        
        # Somar duração total de todos os agendamentos confirmados
        total_duration_minutes = bookings.aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
        
        # Buscar todos os profissionais com agendamentos no período
        professionals_with_bookings = bookings.values_list('professional', flat=True).distinct()
        
        # Calcular total de minutos disponíveis por profissional
        total_available_minutes = 0
        
        # Iterar por cada dia do período
        current_date = start_date
        while current_date <= end_date:
            weekday = current_date.weekday()  # 0=segunda, 6=domingo
            
            # Apenas contar dias úteis (segunda a sábado)
            if weekday < 6:
                # Para cada profissional com agendamentos
                for professional_id in professionals_with_bookings:
                    try:
                        professional = Professional.objects.get(id=professional_id, tenant=self.tenant)
                    except Professional.DoesNotExist:
                        continue
                    
                    # Buscar regra de disponibilidade para este dia e profissional
                    availability = AvailabilityRule.objects.filter(
                        tenant=self.tenant,
                        professional=professional,
                        weekday=weekday,
                        is_active=True
                    ).first()
                    
                    if not availability:
                        # Se não houver regra específica, buscar padrão da empresa
                        availability = AvailabilityRule.objects.filter(
                            tenant=self.tenant,
                            professional__isnull=True,
                            weekday=weekday,
                            is_active=True
                        ).first()
                    
                    if availability:
                        # Calcular minutos disponíveis (hora fim - hora início - pausas)
                        start = availability.start_time
                        end = availability.end_time
                        
                        # Converter para minutos
                        start_minutes = start.hour * 60 + start.minute
                        end_minutes = end.hour * 60 + end.minute
                        
                        day_available = end_minutes - start_minutes
                        
                        # Subtrair pausas se houver
                        if availability.break_start and availability.break_end:
                            break_start_minutes = availability.break_start.hour * 60 + availability.break_start.minute
                            break_end_minutes = availability.break_end.hour * 60 + availability.break_end.minute
                            day_available -= (break_end_minutes - break_start_minutes)
                        
                        total_available_minutes += day_available
            
            current_date += timedelta(days=1)
        
        # Calcular percentual
        if total_available_minutes > 0:
            occupation_rate = (total_duration_minutes / total_available_minutes) * 100
            return round(min(occupation_rate, 100), 1)
        
        return 0.0
    
    def get_summary_by_date_range(self, start_date, end_date):
        """Resumo para período customizado"""
        bookings = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__range=(start_date, end_date)
        )
        
        confirmed = bookings.filter(status='confirmed').count()
        pending = bookings.filter(status='pending').count()
        cancelled = bookings.filter(status='cancelled').count()
        rescheduled = bookings.filter(notes__icontains='Reagendado').count()
        total = bookings.count()
        
        # Calcular número de dias distintos com agendamentos
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        days_with_bookings = bookings.annotate(
            booking_date=TruncDate('scheduled_for')
        ).values('booking_date').distinct().count()
        
        # Se não houver agendamentos, usar 1 para evitar divisão por zero
        days_with_bookings = max(days_with_bookings, 1) if total > 0 else 1
        
        # Calcular média por dia com agendamentos
        average_per_day = round(total / days_with_bookings, 2) if total > 0 else 0.0
        
        return {
            'total_bookings': total,
            'confirmed_bookings': confirmed,
            'pending_bookings': pending,
            'cancelled_bookings': cancelled,
            'rescheduled_bookings': rescheduled,
            'completed_bookings': confirmed,
            'no_show_bookings': bookings.filter(status='no_show').count(),
            
            'today_bookings': 0,
            'today_confirmed': 0,
            'today_pending': 0,
            
            'cancellation_rate': (cancelled / total * 100) if total > 0 else 0.0,
            'conversion_rate': (confirmed / total * 100) if total > 0 else 0.0,
            'no_show_rate': (bookings.filter(status='no_show').count() / total * 100) if total > 0 else 0.0,
            'average_bookings_per_day': average_per_day,
            'average_bookings_per_professional': self.get_average_bookings_per_professional_by_range(start_date, end_date),
            'occupation_rate': self.get_occupation_rate_by_range(start_date, end_date),
            
            'peak_hours': self.get_peak_hours_by_range(start_date, end_date),
            'peak_days': self.get_peak_days_by_range(start_date, end_date),
            'bookings_by_status_last_7_days': self.get_bookings_by_status_last_7_days(),
            'top_professionals': self.get_bookings_by_professional(30, 5),
            'top_services': self.get_bookings_by_service(30, 5),
        }
