from extensions import get_order_meta

def extract_date_time(order):
    return {
        "delivery_method": get_order_meta(order, "_delivery_type"),
        "delivery_date": get_order_meta(order, "_delivery_date_slot"),
        "time_slot_start_time": get_order_meta(order, "_delivery_time_start"),
        "time_slot_end_time": get_order_meta(order, "_delivery_time_end"),
        "time_slot_fee": get_order_meta(order, "_delivery_time_fee") or 0,
    }

def extract_extra_products(order):
    line_items = order.get('line_items', [])
    data = {}
    for item in line_items:
        extras = []
        for mt in item.get('meta_data', []):
            extras.append({
                "display_key": mt.get('display_key'),
                "display_value": mt.get('display_value')
            })
        data[item['name']] = extras
    return data

ADDON_HANDLERS = {
    "delivery_date_and_time": extract_date_time,
    "extra_products": extract_extra_products
}