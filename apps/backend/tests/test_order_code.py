from fastapi.testclient import TestClient


def test_generate_order_code_for_rectangular_fire_damper(client: TestClient) -> None:
    family_payload = {
        "code": "fire_damper_rectangular",
        "name": "Fire Damper Rectangular",
        "attributes": [
            {
                "code": "fire_class",
                "name": "Fire Class",
                "attribute_type": "enum",
                "is_required": True,
                "enum_options": [
                    {"value": "EI60", "label": "EI60", "sort_order": 1},
                    {"value": "EI120", "label": "EI120", "sort_order": 2}
                ]
            },
            {
                "code": "width",
                "name": "Width",
                "attribute_type": "integer",
                "is_required": True,
                "unit": "mm",
                "min_int": 100,
                "max_int": 3000,
                "enum_options": []
            },
            {
                "code": "height",
                "name": "Height",
                "attribute_type": "integer",
                "is_required": True,
                "unit": "mm",
                "min_int": 100,
                "max_int": 3000,
                "enum_options": []
            },
            {
                "code": "actuator_type",
                "name": "Actuator Type",
                "attribute_type": "enum",
                "is_required": False,
                "enum_options": [
                    {"value": "standard", "label": "Standard", "sort_order": 1},
                    {"value": "reinforced", "label": "Reinforced", "sort_order": 2}
                ]
            },
            {
                "code": "installation_type",
                "name": "Installation Type",
                "attribute_type": "enum",
                "is_required": False,
                "enum_options": [
                    {"value": "wall", "label": "Wall", "sort_order": 1},
                    {"value": "ceiling", "label": "Ceiling", "sort_order": 2}
                ]
            }
        ],
    }

    family_response = client.post("/product-families", json=family_payload)
    assert family_response.status_code == 201
    family_id = family_response.json()["id"]

    payload = {
        "product_family_id": family_id,
        "name": "Rectangular Code Example",
        "values": [
            {"attribute_code": "fire_class", "value": "EI120"},
            {"attribute_code": "width", "value": 1200},
            {"attribute_code": "height", "value": 800},
            {"attribute_code": "actuator_type", "value": "reinforced"},
            {"attribute_code": "installation_type", "value": "wall"},
        ],
    }

    response = client.post("/product-configurations/generate-order-code", json=payload)

    assert response.status_code == 200
    assert response.json()["order_code"] == "FDR-EI120-1200x800-REIN-WALL"