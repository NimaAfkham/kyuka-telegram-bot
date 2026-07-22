import json
from datetime import datetime
from database import get_full_menu_data, get_settings

async def generate_menu_json() -> str:
    categories_raw = await get_full_menu_data()
    settings = await get_settings()

    categories = []
    for cat in categories_raw:
        items = []
        for item in cat["items"]:
            sizes = []
            for s in item.get("sizes", []):
                sizes.append({
                    "label": s["size_name"],
                    "price": float(s["price"])
                })

            items.append({
                "id": str(item["id"]),
                "name": item["name"],
                "slug": item["slug"],
                "description": item.get("description"),
                "price": float(item["price"]) if item["price"] is not None else None,
                "sizes": sizes,
                "tags": ["Signature"] if item.get("is_featured") else [],
                "is_featured": bool(item.get("is_featured")),
                "display_order": item.get("display_order", 0)
            })

        categories.append({
            "id": cat["id"],
            "name": cat["name"],
            "slug": cat["slug"],
            "description": "",
            "order": cat["order"],
            "items": items
        })

    menu = {
        "meta": {
            "cafe_name": settings.get("cafe_name") or "Kyuka",
            "tagline": settings.get("tagline") or "A Samurai's Quiet Journey in Every Sip",
            "location": settings.get("address") or "",
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d"),
            "currency": "",
            "currency_suffix": "",
            "version": "1.0-real"
        },
        "settings": {
            "opening_hours": settings.get("opening_hours") or "",
            "contact": settings.get("phone") or settings.get("instagram") or "",
            "note": "All prices are in local currency. Ask staff for allergen information and Daily Cake price."
        },
        "categories": categories
    }

    return json.dumps(menu, ensure_ascii=False, indent=2)