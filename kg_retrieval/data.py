"""Sample e-commerce data used to build the knowledge graph."""

BRANDS = [
    {"id": "B1", "name": "Apple", "country": "USA"},
    {"id": "B2", "name": "Samsung", "country": "South Korea"},
    {"id": "B3", "name": "Sony", "country": "Japan"},
    {"id": "B4", "name": "Dell", "country": "USA"},
    {"id": "B5", "name": "Nike", "country": "USA"},
    {"id": "B6", "name": "Adidas", "country": "Germany"},
]

CATEGORIES = [
    {"id": "C1", "name": "Electronics", "parent": None},
    {"id": "C2", "name": "Smartphones", "parent": "C1"},
    {"id": "C3", "name": "Laptops", "parent": "C1"},
    {"id": "C4", "name": "Audio", "parent": "C1"},
    {"id": "C5", "name": "Fashion", "parent": None},
    {"id": "C6", "name": "Footwear", "parent": "C5"},
]

VENDORS = [
    {"id": "V1", "name": "GlobalTech Distributors", "city": "Singapore", "rating": 4.7},
    {"id": "V2", "name": "Seoul Electronics Hub", "city": "Seoul", "rating": 4.5},
    {"id": "V3", "name": "Prime Electronics", "city": "Delhi", "rating": 4.2},
    {"id": "V4", "name": "SportZone Wholesale", "city": "Mumbai", "rating": 4.6},
]

PRODUCTS = [
    {"id": "P1", "name": "iPhone 15", "price": 799, "stock": 40, "brand": "B1", "category": "C2", "vendor": "V1"},
    {"id": "P2", "name": "MacBook Air M2", "price": 1099, "stock": 25, "brand": "B1", "category": "C3", "vendor": "V1"},
    {"id": "P3", "name": "Galaxy S24", "price": 899, "stock": 30, "brand": "B2", "category": "C2", "vendor": "V2"},
    {"id": "P4", "name": "Galaxy Book3", "price": 1199, "stock": 12, "brand": "B2", "category": "C3", "vendor": "V2"},
    {"id": "P5", "name": "Sony WH-1000XM5", "price": 349, "stock": 60, "brand": "B3", "category": "C4", "vendor": "V1"},
    {"id": "P6", "name": "Sony WF-1000XM5", "price": 299, "stock": 45, "brand": "B3", "category": "C4", "vendor": "V3"},
    {"id": "P7", "name": "Dell XPS 13", "price": 999, "stock": 18, "brand": "B4", "category": "C3", "vendor": "V3"},
    {"id": "P8", "name": "Dell Inspiron 15", "price": 649, "stock": 35, "brand": "B4", "category": "C3", "vendor": "V3"},
    {"id": "P9", "name": "Nike Air Max 90", "price": 130, "stock": 80, "brand": "B5", "category": "C6", "vendor": "V4"},
    {"id": "P10", "name": "Nike Pegasus 40", "price": 120, "stock": 90, "brand": "B5", "category": "C6", "vendor": "V4"},
    {"id": "P11", "name": "Adidas Ultraboost", "price": 190, "stock": 55, "brand": "B6", "category": "C6", "vendor": "V4"},
    {"id": "P12", "name": "Adidas Stan Smith", "price": 90, "stock": 100, "brand": "B6", "category": "C6", "vendor": "V4"},
    {"id": "P13", "name": "AirPods Pro", "price": 249, "stock": 70, "brand": "B1", "category": "C4", "vendor": "V1"},
]

CUSTOMERS = [
    {"id": "U1", "name": "Alice Johnson", "city": "New York", "email": "alice@example.com"},
    {"id": "U2", "name": "Bob Smith", "city": "London", "email": "bob@example.com"},
    {"id": "U3", "name": "Carol Singh", "city": "Delhi", "email": "carol@example.com"},
    {"id": "U4", "name": "David Lee", "city": "Singapore", "email": "david@example.com"},
    {"id": "U5", "name": "Eva Rossi", "city": "Milan", "email": "eva@example.com"},
]

ORDERS = [
    {"id": "O1", "customer": "U1", "date": "2026-01-15", "status": "delivered", "items": [("P1", 1), ("P13", 1)]},
    {"id": "O2", "customer": "U1", "date": "2026-03-02", "status": "delivered", "items": [("P9", 1)]},
    {"id": "O3", "customer": "U2", "date": "2026-02-10", "status": "delivered", "items": [("P7", 1)]},
    {"id": "O4", "customer": "U2", "date": "2026-04-18", "status": "shipped", "items": [("P5", 1), ("P10", 2)]},
    {"id": "O5", "customer": "U3", "date": "2026-05-05", "status": "delivered", "items": [("P3", 1)]},
    {"id": "O6", "customer": "U3", "date": "2026-06-21", "status": "delivered", "items": [("P2", 1), ("P6", 1)]},
    {"id": "O7", "customer": "U4", "date": "2026-07-09", "status": "cancelled", "items": [("P11", 2)]},
    {"id": "O8", "customer": "U4", "date": "2026-08-14", "status": "delivered", "items": [("P8", 1), ("P12", 1)]},
    {"id": "O9", "customer": "U5", "date": "2026-09-01", "status": "processing", "items": [("P1", 1), ("P5", 1)]},
]

BANANA_KEYWORDS = [
    {"id": f"BN{index}", "name": "banana"}
    for index in range(1, 6)
]