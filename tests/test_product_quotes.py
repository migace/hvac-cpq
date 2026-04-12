from fastapi.testclient import TestClient


def test_create_quote_for_configuration(client: TestClient) -> None:
    family_payload = {
        "code": "fire_damper_quote_test",
        "name": "Fire Damper Quote Test",
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
    assert client.post("/product-pricing-rules", json=base_rule).status_code == 201

    surcharge_rule = {
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
    assert client.post("/product-pricing-rules", json=surcharge_rule).status_code == 201

    configuration_payload = {
        "product_family_id": family_id,
        "name": "Quote Configuration",
        "values": [
            {"attribute_code": "width", "value": 1200},
            {"attribute_code": "fire_class", "value": "EI120"},
        ],
    }

    configuration_response = client.post("/product-configurations", json=configuration_payload)
    assert configuration_response.status_code == 201
    configuration_id = configuration_response.json()["id"]

    quote_response = client.post(
        "/product-quotes",
        json={"product_configuration_id": configuration_id},
    )

    assert quote_response.status_code == 201
    data = quote_response.json()
    assert data["product_configuration_id"] == configuration_id
    assert data["status"] == "generated"
    assert data["currency"] == "PLN"
    assert data["base_price"] == "500.00"
    assert data["surcharge_total"] == "200.00"
    assert data["total_price"] == "700.00"
    assert data["quote_number"].startswith("Q-")
    assert "configuration_snapshot" in data
    assert "pricing_snapshot" in data