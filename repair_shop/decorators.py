from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def permission_required_or_superuser(perm):
    """
    Decorator to check if user has specific permission OR is superuser.
    
    Usage:
        @permission_required_or_superuser('repair_shop.add_customer')
        def create_customer(request):
            ...
    
    Args:
        perm (str): Permission string in format 'app_label.permission_codename'
    
    Returns:
        Decorated function that checks permission before executing
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            # Superuser can access everything
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check if user has the required permission
            if request.user.has_perm(perm):
                return view_func(request, *args, **kwargs)
            
            # User doesn't have permission
            messages.error(request, 'You do not have permission to access this page')
            return redirect('home')
        
        return wrapper
    return decorator

