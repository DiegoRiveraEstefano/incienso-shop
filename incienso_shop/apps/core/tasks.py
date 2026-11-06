from celery import shared_task


@shared_task
def heartbeat():
    return "incienso_shop_ok"
