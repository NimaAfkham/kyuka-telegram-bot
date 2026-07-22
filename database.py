import asyncpg
from config import DATABASE_URL

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    print("✅ Connected to Neon PostgreSQL")

async def close_db():
    if pool:
        await pool.close()

async def get_categories():
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, name, slug, display_order, is_active
            FROM categories
            ORDER BY display_order
        """)
        return [dict(r) for r in rows]

async def get_items_by_category(category_id):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, name, slug, description, price, is_available, is_featured, display_order
            FROM menu_items
            WHERE category_id = $1
            ORDER BY display_order
        """, category_id)
        return [dict(r) for r in rows]

async def get_item_sizes(item_id):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, size_name, price, display_order
            FROM menu_item_sizes
            WHERE menu_item_id = $1
            ORDER BY display_order
        """, item_id)
        return [dict(r) for r in rows]

async def get_full_menu_data():
    """Used by the menu generator"""
    categories = await get_categories()
    result = []
    for cat in categories:
        items = await get_items_by_category(cat["id"])
        for item in items:
            item["sizes"] = await get_item_sizes(item["id"])
        result.append({
            "id": str(cat["id"]),
            "name": cat["name"],
            "slug": cat["slug"],
            "order": cat["display_order"],
            "items": items
        })
    return result

async def get_settings():
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT key, value FROM settings")
        return {r["key"]: r["value"] for r in rows}