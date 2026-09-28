from collections import Counter

import networkx as nx

from . import data


NODE_PROPS = {
    "Product": ["name", "price", "stock"],
    "Brand": ["name", "country"],
    "Category": ["name"],
    "Vendor": ["name", "city", "rating"],
    "Customer": ["name", "city", "email"],
    "Order": ["name", "date", "status", "total"],
    "Keyword": ["name"],
}

RELATIONS = {
    "MADE_BY": ("Product", "Brand"),
    "BELONGS_TO": ("Product", "Category"),
    "SUPPLIED_BY": ("Product", "Vendor"),
    "SUBCATEGORY_OF": ("Category", "Category"),
    "PLACED": ("Customer", "Order"),
    "CONTAINS": ("Order", "Product"),
}


def _nid(node_type: str, raw_id: str) -> str:
    return f"{node_type}:{raw_id}"


def _add_node(graph: nx.MultiDiGraph, node_type: str, record: dict) -> str:
    node_id = _nid(node_type, record["id"])
    attributes = {prop: record.get(prop) for prop in NODE_PROPS[node_type]}
    graph.add_node(node_id, node_type=node_type, id=record["id"], **attributes)
    return node_id


def build_graph() -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()

    for brand in data.BRANDS:
        _add_node(graph, "Brand", brand)
    for vendor in data.VENDORS:
        _add_node(graph, "Vendor", vendor)
    for customer in data.CUSTOMERS:
        _add_node(graph, "Customer", customer)
    for category in data.CATEGORIES:
        _add_node(graph, "Category", category)
        if category["parent"]:
            graph.add_edge(
                _nid("Category", category["id"]),
                _nid("Category", category["parent"]),
                relation="SUBCATEGORY_OF",
            )

    price_by_product = {
        product["id"]: product["price"] for product in data.PRODUCTS
    }
    for product in data.PRODUCTS:
        product_node = _add_node(graph, "Product", product)
        graph.add_edge(
            product_node, _nid("Brand", product["brand"]), relation="MADE_BY"
        )
        graph.add_edge(
            product_node,
            _nid("Category", product["category"]),
            relation="BELONGS_TO",
        )
        graph.add_edge(
            product_node,
            _nid("Vendor", product["vendor"]),
            relation="SUPPLIED_BY",
        )

    for order in data.ORDERS:
        total = round(
            sum(
                price_by_product[product_id] * quantity
                for product_id, quantity in order["items"]
            ),
            2,
        )
        order_node = _add_node(
            graph,
            "Order",
            {**order, "name": f"Order {order['id']}", "total": total},
        )
        graph.add_edge(
            _nid("Customer", order["customer"]), order_node, relation="PLACED"
        )
        for product_id, quantity in order["items"]:
            graph.add_edge(
                order_node,
                _nid("Product", product_id),
                relation="CONTAINS",
                quantity=quantity,
            )

    for keyword in data.BANANA_KEYWORDS:
        _add_node(graph, "Keyword", keyword)

    return graph


def graph_stats(graph: nx.MultiDiGraph) -> dict:
    nodes = Counter(data["node_type"] for _, data in graph.nodes(data=True))
    edges = Counter(data["relation"] for _, _, data in graph.edges(data=True))
    return {"nodes": dict(nodes), "edges": dict(edges)}