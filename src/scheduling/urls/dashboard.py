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
    path("profissionais/", dashboard_views.professional_list, name="professional_list"),
    path("profissionais/<int:pk>/horarios/", dashboard_views.professional_schedule, name="professional_schedule"),
    path("meus-horarios/", dashboard_views.my_schedule, name="my_schedule"),
    path("equipe/", dashboard_views.team_list, name="team_list"),
    path("equipe/<int:pk>/atualizar/", dashboard_views.team_update, name="team_update"),
    path("equipe/<int:pk>/remover/", dashboard_views.team_remove, name="team_remove"),
]
