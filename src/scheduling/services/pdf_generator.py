"""
Serviço de Geração de Relatórios PDF
"""

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.utils import timezone


class PDFReportGenerator:
    """Gera relatórios em PDF com dados financeiros"""
    
    def __init__(self, tenant, financial_data):
        self.tenant = tenant
        self.financial_data = financial_data
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados"""
        # Título
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Subtítulo
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        
        # Seção
        self.section_style = ParagraphStyle(
            'Section',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        # Normal
        self.normal_style = ParagraphStyle(
            'Normal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748b'),
        )
    
    def generate(self, period_label="30 Últimos Dias"):
        """Gerar o PDF completo"""
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Elementos do documento
        elements = []
        
        # Cabeçalho
        elements.extend(self._build_header(period_label))
        elements.append(Spacer(1, 0.3*inch))
        
        # KPIs Principais
        elements.extend(self._build_kpis())
        elements.append(Spacer(1, 0.3*inch))
        
        # Métricas de Agendamento
        elements.extend(self._build_booking_metrics())
        elements.append(Spacer(1, 0.3*inch))
        
        # Top Profissionais
        elements.extend(self._build_top_professionals())
        elements.append(Spacer(1, 0.3*inch))
        
        # Top Serviços
        elements.extend(self._build_top_services())
        elements.append(Spacer(1, 0.3*inch))
        
        # Rodapé
        elements.append(Spacer(1, 0.2*inch))
        elements.extend(self._build_footer())
        
        # Criar PDF
        doc.build(elements)
        self.buffer.seek(0)
        return self.buffer
    
    def _build_header(self, period_label):
        """Construir cabeçalho do relatório"""
        elements = []
        
        # Título
        elements.append(Paragraph("📊 Relatório Financeiro", self.title_style))
        elements.append(Paragraph(self.tenant.name, self.subtitle_style))
        
        # Data do relatório
        now = timezone.now().strftime("%d de %B de %Y às %H:%M")
        elements.append(Paragraph(f"Período: {period_label}", self.normal_style))
        elements.append(Paragraph(f"Gerado em: {now}", self.normal_style))
        
        return elements
    
    def _build_kpis(self):
        """Construir seção de KPIs principais"""
        elements = []
        elements.append(Paragraph("📈 KPIs Principais", self.section_style))
        
        # Dados de KPI
        kpi_data = [
            ['Métrica', 'Valor'],
            ['Receita Anual', f"R$ {self.financial_data.get('annual_revenue', 0):.2f}"],
            ['Receita Hoje', f"R$ {self.financial_data.get('revenue_today', 0):.2f}"],
            ['Receita Este Mês', f"R$ {self.financial_data.get('revenue_this_month', 0):.2f}"],
            ['Ticket Médio', f"R$ {self.financial_data.get('average_ticket', 0):.2f}"],
            ['Estimativa Mês', f"R$ {self.financial_data.get('estimated_revenue_this_month', 0):.2f}"],
        ]
        
        # Tabela
        table = Table(kpi_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        
        elements.append(table)
        return elements
    
    def _build_booking_metrics(self):
        """Construir seção de métricas de agendamento"""
        elements = []
        elements.append(Paragraph("📅 Métricas de Agendamento", self.section_style))
        
        # Dados de agendamento
        booking_data = [
            ['Status', 'Quantidade', 'Percentual'],
            ['Total', str(self.financial_data.get('total_bookings', 0)), '100%'],
            ['Confirmados', str(self.financial_data.get('confirmed_bookings', 0)), 
             f"{(self.financial_data.get('confirmed_bookings', 0) / max(self.financial_data.get('total_bookings', 1), 1) * 100):.1f}%"],
            ['Pendentes', str(self.financial_data.get('pending_bookings', 0)),
             f"{(self.financial_data.get('pending_bookings', 0) / max(self.financial_data.get('total_bookings', 1), 1) * 100):.1f}%"],
            ['Cancelados', str(self.financial_data.get('cancelled_bookings', 0)),
             f"{(self.financial_data.get('cancelled_bookings', 0) / max(self.financial_data.get('total_bookings', 1), 1) * 100):.1f}%"],
            ['Taxa de Conversão', f"{self.financial_data.get('conversion_rate', 0):.1f}%", ''],
        ]
        
        # Tabela
        table = Table(booking_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        
        elements.append(table)
        return elements
    
    def _build_top_professionals(self):
        """Construir seção de top profissionais"""
        elements = []
        elements.append(Paragraph("👥 Top 5 Profissionais (por Receita)", self.section_style))
        
        professionals = self.financial_data.get('top_professionals', [])
        
        if professionals:
            prof_data = [['Profissional', 'Agendamentos', 'Receita', 'Ticket Médio']]
            
            for prof in professionals[:5]:
                prof_data.append([
                    prof.get('professional__display_name', 'N/A'),
                    str(prof.get('booking_count', 0)),
                    f"R$ {prof.get('total_revenue', 0):.2f}",
                    f"R$ {prof.get('avg_ticket', 0):.2f}",
                ])
            
            # Tabela
            table = Table(prof_data, colWidths=[2*inch, 1.2*inch, 1.3*inch, 1.3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ]))
            
            elements.append(table)
        else:
            elements.append(Paragraph("Nenhum dado disponível", self.normal_style))
        
        return elements
    
    def _build_top_services(self):
        """Construir seção de top serviços"""
        elements = []
        elements.append(Paragraph("🎯 Top 5 Serviços (por Receita)", self.section_style))
        
        services = self.financial_data.get('top_services', [])
        
        if services:
            svc_data = [['Serviço', 'Agendamentos', 'Receita', 'Ticket Médio']]
            
            for svc in services[:5]:
                svc_data.append([
                    svc.get('service__name', 'N/A'),
                    str(svc.get('booking_count', 0)),
                    f"R$ {svc.get('total_revenue', 0):.2f}",
                    f"R$ {svc.get('avg_ticket', 0):.2f}",
                ])
            
            # Tabela
            table = Table(svc_data, colWidths=[2*inch, 1.2*inch, 1.3*inch, 1.3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ]))
            
            elements.append(table)
        else:
            elements.append(Paragraph("Nenhum dado disponível", self.normal_style))
        
        return elements
    
    def _build_footer(self):
        """Construir rodapé do relatório"""
        elements = []
        
        # Linha separadora
        elements.append(Paragraph("_" * 80, self.normal_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Texto do rodapé
        footer_text = f"Relatório gerado automaticamente pelo BorAgendar | {self.tenant.name} | {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        elements.append(Paragraph(footer_text, self.normal_style))
        
        return elements
