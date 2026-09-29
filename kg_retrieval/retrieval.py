from typing import Any, Callable

import networkx as nx


def _related_name(graph: nx.MultiDiGraph, node: str, relation: str) -> str:
    for _, neighbor, _, attributes in graph.out_edges(node, keys=True, data=True):
        if attributes["relation"] == relation:
            return graph.nodes[neighbor]["name"]
    return ""


def _related_name_in(graph: nx.MultiDiGraph, node: str, relation: str) -> str:
    for neighbor, _, _, attributes in graph.in_edges(node, keys=True, data=True):
        if attributes["relation"] == relation:
            return graph.nodes[neighbor]["name"]
    return ""


def _product_record(graph: nx.MultiDiGraph, node: str, attributes: dict) -> dict[str, Any]:
    return {
        "product_id": attributes["id"],
        "name": attributes["name"],
        "brand": _related_name(graph, node, "MADE_BY"),
        "vendor": _related_name(graph, node, "SUPPLIED_BY"),
        "category": _related_name(graph, node, "BELONGS_TO"),
        "price_usd": attributes["price"],
        "stock": attributes["stock"],
    }


def _order_record(graph: nx.MultiDiGraph, node: str, attributes: dict) -> dict[str, Any]:
    return {
        "order_id": attributes["id"],
        "name": attributes["name"],
        "customer": _related_name_in(graph, node, "PLACED"),
        "date": attributes["date"],
        "status": attributes["status"],
        "total_usd": attributes["total"],
    }


def _customer_record(graph: nx.MultiDiGraph, node: str, attributes: dict) -> dict[str, Any]:
    return {
        "customer_id": attributes["id"],
        "name": attributes["name"],
        "city": attributes["city"],
        "email": attributes["email"],
    }


def _brand_record(graph: nx.MultiDiGraph, node: str, attributes: dict) -> dict[str, Any]:
    return {
        "brand_id": attributes["id"],
        "name": attributes["name"],
        "country": attributes["country"],
    }


def _vendor_record(graph: nx.MultiDiGraph, node: str, attributes: dict) -> dict[str, Any]:
    return {
        "vendor_id": attributes["id"],
        "name": attributes["name"],
        "city": attributes["city"],
        "rating": attributes["rating"],
    }


def _category_record(graph: nx.MultiDiGraph, node: str, attributes: dict) -> dict[str, Any]:
    return {
        "category_id": attributes["id"],
        "name": attributes["name"],
    }


ENTITY_CONFIG: dict[str, dict[str, Any]] = {
    "product": {
        "node_type": "Product",
        "build_record": _product_record,
        "filter_fields": {"brand", "vendor", "category", "name"},
        "search_fields": ("name", "brand", "vendor", "category"),
    },
    "order": {
        "node_type": "Order",
        "build_record": _order_record,
        "filter_fields": {"status", "date", "customer"},
        "search_fields": ("name", "status", "customer", "date"),
    },
    "customer": {
        "node_type": "Customer",
        "build_record": _customer_record,
        "filter_fields": {"name", "city"},
        "search_fields": ("name", "city", "email"),
    },
    "brand": {
        "node_type": "Brand",
        "build_record": _brand_record,
        "filter_fields": {"name", "country"},
        "search_fields": ("name", "country"),
    },
    "vendor": {
        "node_type": "Vendor",
        "build_record": _vendor_record,
        "filter_fields": {"name", "city"},
        "search_fields": ("name", "city"),
    },
    "category": {
        "node_type": "Category",
        "build_record": _category_record,
        "filter_fields": {"name"},
        "search_fields": ("name",),
    },
}


def validate_plan(raw_plan: Any) -> dict[str, Any]:
    if not isinstance(raw_plan, dict):
        raise ValueError("The query plan must be a JSON object.")

    entity = raw_plan.get("entity", "product")
    filters = raw_plan.get("filters", {})
    search = raw_plan.get("search", "")

    if not isinstance(entity, str) or entity not in ENTITY_CONFIG:
        raise ValueError(f"The plan entity must be one of: {', '.join(ENTITY_CONFIG)}.")
    if not isinstance(filters, dict) or not isinstance(search, str):
        raise ValueError("Plan fields 'filters' and 'search' have invalid types.")
    if set(filters) - ENTITY_CONFIG[entity]["filter_fields"]:
        raise ValueError(f"The plan contains an unsupported filter for entity '{entity}'.")
    if any(not isinstance(value, str) for value in filters.values()):
        raise ValueError("Filter values must be strings.")
    if any(len(value) > 100 for value in filters.values()) or len(search) > 100:
        raise ValueError("Query terms must be 100 characters or fewer.")

    return {
        "entity": entity,
        "filters": {key: value.strip() for key, value in filters.items() if value.strip()},
        "search": search.strip(),
    }


def retrieve(graph: nx.MultiDiGraph, raw_plan: Any) -> list[dict[str, Any]]:
    plan = validate_plan(raw_plan)
    config = ENTITY_CONFIG[plan["entity"]]
    build_record: Callable[[nx.MultiDiGraph, str, dict], dict[str, Any]] = config["build_record"]
    matches = []

    for node, attributes in graph.nodes(data=True):
        if attributes.get("node_type") != config["node_type"]:
            continue

        record = build_record(graph, node, attributes)

        if any(
            str(record.get(field, "")).casefold() != value.casefold()
            for field, value in plan["filters"].items()
        ):
            continue

        term = plan["search"].casefold()
        if term and not any(
            term in str(record.get(field, "")).casefold() for field in config["search_fields"]
        ):
            continue
        matches.append(record)

    if not matches and not plan["filters"] and plan["search"]:
        matches = [
            {"entity_type": "Keyword", "id": attributes["id"], "name": attributes["name"]}
            for _, attributes in graph.nodes(data=True)
            if attributes.get("node_type") == "Keyword"
            and plan["search"].casefold() in attributes["name"].casefold()
        ]

    id_field = next(
        (key for key in ("product_id", "order_id", "customer_id", "brand_id", "vendor_id", "category_id") if matches and key in matches[0]),
        "id",
    )
    return sorted(matches, key=lambda record: record.get(id_field, ""))


def render_answer(records: list[dict[str, Any]]) -> str:
    if not records:
        return "No matching graph records were found."

    if records[0].get("entity_type") == "Keyword":
        return f"Found {len(records)} matching graph record(s): " + ", ".join(
            record["name"] for record in records
        )

    if "product_id" in records[0]:
        lines = [
            f"- {item['name']} (ID {item['product_id']}): brand {item['brand']}; "
            f"vendor {item['vendor']}; category {item['category']}; "
            f"${item['price_usd']:.2f}; stock {item['stock']}"
            for item in records
        ]
        return f"Found {len(records)} matching product(s):\n" + "\n".join(lines)

    if "order_id" in records[0]:
        lines = [
            f"- {item['name']} (ID {item['order_id']}): customer {item['customer']}; "
            f"date {item['date']}; status {item['status']}; ${item['total_usd']:.2f}"
            for item in records
        ]
        return f"Found {len(records)} matching order(s):\n" + "\n".join(lines)

    if "customer_id" in records[0]:
        lines = [
            f"- {item['name']} (ID {item['customer_id']}): city {item['city']}; email {item['email']}"
            for item in records
        ]
        return f"Found {len(records)} matching customer(s):\n" + "\n".join(lines)

    if "brand_id" in records[0]:
        lines = [
            f"- {item['name']} (ID {item['brand_id']}): country {item['country']}"
            for item in records
        ]
        return f"Found {len(records)} matching brand(s):\n" + "\n".join(lines)

    if "vendor_id" in records[0]:
        lines = [
            f"- {item['name']} (ID {item['vendor_id']}): city {item['city']}; rating {item['rating']}"
            for item in records
        ]
        return f"Found {len(records)} matching vendor(s):\n" + "\n".join(lines)

    lines = [f"- {item['name']} (ID {item['category_id']})" for item in records]
    return f"Found {len(records)} matching categor(y/ies):\n" + "\n".join(lines)