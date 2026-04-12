from fastapi.testclient import TestClient


def _create_family(client: TestClient, code: str = "test_family") -> int:
    family_payload = {
        "code": code,
        "name": f"Test Family {code}",
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
    response = client.post("/product-families", json=family_payload)
    assert response.status_code == 201
    return response.json()["id"]


def _create_configuration(
    client: TestClient, family_id: int, name: str = "Test Config"
) -> dict:
    payload = {
        "product_family_id": family_id,
        "name": name,
        "values": [
            {"attribute_code": "width", "value": 1200},
            {"attribute_code": "height", "value": 800},
            {"attribute_code": "fire_class", "value": "EI60"},
        ],
    }
    response = client.post("/product-configurations", json=payload)
    assert response.status_code == 201
    return response.json()


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


def test_list_product_configurations_returns_200(client: TestClient) -> None:
    response = client.get("/product-configurations")
    assert response.status_code == 200


def test_list_product_configurations_returns_empty_list_when_none_exist(
    client: TestClient,
) -> None:
    response = client.get("/product-configurations")
    assert response.status_code == 200
    assert response.json() == []


def test_list_product_configurations_returns_created_configurations(
    client: TestClient,
) -> None:
    family_id = _create_family(client, code="list_family")
    _create_configuration(client, family_id, name="Config A")
    _create_configuration(client, family_id, name="Config B")

    response = client.get("/product-configurations")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2

    names = [item["name"] for item in data]
    assert "Config A" in names
    assert "Config B" in names

    for item in data:
        assert item["product_family_id"] == family_id
        assert item["product_family_code"] == "list_family"
        assert item["status"] == "draft"
        assert item["values_count"] == 3


def test_list_product_configurations_ordered_newest_first(
    client: TestClient,
) -> None:
    family_id = _create_family(client, code="order_family")
    _create_configuration(client, family_id, name="First")
    _create_configuration(client, family_id, name="Second")
    _create_configuration(client, family_id, name="Third")

    response = client.get("/product-configurations")
    data = response.json()

    assert data[0]["name"] == "Third"
    assert data[1]["name"] == "Second"
    assert data[2]["name"] == "First"


def test_list_product_configurations_does_not_return_values(
    client: TestClient,
) -> None:
    family_id = _create_family(client, code="no_values_family")
    _create_configuration(client, family_id)

    response = client.get("/product-configurations")
    data = response.json()

    assert len(data) == 1
    assert "values" not in data[0]
    assert "values_count" in data[0]