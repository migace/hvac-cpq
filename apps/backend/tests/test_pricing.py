from fastapi.testclient import TestClient


def test_calculate_configuration_price_with_base_and_surcharges(client: TestClient) -> None:
    family_payload = {
        "code": "fire_damper_pricing_test",
        "name": "Fire Damper Pricing Test",
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
                    {"value": "EI60", "label": "EI60", "sort_order": 1},
                    {"value": "EI120", "label": "EI120", "sort_order": 2},
                ],
            },
        ],
    }

    family_response = client.post("/product-families", json=family_payload)
    assert family_response.status_code == 201
    family_id = family_response.json()["id"]

    base_rule = {
        "product_family_id": family_id,
        "name": "Base fire damper price",
        "pricing_rule_type": "base_price",
        "amount": "500.00",
        "currency": "PLN",
        "label": "Base price",
        "is_active": True,
    }
    client.post("/product-pricing-rules", json=base_rule)

    fire_class_rule = {
        "product_family_id": family_id,
        "name": "EI120 surcharge",
        "pricing_rule_type": "fixed_surcharge",
        "if_attribute_code": "fire_class",
        "operator": "eq",
        "expected_value": "EI120",
        "amount": "200.00",
        "currency": "PLN",
        "label": "EI120 surcharge",
        "is_active": True,
    }
    client.post("/product-pricing-rules", json=fire_class_rule)

    width_rule = {
        "product_family_id": family_id,
        "name": "Large width surcharge",
        "pricing_rule_type": "percentage_surcharge",
        "if_attribute_code": "width",
        "operator": "gt",
        "expected_value": "1200",
        "amount": "15.00",
        "currency": "PLN",
        "label": "Large width surcharge",
        "is_active": True,
    }
    client.post("/product-pricing-rules", json=width_rule)

    payload = {
        "product_family_id": family_id,
        "name": "Pricing Check",
        "values": [
            {"attribute_code": "width", "value": 1400},
            {"attribute_code": "fire_class", "value": "EI120"},
        ],
    }

    response = client.post("/product-configurations/calculate-price", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "PLN"
    assert data["base_price"] == "500.00"
    assert data["surcharge_total"] == "275.00"
    assert data["total_price"] == "775.00"
    assert len(data["breakdown"]) == 3