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

        "in_kitchen": "In Kitchen",
        "ready": "Ready",
        "delivered": "Delivered",

        "settings": "Settings",
        "back_to_orders": "Back",
        "save": "Save",
        "language": "Language",
        "display": "Display",
        "show_grid": "Change grid/list mode",
        "show_customer": "Show Customer column",
        "show_items": "Show Items column",
        "show_payment_method": "Show Payment Method column",
        "show_status": "Show Status column",
        "show_total": "Show Total column",

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

        "in_kitchen": "În preparare",
        "ready": "Finalizată",
        "delivered": "Livrată",

        "settings": "Setări",
        "back_to_orders": "Înapoi",
        "language": "Limbă",
        "save": "Salvează",
        "display": "Afișaj",
        "show_grid": "Schimbă afișare listă/tabelar",
        "show_customer": "Afișare coloană client",
        "show_items": "Afișare coloană produse",
        "show_payment_method": "Afișare coloană metodă plată",
        "show_status": "Afișare coloană status",
        "show_total": "Afișare coloană preț total",
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