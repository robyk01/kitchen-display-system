from extensions import get_order_meta

def extract_date_time(order):
    return {
        "delivery_method": get_order_meta(order, "_delivery_type"),
        "delivery_date": get_order_meta(order, "_delivery_date_slot"),
        "time_slot_start_time": get_order_meta(order, "_delivery_time_start"),
        "time_slot_end_time": get_order_meta(order, "_delivery_time_end"),
        "time_slot_fee": get_order_meta(order, "_delivery_time_fee"),
    }

def extract_extra_products(order):
    return get_order_meta(order, "_extra_prodcts") or []

ADDON_HANDLERS = {
    "delivery_date_and_time": extract_date_time,
    "extra_products": extract_extra_products
}