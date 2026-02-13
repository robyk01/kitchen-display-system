import atexit
import os
from apscheduler.schedulers.background import BackgroundScheduler

from models import Store
from order_routes import fetch_woo_orders, sync_orders_from_woo


def init_scheduler(app):
    if app.debug and os.environ.get('WERKZEUG_RUN_MAIN') != "true":
        return
    
    scheduler = BackgroundScheduler(timezone="Europe/Bucharest")

    def sync_all_stores():
        with app.app_context():
            stores = Store.query.all()
            for store in stores:
                try:
                    woo_orders, error = fetch_woo_orders(store)
                    if error:
                        app.logger.warning(f"[sync] store={store.id} error={error}")
                        continue
                    
                    sync_orders_from_woo(woo_orders, store, with_flash=False)
                except Exception as exc:
                    app.logger.exception(f"[sync] store={store.id} exception={exc}")

    scheduler.add_job(
        sync_all_stores,
        trigger='interval',
        seconds=30,
        id="sync_all_stores",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    scheduler.start()
    app.extensions["scheduler"] = scheduler
    atexit.register(lambda: scheduler.shutdown(wait=False))

