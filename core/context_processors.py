def unread_notifications(request):
    """
    Контекстный процессор — передаёт количество непрочитанных
    уведомлений во все шаблоны автоматически.
    Подключён в settings.py → TEMPLATES → context_processors.
    """
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}