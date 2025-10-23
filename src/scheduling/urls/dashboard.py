from django.urls import path

from scheduling.views import dashboard as dashboard_views

app_name = "dashboard"

urlpatterns = [
    path("", dashboard_views.index, name="index"),
    path("agenda/", dashboard_views.calendar_view, name="calendar"),
    path("agendamentos/<int:pk>/", dashboard_views.booking_detail, name="booking_detail"),
    path("agendamentos/novo/", dashboard_views.booking_create, name="booking_create"),
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
]
