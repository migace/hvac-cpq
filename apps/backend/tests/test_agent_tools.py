"""Tests for AI agent tools — validates that each tool correctly wraps
the underlying domain services and returns structured data."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.agent.tools import AgentTools

# ── Helpers ──────────────────────────────────────────────────────────

def _seed_family_with_rules(client: TestClient) -> int:
    """Creates a rectangular fire damper family with attributes, rules, and pricing."""
    family_payload = {
        "code": "fire_damper_rectangular",
        "name": "Fire Damper Rectangular",
        "description": "Rectangular fire damper for HVAC ducts",
        "attributes": [
            {
                "code": "width",
                "name": "Width",
                "attribute_type": "integer",
                "is_required": True,
                "unit": "mm",
                "min_int": 200,
                "max_int": 2000,
                "enum_options": [],
            },
            {
                "code": "height",
                "name": "Height",
                "attribute_type": "integer",
                "is_required": True,
                "unit": "mm",
                "min_int": 200,
                "max_int": 1500,
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
            {
                "code": "actuator_type",
                "name": "Actuator Type",
                "attribute_type": "enum",
                "is_required": False,
                "enum_options": [
                    {"value": "standard", "label": "Standard", "sort_order": 1},
                    {"value": "reinforced", "label": "Reinforced", "sort_order": 2},
                ],
            },
        ],
    }

    resp = client.post("/product-families", json=family_payload)
    assert resp.status_code == 201
    family_id = resp.json()["id"]

    # Business rule: EI120 requires actuator
    client.post("/product-rules", json={
        "product_family_id": family_id,
        "name": "EI120 requires actuator",
        "rule_type": "requires_attribute",
        "if_attribute_code": "fire_class",
        "operator": "eq",
        "expected_value": "EI120",
        "target_attribute_code": "actuator_type",
        "error_message": "EI120 fire class requires an actuator type to be specified.",
        "is_active": True,
    })

    # Pricing rules
    client.post("/product-pricing-rules", json={
        "product_family_id": family_id,
        "name": "Base price",
        "pricing_rule_type": "base_price",
        "amount": "500.00",
        "currency": "PLN",
        "label": "Base price",
        "is_active": True,
    })

    client.post("/product-pricing-rules", json={
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
    })

    return family_id


def _seed_round_family(client: TestClient) -> int:
    """Creates a round fire damper family."""
    family_payload = {
        "code": "fire_damper_round",
        "name": "Fire Damper Round",
        "description": "Round fire damper for circular ducts",
        "attributes": [
            {
                "code": "diameter",
                "name": "Diameter",
                "attribute_type": "integer",
                "is_required": True,
                "unit": "mm",
                "min_int": 100,
                "max_int": 1000,
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
    resp = client.post("/product-families", json=family_payload)
    assert resp.status_code == 201
    return resp.json()["id"]


# ── search_products tool tests ───────────────────────────────────────

class TestSearchProducts:
    def test_search_returns_all_families(self, client: TestClient, db_session: Session) -> None:
        _seed_family_with_rules(client)
        _seed_round_family(client)

        tools = AgentTools(db_session)
        result = tools.search_products()
        assert result["total"] == 2
        codes = {f["code"] for f in result["families"]}
        assert codes == {"fire_damper_rectangular", "fire_damper_round"}

    def test_search_filters_by_shape_rectangular(
        self, client: TestClient, db_session: Session,
    ) -> None:
        _seed_family_with_rules(client)
        _seed_round_family(client)

        tools = AgentTools(db_session)
        result = tools.search_products(shape="rectangular")
        assert result["total"] == 1
        assert result["families"][0]["code"] == "fire_damper_rectangular"

    def test_search_filters_by_shape_round(self, client: TestClient, db_session: Session) -> None:
        _seed_family_with_rules(client)
        _seed_round_family(client)

        tools = AgentTools(db_session)
        result = tools.search_products(shape="round")
        assert result["total"] == 1
        assert result["families"][0]["code"] == "fire_damper_round"

    def test_search_filters_by_fire_class(self, client: TestClient, db_session: Session) -> None:
        _seed_family_with_rules(client)

        tools = AgentTools(db_session)
        result = tools.search_products(fire_class="EI120")
        assert result["total"] == 1
        assert result["families"][0]["code"] == "fire_damper_rectangular"

    def test_search_returns_empty_for_no_match(
        self, client: TestClient, db_session: Session,
    ) -> None:
        _seed_family_with_rules(client)

        tools = AgentTools(db_session)
        result = tools.search_products(query="nonexistent product")
        assert result["total"] == 0


# ── get_family_details tool tests ────────────────────────────────────

class TestGetFamilyDetails:
    def test_returns_full_details_with_rules(self, client: TestClient, db_session: Session) -> None:
        family_id = _seed_family_with_rules(client)

        tools = AgentTools(db_session)
        result = tools.get_family_details(family_id=family_id)

        assert result["code"] == "fire_damper_rectangular"
        assert len(result["attributes"]) == 4
        assert "business_rules" in result
        assert len(result["business_rules"]) >= 1
        assert "pricing_rules" in result
        assert len(result["pricing_rules"]) >= 2

    def test_returns_error_for_missing_family(self, db_session: Session) -> None:
        tools = AgentTools(db_session)
        result = tools.get_family_details(family_id=99999)
        assert "error" in result


# ── calculate_price tool tests ───────────────────────────────────────

class TestCalculatePrice:
    def test_calculates_price_with_surcharge(self, client: TestClient, db_session: Session) -> None:
        family_id = _seed_family_with_rules(client)

        tools = AgentTools(db_session)
        result = tools.calculate_price(
            family_id=family_id,
            configuration={
                "width": 400,
                "height": 300,
                "fire_class": "EI120",
                "actuator_type": "reinforced",
            },
        )

        assert result["currency"] == "PLN"
        assert result["base_price"] == "500.00"
        assert result["total_price"] == "700.00"
        assert len(result["breakdown"]) == 2

    def test_calculates_base_price_only(self, client: TestClient, db_session: Session) -> None:
        family_id = _seed_family_with_rules(client)

        tools = AgentTools(db_session)
        result = tools.calculate_price(
            family_id=family_id,
            configuration={
                "width": 400,
                "height": 300,
                "fire_class": "EI60",
            },
        )

        assert result["total_price"] == "500.00"
        assert result["surcharge_total"] == "0.00"

    def test_returns_error_for_invalid_family(self, db_session: Session) -> None:
        tools = AgentTools(db_session)
        result = tools.calculate_price(
            family_id=99999,
            configuration={"width": 400},
        )
        assert "error" in result


# ── validate_configuration tool tests ────────────────────────────────

class TestValidateConfiguration:
    def test_valid_configuration(self, client: TestClient, db_session: Session) -> None:
        family_id = _seed_family_with_rules(client)

        tools = AgentTools(db_session)
        result = tools.validate_configuration(
            family_id=family_id,
            configuration={
                "width": 400,
                "height": 300,
                "fire_class": "EI60",
            },
        )
        assert result["valid"] is True

    def test_invalid_configuration_missing_required(
        self, client: TestClient, db_session: Session,
    ) -> None:
        family_id = _seed_family_with_rules(client)

        tools = AgentTools(db_session)
        result = tools.validate_configuration(
            family_id=family_id,
            configuration={"width": 400},
        )
        assert result["valid"] is False
        assert "missing" in result["message"].lower() or "required" in result["message"].lower()

    def test_invalid_configuration_rule_violation(
        self, client: TestClient, db_session: Session,
    ) -> None:
        family_id = _seed_family_with_rules(client)

        tools = AgentTools(db_session)
        result = tools.validate_configuration(
            family_id=family_id,
            configuration={
                "width": 400,
                "height": 300,
                "fire_class": "EI120",
            },
        )
        assert result["valid"] is False
        assert "actuator" in result["message"].lower()


# ── generate_order_code tool tests ───────────────────────────────────

class TestGenerateOrderCode:
    def test_generates_order_code(self, client: TestClient, db_session: Session) -> None:
        family_id = _seed_family_with_rules(client)

        tools = AgentTools(db_session)
        result = tools.generate_order_code(
            family_id=family_id,
            configuration={
                "width": 400,
                "height": 300,
                "fire_class": "EI120",
                "actuator_type": "reinforced",
            },
        )
        assert "order_code" in result
        assert "FDR" in result["order_code"]
        assert "400x300" in result["order_code"]


# ── calculate_technical_params tool tests ────────────────────────────

class TestCalculateTechnicalParams:
    def test_calculates_effective_area_rectangular(
        self, client: TestClient, db_session: Session,
    ) -> None:
        family_id = _seed_family_with_rules(client)

        tools = AgentTools(db_session)
        result = tools.calculate_technical_params(
            family_id=family_id,
            configuration={
                "width": 400,
                "height": 300,
                "fire_class": "EI60",
            },
        )
        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["code"] == "effective_area"
        assert result["results"][0]["unit"] == "m2"
        # 400 * 300 / 1_000_000 = 0.12
        assert result["results"][0]["value"] == "0.1200"

    def test_calculates_effective_area_round(self, client: TestClient, db_session: Session) -> None:
        family_id = _seed_round_family(client)

        tools = AgentTools(db_session)
        result = tools.calculate_technical_params(
            family_id=family_id,
            configuration={
                "diameter": 500,
                "fire_class": "EI60",
            },
        )
        assert "results" in result
        assert result["results"][0]["code"] == "effective_area"
