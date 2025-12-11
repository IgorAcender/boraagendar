from django.urls import path

from scheduling.views import dashboard as dashboard_views

app_name = "dashboard"

urlpatterns = [
    path("", dashboard_views.index, name="index"),
    path("relatorio-pdf/", dashboard_views.export_report_pdf, name="export_report_pdf"),
    path("agenda/", dashboard_views.calendar_view, name="calendar"),
    path("agenda/dia/", dashboard_views.calendar_day_view, name="calendar_day"),
    path("agendamentos/<int:pk>/", dashboard_views.booking_detail, name="booking_detail"),
    path("agendamentos/<int:pk>/status/", dashboard_views.booking_update_status, name="booking_update_status"),
    path("agendamentos/passados/", dashboard_views.booking_past_list, name="booking_past_list"),
    path("agendamentos/novo/", dashboard_views.booking_create, name="booking_create"),
    path("agendamentos/dados-profissionais/", dashboard_views.get_professionals_data, name="get_professionals_data"),
    path("agendamentos/profissionais-por-servico/", dashboard_views.get_professionals_by_service, name="get_professionals_by_service"),
    path("agendamentos/horarios-disponiveis/", dashboard_views.get_available_times, name="get_available_times"),
    path("agendamentos/<int:pk>/mover/", dashboard_views.booking_move, name="booking_move"),
    path("servicos/", dashboard_views.service_list, name="service_list"),
    path("servicos/<int:pk>/editar/", dashboard_views.service_update, name="service_update"),
    path("profissionais/", dashboard_views.professional_list, name="professional_list"),
    path("profissionais/<int:pk>/editar/", dashboard_views.professional_update, name="professional_update"),
    path("profissionais/<int:pk>/horarios/", dashboard_views.professional_schedule, name="professional_schedule"),
    path("profissionais/<int:pk>/servicos/", dashboard_views.professional_services, name="professional_services"),
    path("meus-horarios/", dashboard_views.my_schedule, name="my_schedule"),
    path("meus-servicos/", dashboard_views.my_services, name="my_services"),
    path("equipe/", dashboard_views.team_list, name="team_list"),
    path("equipe/<int:pk>/atualizar/", dashboard_views.team_update, name="team_update"),
    path("equipe/<int:pk>/remover/", dashboard_views.team_remove, name="team_remove"),
    path("configuracoes/", dashboard_views.tenant_settings, name="tenant_settings"),
    path("configuracoes/marca/", dashboard_views.branding_settings, name="branding_settings"),
    path("configuracoes/politicas/", dashboard_views.booking_policies, name="booking_policies"),
    path("horario-padrao/", dashboard_views.default_availability_view, name="default_availability"),
    path("horario-padrao/salvar/", dashboard_views.default_availability_save, name="default_availability_save"),
]
