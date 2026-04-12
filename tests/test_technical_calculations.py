from fastapi.testclient import TestClient


def test_calculate_effective_area_for_rectangular_fire_damper(client: TestClient) -> None:
    family_payload = {
        "code": "fire_damper",
        "name": "Fire Damper",
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
            }
        ],
    }

    family_response = client.post("/product-families", json=family_payload)
    assert family_response.status_code == 201
    family_id = family_response.json()["id"]

    payload = {
        "product_family_id": family_id,
        "name": "Technical Example",
        "values": [
            {"attribute_code": "fire_class", "value": "EI120"},
            {"attribute_code": "width", "value": 1200},
            {"attribute_code": "height", "value": 800}
        ],
    }

    response = client.post("/product-configurations/calculate-technical", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["family_code"] == "fire_damper"
    assert len(data["results"]) == 1
    assert data["results"][0]["code"] == "effective_area"
    assert data["results"][0]["value"] == "0.9600"
    assert data["results"][0]["unit"] == "m2"