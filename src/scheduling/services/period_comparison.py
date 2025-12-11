"""
Serviço de Comparação de Períodos
"""

from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from ..models import Booking


class PeriodComparison:
    """Compara métricas entre períodos"""
    
    def __init__(self, tenant):
        self.tenant = tenant
        self.timezone = timezone.get_current_timezone()
    
    def get_month_comparison(self, year=None, month=None):
        """
        Comparar mês atual com mês anterior
        Retorna: {
            'current_month': {...},
            'previous_month': {...},
            'comparison': {'revenue': 0.0, 'bookings': 0, 'percentual': 0.0}
        }
        """
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month
        
        # Mês atual
        current_start = timezone.now().replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
        if month == 12:
            current_end = current_start.replace(year=year+1, month=1) - timedelta(microseconds=1)
        else:
            current_end = current_start.replace(month=month+1) - timedelta(microseconds=1)
        
        # Mês anterior
        if month == 1:
            prev_start = current_start.replace(year=year-1, month=12)
            prev_end = prev_start.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            prev_start = current_start.replace(month=month-1)
            if month - 1 in [1, 3, 5, 7, 8, 10, 12]:
                prev_end = prev_start.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
            elif month - 1 in [4, 6, 9, 11]:
                prev_end = prev_start.replace(day=30, hour=23, minute=59, second=59, microsecond=999999)
            else:  # Fevereiro
                if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                    prev_end = prev_start.replace(day=29, hour=23, minute=59, second=59, microsecond=999999)
                else:
                    prev_end = prev_start.replace(day=28, hour=23, minute=59, second=59, microsecond=999999)
        
        # Calcular métricas para cada período
        current_data = self._get_period_metrics(current_start, current_end)
        previous_data = self._get_period_metrics(prev_start, prev_end)
        
        # Calcular comparação
        revenue_diff = current_data['revenue'] - previous_data['revenue']
        bookings_diff = current_data['confirmed_bookings'] - previous_data['confirmed_bookings']
        
        revenue_percentual = 0.0
        if previous_data['revenue'] > 0:
            revenue_percentual = (revenue_diff / previous_data['revenue']) * 100
        
        bookings_percentual = 0.0
        if previous_data['confirmed_bookings'] > 0:
            bookings_percentual = (bookings_diff / previous_data['confirmed_bookings']) * 100
        
        return {
            'current_month': {
                'name': current_start.strftime('%B de %Y').capitalize(),
                'period': f"{current_start.strftime('%d/%m/%Y')} a {current_end.strftime('%d/%m/%Y')}",
                'data': current_data
            },
            'previous_month': {
                'name': prev_start.strftime('%B de %Y').capitalize(),
                'period': f"{prev_start.strftime('%d/%m/%Y')} a {prev_end.strftime('%d/%m/%Y')}",
                'data': previous_data
            },
            'comparison': {
                'revenue': {
                    'absolute': revenue_diff,
                    'percentual': revenue_percentual,
                    'direction': 'up' if revenue_diff > 0 else 'down' if revenue_diff < 0 else 'stable'
                },
                'bookings': {
                    'absolute': bookings_diff,
                    'percentual': bookings_percentual,
                    'direction': 'up' if bookings_diff > 0 else 'down' if bookings_diff < 0 else 'stable'
                }
            }
        }
    
    def get_week_comparison(self):
        """
        Comparar semana atual com semana anterior
        """
        now = timezone.now()
        
        # Semana atual (segunda a domingo)
        current_start = now - timedelta(days=now.weekday())
        current_start = current_start.replace(hour=0, minute=0, second=0, microsecond=0)
        current_end = current_start + timedelta(days=7) - timedelta(microseconds=1)
        
        # Semana anterior
        prev_start = current_start - timedelta(days=7)
        prev_end = current_start - timedelta(microseconds=1)
        
        # Calcular métricas
        current_data = self._get_period_metrics(current_start, current_end)
        previous_data = self._get_period_metrics(prev_start, prev_end)
        
        # Calcular comparação
        revenue_diff = current_data['revenue'] - previous_data['revenue']
        bookings_diff = current_data['confirmed_bookings'] - previous_data['confirmed_bookings']
        
        revenue_percentual = 0.0
        if previous_data['revenue'] > 0:
            revenue_percentual = (revenue_diff / previous_data['revenue']) * 100
        
        bookings_percentual = 0.0
        if previous_data['confirmed_bookings'] > 0:
            bookings_percentual = (bookings_diff / previous_data['confirmed_bookings']) * 100
        
        return {
            'current_week': {
                'name': f"Semana de {current_start.strftime('%d/%m')} a {current_end.strftime('%d/%m/%Y')}",
                'data': current_data
            },
            'previous_week': {
                'name': f"Semana de {prev_start.strftime('%d/%m')} a {prev_end.strftime('%d/%m/%Y')}",
                'data': previous_data
            },
            'comparison': {
                'revenue': {
                    'absolute': revenue_diff,
                    'percentual': revenue_percentual,
                    'direction': 'up' if revenue_diff > 0 else 'down' if revenue_diff < 0 else 'stable'
                },
                'bookings': {
                    'absolute': bookings_diff,
                    'percentual': bookings_percentual,
                    'direction': 'up' if bookings_diff > 0 else 'down' if bookings_diff < 0 else 'stable'
                }
            }
        }
    
    def _get_period_metrics(self, start_date, end_date):
        """Obter métricas para um período"""
        bookings = Booking.objects.filter(
            tenant=self.tenant,
            scheduled_for__range=(start_date, end_date)
        )
        
        confirmed = bookings.filter(status='confirmed')
        pending = bookings.filter(status='pending')
        cancelled = bookings.filter(status='cancelled')
        
        revenue = confirmed.aggregate(Sum('price'))['price__sum'] or Decimal('0.00')
        avg_ticket = confirmed.aggregate(avg_price=Sum('price') / confirmed.count())['avg_price'] if confirmed.count() > 0 else Decimal('0.00')
        
        total_count = bookings.count()
        confirmed_count = confirmed.count()
        pending_count = pending.count()
        cancelled_count = cancelled.count()
        
        conversion_rate = 0.0
        if total_count > 0:
            conversion_rate = (confirmed_count / total_count) * 100
        
        return {
            'revenue': float(revenue),
            'average_ticket': float(avg_ticket) if avg_ticket else 0.0,
            'total_bookings': total_count,
            'confirmed_bookings': confirmed_count,
            'pending_bookings': pending_count,
            'cancelled_bookings': cancelled_count,
            'conversion_rate': conversion_rate,
        }
