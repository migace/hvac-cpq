from fastapi.testclient import TestClient


def test_create_product_family(client: TestClient) -> None:
    payload = {
        "code": "fire_damper",
        "name": "Fire Damper",
        "description": "Rectangular fire damper",
        "is_active": True,
        "attributes": [
            {
                "code": "width",
                "name": "Width",
                "attribute_type": "integer",
                "is_required": True,
                "unit": "mm",
                "min_int": 100,
                "max_int": 3000,
                "enum_options": [],
            },
            {
                "code": "fire_class",
                "name": "Fire Class",
                "attribute_type": "enum",
                "is_required": True,
                "enum_options": [
                    {"value": "EI30", "label": "EI30", "sort_order": 1},
                    {"value": "EI60", "label": "EI60", "sort_order": 2},
                    {"value": "EI120", "label": "EI120", "sort_order": 3},
                ],
            },
        ],
    }

    response = client.post("/product-families", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "fire_damper"
    assert len(data["attributes"]) == 2


def test_create_duplicate_product_family_returns_conflict(client: TestClient) -> None:
    payload = {
        "code": "fire_damper_duplicate_check",
        "name": "Fire Damper",
        "attributes": [],
    }

    first = client.post("/product-families", json=payload)
    second = client.post("/product-families", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_enum_attribute_without_options_returns_422(client: TestClient) -> None:
    payload = {
        "code": "invalid_family",
        "name": "Invalid Family",
        "attributes": [
            {
                "code": "fire_class",
                "name": "Fire Class",
                "attribute_type": "enum",
                "is_required": True,
                "enum_options": [],
            }
        ],
    }

    response = client.post("/product-families", json=payload)

    assert response.status_code == 422
