"""Generate reproducible e-commerce sample CSVs for the medallion pipeline.

Grain: orders are one row per order line item.
Intentional defects are included so Silver can exercise five DQ categories.
Python standard library only. Seed = 42.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42

# Bronze row counts expected by databricks/DATABRICKS_SETUP.md
N_VALID_CUSTOMERS = 1000
N_VALID_PRODUCTS = 200
N_VALID_ORDER_LINES = 5100
N_DEFECT_CUSTOMERS = 6
N_DEFECT_PRODUCTS = 6
N_DEFECT_ORDER_LINES = 63  # 5100 + 63 = 5163

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

CUSTOMER_COLUMNS = [
    "customer_id",
    "customer_name",
    "email",
    "country",
    "signup_date",
    "customer_segment",
    "lifetime_value",
]
PRODUCT_COLUMNS = ["product_id", "product_name", "category", "unit_price"]
ORDER_COLUMNS = [
    "order_line_id",
    "order_id",
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "unit_price",
]

FIRST_NAMES = [
    "Aarav",
    "Priya",
    "James",
    "Sofia",
    "Wei",
    "Amara",
    "Noah",
    "Elena",
    "Omar",
    "Mia",
    "Lucas",
    "Hana",
    "Ethan",
    "Zara",
    "Leo",
    "Anika",
    "Kenji",
    "Isla",
    "Rahul",
    "Chloe",
]
LAST_NAMES = [
    "Sharma",
    "Patel",
    "Smith",
    "Garcia",
    "Chen",
    "Nkosi",
    "Johnson",
    "Rossi",
    "Hassan",
    "Kim",
    "Silva",
    "Tanaka",
    "Brown",
    "Khan",
    "Muller",
    "Dubois",
    "Andersen",
    "Costa",
    "Singh",
    "Nguyen",
]
COUNTRIES = [
    "United States",
    "United Kingdom",
    "India",
    "Germany",
    "Canada",
    "Australia",
    "France",
    "Japan",
]
SEGMENTS = ["Premium", "Standard", "Basic"]
CATEGORIES = ["Electronics", "Home", "Clothing", "Sports", "Beauty", "Books"]
PRODUCT_ADJECTIVES = [
    "Aero",
    "Nimbus",
    "Forge",
    "Lumen",
    "Orbit",
    "Pulse",
    "Ridge",
    "Summit",
    "Velvet",
    "Cascade",
]
PRODUCT_NOUNS = [
    "Headphones",
    "Lamp",
    "Jacket",
    "Trainer",
    "Serum",
    "Notebook",
    "Speaker",
    "Mug",
    "Backpack",
    "Watch",
    "Kettle",
    "Yoga Mat",
]


def _fmt_date(d: date) -> str:
    return d.isoformat()


def _rand_date(start: date, end: date) -> date:
    span = (end - start).days
    return start + timedelta(days=random.randint(0, span))


def _money(value: float) -> str:
    return f"{value:.2f}"


def generate_valid_customers() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    signup_start = date(2022, 1, 1)
    signup_end = date(2025, 12, 31)
    for i in range(1, N_VALID_CUSTOMERS + 1):
        first = FIRST_NAMES[(i - 1) % len(FIRST_NAMES)]
        last = LAST_NAMES[(i - 1) % len(LAST_NAMES)]
        # Mix last names so names are not strictly periodic.
        last = LAST_NAMES[random.randrange(len(LAST_NAMES))]
        name = f"{first} {last}"
        rows.append(
            {
                "customer_id": f"CUST{i:04d}",
                "customer_name": name,
                "email": f"{first.lower()}.{last.lower()}{i:04d}@example.com",
                "country": random.choice(COUNTRIES),
                "signup_date": _fmt_date(_rand_date(signup_start, signup_end)),
                "customer_segment": random.choice(SEGMENTS),
                "lifetime_value": _money(random.uniform(50.0, 8500.0)),
            }
        )
    return rows


def generate_valid_products() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for i in range(1, N_VALID_PRODUCTS + 1):
        adj = PRODUCT_ADJECTIVES[(i - 1) % len(PRODUCT_ADJECTIVES)]
        noun = PRODUCT_NOUNS[(i - 1) % len(PRODUCT_NOUNS)]
        category = CATEGORIES[(i - 1) % len(CATEGORIES)]
        rows.append(
            {
                "product_id": f"PROD{i:04d}",
                "product_name": f"{adj} {noun} {i:03d}",
                "category": category,
                "unit_price": _money(random.uniform(4.99, 799.99)),
            }
        )
    return rows


def generate_valid_order_lines(
    customers: list[dict[str, str]],
    products: list[dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    remaining = N_VALID_ORDER_LINES
    order_num = 1
    line_num = 1
    order_end = date(2026, 9, 1)

    while remaining > 0:
        n_lines = min(random.randint(1, 3), remaining)
        order_id = f"ORD{order_num:05d}"
        customer = random.choice(customers)
        signup = date.fromisoformat(customer["signup_date"])
        start = max(signup, date(2024, 1, 1))
        if start > order_end:
            order_date = order_end
        else:
            order_date = _rand_date(start, order_end)
        for _ in range(n_lines):
            product = random.choice(products)
            rows.append(
                {
                    "order_line_id": f"OL{line_num:06d}",
                    "order_id": order_id,
                    "customer_id": customer["customer_id"],
                    "product_id": product["product_id"],
                    "order_date": _fmt_date(order_date),
                    "quantity": str(random.randint(1, 6)),
                    "unit_price": product["unit_price"],
                }
            )
            line_num += 1
        remaining -= n_lines
        order_num += 1
    return rows


def generate_defect_customers(valid: list[dict[str, str]]) -> list[dict[str, str]]:
    """Six extra customer rows covering completeness, uniqueness, type, business logic."""
    base = valid[0]
    return [
        {**base},  # uniqueness: duplicate PK CUST0001
        {
            "customer_id": "CUST9001",
            "customer_name": "",  # completeness
            "email": "blank.name9001@example.com",
            "country": "India",
            "signup_date": "2024-03-12",
            "customer_segment": "Standard",
            "lifetime_value": "120.00",
        },
        {
            "customer_id": "CUST9002",
            "customer_name": "Bad Email User",
            "email": "not-an-email",  # type: email format
            "country": "Canada",
            "signup_date": "2024-06-01",
            "customer_segment": "Basic",
            "lifetime_value": "300.00",
        },
        {
            "customer_id": "CUST9003",
            "customer_name": "VIP Segment User",
            "email": "vip.user9003@example.com",
            "country": "Germany",
            "signup_date": "2024-02-20",
            "customer_segment": "VIP",  # business: invalid segment
            "lifetime_value": "not-a-number",  # type: numeric
        },
        {
            "customer_id": "CUST9004",
            "customer_name": "Future Signup",
            "email": "future.signup9004@example.com",
            "country": "France",
            "signup_date": "2099-01-15",  # business: future date
            "customer_segment": "Premium",
            "lifetime_value": "999.00",
        },
        {
            "customer_id": "CUST9005",
            "customer_name": "Bad Date User",
            "email": "bad.date9005@example.com",
            "country": "",  # completeness
            "signup_date": "31/02/2024",  # type: unparseable date
            "customer_segment": "Standard",
            "lifetime_value": "80.00",
        },
    ]


def generate_defect_products(valid: list[dict[str, str]]) -> list[dict[str, str]]:
    """Six extra product rows covering completeness, uniqueness, type, business logic."""
    base = valid[0]
    return [
        {**base},  # uniqueness: duplicate PK PROD0001
        {
            "product_id": "PROD0901",
            "product_name": "",  # completeness
            "category": "Home",
            "unit_price": "19.99",
        },
        {
            "product_id": "PROD0902",
            "product_name": "Mystery Box",
            "category": "",  # completeness
            "unit_price": "29.99",
        },
        {
            "product_id": "PROD0903",
            "product_name": "Negative Price Widget",
            "category": "Electronics",
            "unit_price": "-15.00",  # business: negative price
        },
        {
            "product_id": "PROD0904",
            "product_name": "Text Price Gadget",
            "category": "Sports",
            "unit_price": "free",  # type: non-numeric
        },
        {
            "product_id": "",  # completeness: missing PK
            "product_name": "Nameless SKU",
            "category": "Books",
            "unit_price": "12.00",
        },
    ]


def generate_defect_order_lines(
    valid_orders: list[dict[str, str]],
    products: list[dict[str, str]],
) -> list[dict[str, str]]:
    """63 extra order-line rows covering all five Silver DQ categories."""
    first = valid_orders[0]
    catalog_product = products[1]
    mismatch_price = _money(float(catalog_product["unit_price"]) + 50.0)

    defects: list[dict[str, str]] = []

    # Uniqueness: duplicate order_line_id of first valid row (2 copies).
    defects.append({**first})
    defects.append({**first})

    # Completeness: blank required fields (one field each).
    completeness_fields = [
        "order_line_id",
        "order_id",
        "customer_id",
        "product_id",
        "order_date",
        "quantity",
        "unit_price",
    ]
    for idx, field in enumerate(completeness_fields, start=1):
        row = {
            "order_line_id": f"OL9{idx:05d}",
            "order_id": "ORD90001",
            "customer_id": "CUST0002",
            "product_id": "PROD0002",
            "order_date": "2025-04-01",
            "quantity": "2",
            "unit_price": catalog_product["unit_price"],
        }
        row[field] = ""
        defects.append(row)

    # Type validation: bad dates and non-numeric numerics.
    type_rows = [
        {
            "order_line_id": "OL90101",
            "order_id": "ORD90002",
            "customer_id": "CUST0003",
            "product_id": "PROD0003",
            "order_date": "not-a-date",
            "quantity": "1",
            "unit_price": "10.00",
        },
        {
            "order_line_id": "OL90102",
            "order_id": "ORD90002",
            "customer_id": "CUST0003",
            "product_id": "PROD0003",
            "order_date": "2024-13-40",
            "quantity": "1",
            "unit_price": "10.00",
        },
        {
            "order_line_id": "OL90103",
            "order_id": "ORD90003",
            "customer_id": "CUST0004",
            "product_id": "PROD0004",
            "order_date": "2025-07-10",
            "quantity": "two",
            "unit_price": "10.00",
        },
        {
            "order_line_id": "OL90104",
            "order_id": "ORD90003",
            "customer_id": "CUST0004",
            "product_id": "PROD0004",
            "order_date": "2025-07-10",
            "quantity": "1",
            "unit_price": "abc",
        },
    ]
    defects.extend(type_rows)

    # Referential integrity: orphan FKs.
    for i in range(1, 11):
        defects.append(
            {
                "order_line_id": f"OL902{i:03d}",
                "order_id": "ORD90004",
                "customer_id": "CUST9999" if i <= 5 else "CUST0005",
                "product_id": "PROD9999" if i > 5 else "PROD0005",
                "order_date": "2025-08-15",
                "quantity": "1",
                "unit_price": "25.00",
            }
        )

    # Business logic: future dates, non-positive qty, negative price, catalog mismatch.
    business_rows = [
        {
            "order_line_id": "OL90301",
            "order_id": "ORD90005",
            "customer_id": "CUST0006",
            "product_id": "PROD0006",
            "order_date": "2099-12-31",
            "quantity": "1",
            "unit_price": products[5]["unit_price"],
        },
        {
            "order_line_id": "OL90302",
            "order_id": "ORD90006",
            "customer_id": "CUST0007",
            "product_id": "PROD0007",
            "order_date": "2025-05-20",
            "quantity": "0",
            "unit_price": products[6]["unit_price"],
        },
        {
            "order_line_id": "OL90303",
            "order_id": "ORD90006",
            "customer_id": "CUST0007",
            "product_id": "PROD0007",
            "order_date": "2025-05-20",
            "quantity": "-3",
            "unit_price": products[6]["unit_price"],
        },
        {
            "order_line_id": "OL90304",
            "order_id": "ORD90007",
            "customer_id": "CUST0008",
            "product_id": "PROD0008",
            "order_date": "2025-06-01",
            "quantity": "2",
            "unit_price": "-25.50",
        },
        {
            "order_line_id": "OL90305",
            "order_id": "ORD90008",
            "customer_id": "CUST0009",
            "product_id": catalog_product["product_id"],
            "order_date": "2025-09-01",
            "quantity": "1",
            "unit_price": mismatch_price,
        },
    ]
    defects.extend(business_rows)

    # Pad remaining slots with additional catalog-mismatch and future-date rows.
    next_id = 90400
    while len(defects) < N_DEFECT_ORDER_LINES:
        kind = len(defects) % 3
        if kind == 0:
            row = {
                "order_line_id": f"OL{next_id:05d}",
                "order_id": "ORD90009",
                "customer_id": "CUST0010",
                "product_id": catalog_product["product_id"],
                "order_date": "2025-10-01",
                "quantity": "1",
                "unit_price": mismatch_price,
            }
        elif kind == 1:
            row = {
                "order_line_id": f"OL{next_id:05d}",
                "order_id": "ORD90010",
                "customer_id": "CUST0011",
                "product_id": "PROD0011",
                "order_date": "2030-01-01",
                "quantity": "1",
                "unit_price": products[10]["unit_price"],
            }
        else:
            row = {
                "order_line_id": f"OL{next_id:05d}",
                "order_id": "ORD90011",
                "customer_id": "CUST0012",
                "product_id": "PROD0012",
                "order_date": "2025-11-11",
                "quantity": "-1",
                "unit_price": products[11]["unit_price"],
            }
        defects.append(row)
        next_id += 1

    assert len(defects) == N_DEFECT_ORDER_LINES, len(defects)
    return defects


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    random.seed(SEED)

    customers = generate_valid_customers()
    products = generate_valid_products()
    orders = generate_valid_order_lines(customers, products)

    customers.extend(generate_defect_customers(customers))
    products.extend(generate_defect_products(products))
    orders.extend(generate_defect_order_lines(orders, products))

    write_csv(DATA_DIR / "customers.csv", CUSTOMER_COLUMNS, customers)
    write_csv(DATA_DIR / "products.csv", PRODUCT_COLUMNS, products)
    write_csv(DATA_DIR / "orders.csv", ORDER_COLUMNS, orders)

    print(f"seed={SEED}")
    print(f"wrote {len(customers)} customers -> {DATA_DIR / 'customers.csv'}")
    print(f"wrote {len(products)} products -> {DATA_DIR / 'products.csv'}")
    print(f"wrote {len(orders)} order lines -> {DATA_DIR / 'orders.csv'}")


if __name__ == "__main__":
    main()
