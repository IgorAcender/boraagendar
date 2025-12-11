"""
Template tags para checagem de features e exibição de bloqueios
"""
from django import template
from tenants.subscription_helpers import get_user_subscription, has_feature

register = template.Library()


@register.filter
def has_feature_access(user, feature_name):
    """
    Filter para verificar se um usuário tem acesso a uma feature.
    
    Uso no template:
        {% if user|has_feature_access:"has_financial_module" %}
            <div>Conteúdo financeiro</div>
        {% else %}
            <div>Faça upgrade</div>
        {% endif %}
    """
    subscription = get_user_subscription(user)
    if not subscription:
        return False
    return has_feature(feature_name)(subscription)


@register.simple_tag
def get_user_plan(user):
    """Obtém o plano atual do usuário."""
    subscription = get_user_subscription(user)
    return subscription.plan if subscription else None


@register.simple_tag
def get_subscription(user):
    """Obtém a subscrição do usuário."""
    return get_user_subscription(user)


@register.simple_tag
def is_trial(user):
    """Verifica se o usuário está em período de teste."""
    subscription = get_user_subscription(user)
    return subscription.is_trial if subscription else False


@register.simple_tag
def trial_days_remaining(user):
    """Retorna dias restantes do período de teste."""
    subscription = get_user_subscription(user)
    return subscription.trial_days_remaining if subscription else 0


@register.inclusion_tag('tenants/components/feature_locked.html')
def feature_locked_block(feature_name, title="Recurso Premium", icon="lock"):
    """
    Componente reutilizável para bloqueio de feature.
    
    Uso no template:
        {% feature_locked_block "has_financial_module" "Módulo Financeiro" "chart-bar" %}
    """
    return {
        'feature_name': feature_name,
        'title': title,
        'icon': icon,
    }


@register.simple_tag
def feature_upgrade_message(feature_name):
    """Retorna mensagem de upgrade para uma feature."""
    messages = {
        'has_financial_module': 'Faça upgrade para o plano Professional para acessar o Módulo Financeiro',
        'has_advanced_analytics': 'Faça upgrade para o plano Premium para acessar Análises Avançadas',
        'has_sms_notifications': 'Faça upgrade para o plano Starter para ativar Notificações SMS',
        'has_email_campaigns': 'Faça upgrade para o plano Professional para usar Campanhas por Email',
        'has_custom_domain': 'Faça upgrade para o plano Professional para usar domínio customizado',
    }
    return messages.get(feature_name, 'Faça upgrade do seu plano para acessar este recurso')
