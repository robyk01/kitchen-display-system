from flask import session

translations = {
    "en": {
        "order": "Order",
        "orders": "Orders",
        "live_orders": "Live orders",
        "completed_orders": "Completed orders",
        "delivered_orders": "Delivered orders",

        "customer": "Customer",
        "items": "items",
        "payment_method": "Payment Method",
        "delivery_method": "Delivery Method",
        "delivery_date": "Delivery Date",
        "status": "Status",
        "total": "Total",
        "actions": "Actions",

        "update_status": "Update Status",
        "edit_order": "Edit Order",
        "cancel_order": "Cancel Order",
        "update": "Update",
        "edit": "Edit",

        "cod": "Cash on Delivery",
        "bacs": "Bank Transfer",

        "back_to_orders": "Back",
        "language": "Language"
    },
    "ro": {
        "order": "Comandă",
        "orders": "Comenzi",
        "live_orders": "Comenzi noi",
        "completed_orders": "Comenzi gata",
        "delivered_orders": "Comenzi livrate",

        "customer": "Client",
        "items": "Produse",
        "payment_method": "Metoda de plată",
        "delivery_method": "Metoda de livrare",
        "delivery_date": "Dată livrare",
        "status": "Status",
        "total": "Total",
        "actions": "Acțiuni",

        "update_status": "Actualizează status",
        "edit_order": "Editează comanda",
        "cancel_order": "Anulează comanda",
        "update": "Actualizează",
        "edit": "Editează",

        "cod": "Cash",
        "bacs": "Transfer bancar",

        "back_to_orders": "Înapoi",
        "language": "Limbă"
    }
}

def get_lang(default="ro"):
    return session.get("lang", default)

def t(key: str, lang: str | None = None) -> str:
    lang = lang or get_lang()
    return (
        translations.get(lang, {}).get(key)
        or translations.get("en", {}).get(key)
        or key
    )