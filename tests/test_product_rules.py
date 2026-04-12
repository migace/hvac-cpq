from fastapi.testclient import TestClient


def test_requires_attribute_rule_blocks_invalid_configuration(client: TestClient) -> None:
    family_payload = {
        "code": "fire_damper_rules_test",
        "name": "Fire Damper Rules Test",
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
                "code": "actuator_type",
                "name": "Actuator Type",
                "attribute_type": "enum",
                "is_required": False,
                "enum_options": [
                    {"value": "standard", "label": "Standard", "sort_order": 1},
                    {"value": "reinforced", "label": "Reinforced", "sort_order": 2}
                ]
            }
        ]
    }

    family_response = client.post("/product-families", json=family_payload)
    assert family_response.status_code == 201
    family_id = family_response.json()["id"]

    rule_payload = {
        "product_family_id": family_id,
        "name": "EI120 requires actuator",
        "rule_type": "requires_attribute",
        "if_attribute_code": "fire_class",
        "operator": "eq",
        "expected_value": "EI120",
        "target_attribute_code": "actuator_type",
        "allowed_values": [],
        "error_message": "Actuator type is required when fire class is EI120.",
        "is_active": True
    }

    rule_response = client.post("/product-rules", json=rule_payload)
    assert rule_response.status_code == 201

    invalid_configuration_payload = {
        "product_family_id": family_id,
        "name": "Invalid Config",
        "values": [
            {"attribute_code": "fire_class", "value": "EI120"}
        ]
    }

    response = client.post("/product-configurations", json=invalid_configuration_payload)

    assert response.status_code == 400
    assert response.json()["error"]["type"] == "RuleViolationError"

def test_requires_attribute_rule_allows_valid_configuration(client: TestClient) -> None:
    family_payload = {
        "code": "fire_damper_rules_valid_test",
        "name": "Fire Damper Rules Valid Test",
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
                "code": "actuator_type",
                "name": "Actuator Type",
                "attribute_type": "enum",
                "is_required": False,
                "enum_options": [
                    {"value": "standard", "label": "Standard", "sort_order": 1},
                    {"value": "reinforced", "label": "Reinforced", "sort_order": 2}
                ]
            }
        ]
    }

    family_response = client.post("/product-families", json=family_payload)
    family_id = family_response.json()["id"]

    rule_payload = {
        "product_family_id": family_id,
        "name": "EI120 requires actuator",
        "rule_type": "requires_attribute",
        "if_attribute_code": "fire_class",
        "operator": "eq",
        "expected_value": "EI120",
        "target_attribute_code": "actuator_type",
        "allowed_values": [],
        "error_message": "Actuator type is required when fire class is EI120.",
        "is_active": True
    }
    client.post("/product-rules", json=rule_payload)

    valid_configuration_payload = {
        "product_family_id": family_id,
        "name": "Valid Config",
        "values": [
            {"attribute_code": "fire_class", "value": "EI120"},
            {"attribute_code": "actuator_type", "value": "reinforced"}
        ]
    }

    response = client.post("/product-configurations", json=valid_configuration_payload)

    assert response.status_code == 201