"""
Serviço de Análise Financeira para Dashboard
"""

from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg, F, Case, When, DecimalField
from decimal import Decimal
from ..models import Booking, Service, Professional


class FinancialAnalytics:
    """Calcula métricas financeiras do dashboard"""
    
    def __init__(self, tenant):
        self.tenant = tenant
        self.timezone = timezone.get_current_timezone()
    
    # ==================== MÉTRICAS BÁSICAS ====================
    
    def get_total_revenue(self, days=None):
        """Receita total (último período)"""
        query = Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed'
        )
        
        if days:
            start_date = timezone.now() - timedelta(days=days)
            query = query.filter(scheduled_for__gte=start_date)
        
        total = query.aggregate(Sum('price'))['price__sum'] or Decimal('0.00')
        return float(total)
    
    def get_annual_revenue(self):
        """Receita anual (últimos 365 dias)"""
        return self.get_total_revenue(days=365)
    
    def get_revenue_today(self):
        """Receita do dia de hoje (00:00 até 23:59 do dia atual)"""
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        revenue = Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed',
            scheduled_for__range=(today_start, today_end)
        ).aggregate(Sum('price'))['price__sum'] or Decimal('0.00')
        
        return float(revenue)
    
    def get_revenue_this_month(self):
        """Receita do mês atual"""
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if now.month == 12:
            month_end = month_start.replace(year=now.year + 1, month=1)
        else:
            month_end = month_start.replace(month=now.month + 1)
        
        revenue = Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed',
            scheduled_for__range=(month_start, month_end)
        ).aggregate(Sum('price'))['price__sum'] or Decimal('0.00')
        
        return float(revenue)
    
    def get_estimated_revenue_this_month(self):
        """Receita estimada do mês (confirmados + pendentes futuros)"""
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if now.month == 12:
            month_end = month_start.replace(year=now.year + 1, month=1)
        else:
            month_end = month_start.replace(month=now.month + 1)
        
        # Somar confirmados e pendentes do mês
        estimated = Booking.objects.filter(
            tenant=self.tenant,
            status__in=['confirmed', 'pending'],  # Confirmados + Pendentes
            scheduled_for__range=(month_start, month_end)
        ).aggregate(Sum('price'))['price__sum'] or Decimal('0.00')
        
        return float(estimated)
    
    def get_revenue_this_week(self):
        """Receita da semana atual"""
        now = timezone.now()
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)
        
        revenue = Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed',
            scheduled_for__range=(week_start, week_end)
        ).aggregate(Sum('price'))['price__sum'] or Decimal('0.00')
        
        return float(revenue)
    
    def get_average_ticket(self, days=30):
        """Ticket médio"""
        start_date = timezone.now() - timedelta(days=days)
        
        avg = Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed',
            scheduled_for__gte=start_date
        ).aggregate(Avg('price'))['price__avg'] or Decimal('0.00')
        
        return float(avg)
    
    # ==================== MÉTRICAS DE AGENDAMENTOS ====================
    
    def get_total_bookings(self):
        """Total de agendamentos"""
        return Booking.objects.filter(tenant=self.tenant).count()
    
    def get_confirmed_bookings(self):
        """Agendamentos confirmados"""
        return Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed'
        ).count()
    
    def get_pending_bookings(self):
        """Agendamentos pendentes"""
        return Booking.objects.filter(
            tenant=self.tenant,
            status='pending'
        ).count()
    
    def get_cancelled_bookings(self):
        """Agendamentos cancelados"""
        return Booking.objects.filter(
            tenant=self.tenant,
            status='cancelled'
        ).count()
    
    def get_conversion_rate(self, days=30):
        """Taxa de conversão (confirmados/total)"""
        start_date = timezone.now() - timedelta(days=days)
        
        total = Booking.objects.filter(
            tenant=self.tenant,
            created_at__gte=start_date
        ).count()
        
        if total == 0:
            return 0.0
        
        confirmed = Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed',
            created_at__gte=start_date
        ).count()
        
        return (confirmed / total) * 100
    
    # ==================== MÉTRICAS POR PROFISSIONAL ====================
    
    def get_revenue_by_professional(self, days=30):
        """Receita por profissional"""
        start_date = timezone.now() - timedelta(days=days)
        
        data = Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed',
            scheduled_for__gte=start_date
        ).values('professional__display_name', 'professional_id').annotate(
            total_revenue=Sum('price'),
            booking_count=Count('id'),
            avg_ticket=Avg('price')
        ).order_by('-total_revenue')
        
        return list(data)
    
    def get_top_professionals(self, limit=5, days=30):
        """Top 5 profissionais por receita"""
        return self.get_revenue_by_professional(days)[:limit]
    
    # ==================== MÉTRICAS POR SERVIÇO ====================
    
    def get_revenue_by_service(self, days=30):
        """Receita por serviço"""
        start_date = timezone.now() - timedelta(days=days)
        
        data = Booking.objects.filter(
            tenant=self.tenant,
            status='confirmed',
            scheduled_for__gte=start_date
        ).values('service__name', 'service_id').annotate(
            total_revenue=Sum('price'),
            booking_count=Count('id'),
            avg_ticket=Avg('price')
        ).order_by('-total_revenue')
        
        return list(data)
    
    def get_top_services(self, limit=5, days=30):
        """Top 5 serviços por receita"""
        return self.get_revenue_by_service(days)[:limit]
    
    # ==================== DADOS PARA GRÁFICOS ====================
    
    def get_revenue_last_7_days(self):
        """Receita dos últimos 7 dias (para gráfico)"""
        data = []
        
        for i in range(6, -1, -1):
            date = timezone.now() - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)
            
            revenue = Booking.objects.filter(
                tenant=self.tenant,
                status='confirmed',
                scheduled_for__range=(date_start, date_end)
            ).aggregate(Sum('price'))['price__sum'] or Decimal('0.00')
            
            data.append({
                'date': date.strftime('%d/%m'),
                'revenue': float(revenue)
            })
        
        return data
    
    def get_revenue_last_12_months(self):
        """Receita dos últimos 12 meses (para gráfico)"""
        data = []
        now = timezone.now()
        
        for i in range(11, -1, -1):
            month_date = now - timedelta(days=30*i)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            if month_date.month == 12:
                month_end = month_start.replace(year=month_date.year + 1, month=1)
            else:
                month_end = month_start.replace(month=month_date.month + 1)
            
            revenue = Booking.objects.filter(
                tenant=self.tenant,
                status='confirmed',
                scheduled_for__range=(month_start, month_end)
            ).aggregate(Sum('price'))['price__sum'] or Decimal('0.00')
            
            data.append({
                'month': month_start.strftime('%b/%y'),
                'revenue': float(revenue)
            })
        
        return data
    
    # ==================== RESUMO COMPLETO ====================
    
    def get_dashboard_summary(self, days=30):
        """Resumo completo para o dashboard"""
        return {
            # Métricas Financeiras
            'annual_revenue': self.get_annual_revenue(),
            'revenue_today': self.get_revenue_today(),
            'revenue_this_week': self.get_revenue_this_week(),
            'revenue_this_month': self.get_revenue_this_month(),
            'estimated_revenue_this_month': self.get_estimated_revenue_this_month(),
            'average_ticket': self.get_average_ticket(days),
            
            # Agendamentos
            'total_bookings': self.get_total_bookings(),
            'confirmed_bookings': self.get_confirmed_bookings(),
            'pending_bookings': self.get_pending_bookings(),
            'cancelled_bookings': self.get_cancelled_bookings(),
            'conversion_rate': self.get_conversion_rate(days),
            
            # Top informações
            'top_professionals': self.get_top_professionals(5, days),
            'top_services': self.get_top_services(5, days),
            
            # Gráficos
            'revenue_last_7_days': self.get_revenue_last_7_days(),
            'revenue_last_12_months': self.get_revenue_last_12_months(),
        }
