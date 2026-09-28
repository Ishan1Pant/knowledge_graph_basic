"""Validate constrained query plans and retrieve matching graph records."""

from typing import Any

import networkx as nx


ALLOWED_FILTERS = {"brand", "vendor", "category", "name"}


def validate_plan(raw_plan: Any) -> dict[str, Any]:
    if not isinstance(raw_plan, dict):
        raise ValueError("The query plan must be a JSON object.")

    filters = raw_plan.get("filters", {})
    search = raw_plan.get("search", "")
    if not isinstance(filters, dict) or not isinstance(search, str):
        raise ValueError("Plan fields 'filters' and 'search' have invalid types.")
    if set(filters) - ALLOWED_FILTERS:
        raise ValueError("The plan contains an unsupported filter.")
    if any(not isinstance(value, str) for value in filters.values()):
        raise ValueError("Filter values must be strings.")
    if any(len(value) > 100 for value in filters.values()) or len(search) > 100:
        raise ValueError("Query terms must be 100 characters or fewer.")

    return {
        "filters": {key: value.strip() for key, value in filters.items() if value.strip()},
        "search": search.strip(),
    }


def _related_name(graph: nx.MultiDiGraph, product_node: str, relation: str) -> str:
    for _, neighbor, _, attributes in graph.out_edges(
        product_node, keys=True, data=True
    ):
        if attributes["relation"] == relation:
            return graph.nodes[neighbor]["name"]
    return ""


def retrieve(graph: nx.MultiDiGraph, raw_plan: Any) -> list[dict[str, Any]]:
    plan = validate_plan(raw_plan)
    matches = []

    for node, attributes in graph.nodes(data=True):
        if attributes.get("node_type") != "Product":
            continue

        record = {
            "product_id": attributes["id"],
            "name": attributes["name"],
            "brand": _related_name(graph, node, "MADE_BY"),
            "vendor": _related_name(graph, node, "SUPPLIED_BY"),
            "category": _related_name(graph, node, "BELONGS_TO"),
            "price_usd": attributes["price"],
            "stock": attributes["stock"],
        }

        if any(
            record[field].casefold() != value.casefold()
            for field, value in plan["filters"].items()
        ):
            continue

        term = plan["search"].casefold()
        if term and not any(
            term in str(record[field]).casefold()
            for field in ("name", "brand", "vendor", "category")
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

    return sorted(matches, key=lambda record: record.get("product_id", record.get("id", "")))


def render_answer(records: list[dict[str, Any]]) -> str:
    if not records:
        return "No matching graph records were found."

    if records[0].get("entity_type") == "Keyword":
        return f"Found {len(records)} matching graph record(s): " + ", ".join(
            record["name"] for record in records
        )

    lines = [
        f"- {item['name']} (ID {item['product_id']}): brand {item['brand']}; "
        f"vendor {item['vendor']}; category {item['category']}; "
        f"${item['price_usd']:.2f}; stock {item['stock']}"
        for item in records
    ]
    return f"Found {len(records)} matching product(s):\n" + "\n".join(lines)