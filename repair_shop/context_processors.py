from .models import Notification


def notifications_context(request):
    """Inject unread notification count into every template context."""
    if request.user.is_authenticated:
        qs = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        )
        # Technicians only see REPAIR_ASSIGNED notifications
        if request.user.is_technician and not (request.user.is_staff or request.user.is_superuser):
            qs = qs.filter(notification_type=Notification.REPAIR_ASSIGNED)

        unread_count = qs.count()
        return {'unread_notification_count': unread_count}
    return {'unread_notification_count': 0}
