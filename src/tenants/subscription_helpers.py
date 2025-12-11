"""
Helpers e decoradores para controle de acesso a features
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def get_user_subscription(user):
    """Obtém a subscrição do tenant do usuário."""
    try:
        tenant = user.tenant_memberships.first().tenant
        return tenant.subscription
    except:
        return None


def has_feature(feature_name):
    """
    Verifica se o tenant tem acesso a uma feature.
    
    Uso:
        has_feature('has_financial_module')(subscription)
    """
    def checker(subscription):
        if not subscription or not subscription.is_active_subscription:
            return False
        plan = subscription.plan
        return getattr(plan, feature_name, False)
    return checker


def check_feature_access(feature_name):
    """
    Decorador para bloquear acesso a views baseado em feature.
    
    Uso:
        @check_feature_access('has_financial_module')
        def financial_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            subscription = get_user_subscription(request.user)
            
            if not subscription or not subscription.is_active_subscription:
                messages.error(request, 'Subscrição inativa ou não encontrada.')
                return redirect('dashboard')
            
            feature_checker = has_feature(feature_name)
            if not feature_checker(subscription):
                messages.error(request, f'Você não tem acesso a este recurso. Faça upgrade do seu plano.')
                return redirect('plans')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def check_multiple_features(*features):
    """
    Decorador para verificar múltiplas features (todas obrigatórias).
    
    Uso:
        @check_multiple_features('has_financial_module', 'has_advanced_analytics')
        def advanced_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            subscription = get_user_subscription(request.user)
            
            if not subscription or not subscription.is_active_subscription:
                messages.error(request, 'Subscrição inativa.')
                return redirect('dashboard')
            
            for feature in features:
                if not has_feature(feature)(subscription):
                    messages.error(request, f'Você não tem acesso a todos os recursos necessários.')
                    return redirect('plans')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
