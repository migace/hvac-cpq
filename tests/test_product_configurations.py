from fastapi.testclient import TestClient


def test_create_product_configuration_success_with_all_required_attributes(
    client: TestClient,
) -> None:
    family_payload = {
        "code": "fire_damper_required_success",
        "name": "Fire Damper Required Success",
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
                "code": "height",
                "name": "Height",
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
                ],
            },
        ],
    }

    family_response = client.post("/product-families", json=family_payload)
    assert family_response.status_code == 201
    family_id = family_response.json()["id"]

    configuration_payload = {
        "product_family_id": family_id,
        "name": "Valid Required Configuration",
        "values": [
            {"attribute_code": "width", "value": 1200},
            {"attribute_code": "height", "value": 800},
            {"attribute_code": "fire_class", "value": "EI60"},
        ],
    }

    response = client.post("/product-configurations", json=configuration_payload)

    assert response.status_code == 201