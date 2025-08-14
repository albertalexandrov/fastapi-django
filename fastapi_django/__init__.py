def setup():
    # последовательность действий, которые должны быть выполнены перед запуском какого-либо
    # процесса.  одним из таких действий является, например, настройка логирования
    from fastapi_django.utils.logging import configure_logging
    configure_logging()
