"""Agent quality evaluation tests.

These tests define golden test cases that validate the agent's tool selection
and response quality. They test the tool layer directly (without calling OpenAI)
to verify that given a specific user intent, the correct tools produce the
expected data.

This approach allows CI-friendly evaluation without API costs. For full
end-to-end LLM evaluation (testing prompt quality and model behavior),
see the docstring at the bottom of this file.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.agent.tools import AgentTools


def _seed_full_catalog(client: TestClient) -> dict[str, int]:
    """Seed all three demo families and return a code->id mapping."""
    families = {}

    # Rectangular
    resp = client.post("/product-families", json={
        "code": "fire_damper_rectangular",
        "name": "Fire Damper Rectangular",
        "description": "Rectangular fire damper for standard HVAC ducts",
        "attributes": [
            {"code": "width", "name": "Width", "attribute_type": "integer",
             "is_required": True, "unit": "mm", "min_int": 200, "max_int": 2000,
             "enum_options": []},
            {"code": "height", "name": "Height", "attribute_type": "integer",
             "is_required": True, "unit": "mm", "min_int": 200, "max_int": 1500,
             "enum_options": []},
            {"code": "fire_class", "name": "Fire Class", "attribute_type": "enum",
             "is_required": True, "enum_options": [
                 {"value": "EI60", "label": "EI60", "sort_order": 1},
                 {"value": "EI120", "label": "EI120", "sort_order": 2}]},
            {"code": "actuator_type", "name": "Actuator Type", "attribute_type": "enum",
             "is_required": False, "enum_options": [
                 {"value": "standard", "label": "Standard", "sort_order": 1},
                 {"value": "reinforced", "label": "Reinforced", "sort_order": 2}]},
        ],
    })
    families["fire_damper_rectangular"] = resp.json()["id"]

    # Round
    resp = client.post("/product-families", json={
        "code": "fire_damper_round",
        "name": "Fire Damper Round",
        "description": "Round fire damper for circular ducts",
        "attributes": [
            {"code": "diameter", "name": "Diameter", "attribute_type": "integer",
             "is_required": True, "unit": "mm", "min_int": 100, "max_int": 1000,
             "enum_options": []},
            {"code": "fire_class", "name": "Fire Class", "attribute_type": "enum",
             "is_required": True, "enum_options": [
                 {"value": "EI60", "label": "EI60", "sort_order": 1},
                 {"value": "EI120", "label": "EI120", "sort_order": 2}]},
        ],
    })
    families["fire_damper_round"] = resp.json()["id"]

    # Pricing for rectangular
    fid = families["fire_damper_rectangular"]
    client.post("/product-pricing-rules", json={
        "product_family_id": fid, "name": "Base", "pricing_rule_type": "base_price",
        "amount": "500.00", "currency": "PLN", "label": "Base price", "is_active": True,
    })
    client.post("/product-pricing-rules", json={
        "product_family_id": fid, "name": "EI120", "pricing_rule_type": "fixed_surcharge",
        "if_attribute_code": "fire_class", "operator": "eq", "expected_value": "EI120",
        "amount": "200.00", "currency": "PLN", "label": "EI120 surcharge", "is_active": True,
    })

    # Business rule for rectangular
    client.post("/product-rules", json={
        "product_family_id": fid, "name": "EI120 requires actuator",
        "rule_type": "requires_attribute",
        "if_attribute_code": "fire_class", "operator": "eq", "expected_value": "EI120",
        "target_attribute_code": "actuator_type",
        "error_message": "EI120 requires an actuator type.", "is_active": True,
    })

    # Pricing for round
    rid = families["fire_damper_round"]
    client.post("/product-pricing-rules", json={
        "product_family_id": rid, "name": "Base", "pricing_rule_type": "base_price",
        "amount": "450.00", "currency": "PLN", "label": "Base price", "is_active": True,
    })

    return families


class TestAgentEvaluation:
    """Golden test cases that validate the tool layer produces correct results
    for common user intents. Each test simulates a step of the agent's
    tool-calling workflow."""

    def test_scenario_find_rectangular_ei120(
        self, client: TestClient, db_session: Session,
    ) -> None:
        """User intent: 'I need an EI120 rectangular fire damper 400x300'

        Expected agent workflow:
        1. search_products(shape=rectangular, fire_class=EI120) -> finds rectangular family
        2. get_family_details(family_id=...) -> gets rules and pricing
        3. calculate_price(family_id=..., config) -> returns price with EI120 surcharge
        """
        _seed_full_catalog(client)
        tools = AgentTools(db_session)

        # Step 1: Search
        search_result = tools.search_products(shape="rectangular", fire_class="EI120")
        assert search_result["total"] == 1
        found_family = search_result["families"][0]
        assert found_family["code"] == "fire_damper_rectangular"

        # Step 2: Get details
        details = tools.get_family_details(family_id=found_family["id"])
        assert "business_rules" in details
        assert any("EI120" in r["description"] for r in details["business_rules"])

        # Step 3: Calculate price (with actuator because EI120 requires it)
        config = {
            "width": 400,
            "height": 300,
            "fire_class": "EI120",
            "actuator_type": "reinforced",
        }
        price = tools.calculate_price(
            family_id=found_family["id"],
            configuration=config,
        )
        assert price["currency"] == "PLN"
        assert price["total_price"] == "700.00"  # 500 base + 200 EI120

    def test_scenario_compare_fire_classes(
        self, client: TestClient, db_session: Session,
    ) -> None:
        """User intent: 'What is the price difference between EI60 and EI120?'

        Expected agent workflow:
        1. search_products() -> find families
        2. calculate_price for EI60
        3. calculate_price for EI120
        4. Compare results
        """
        families = _seed_full_catalog(client)
        fid = families["fire_damper_rectangular"]
        tools = AgentTools(db_session)

        price_ei60 = tools.calculate_price(
            family_id=fid,
            configuration={"width": 400, "height": 300, "fire_class": "EI60"},
        )
        price_ei120 = tools.calculate_price(
            family_id=fid,
            configuration={
                "width": 400, "height": 300, "fire_class": "EI120",
                "actuator_type": "reinforced",
            },
        )

        assert float(price_ei120["total_price"]) > float(price_ei60["total_price"])
        difference = float(price_ei120["total_price"]) - float(price_ei60["total_price"])
        assert abs(difference - 200.0) < 0.01  # EI120 surcharge

    def test_scenario_invalid_config_explains_why(
        self, client: TestClient, db_session: Session,
    ) -> None:
        """User intent: 'Configure EI120 rectangular 400x300'
        (missing actuator — rule violation)

        Expected: validate_configuration returns clear error about actuator.
        """
        families = _seed_full_catalog(client)
        fid = families["fire_damper_rectangular"]
        tools = AgentTools(db_session)

        result = tools.validate_configuration(
            family_id=fid,
            configuration={
                "width": 400,
                "height": 300,
                "fire_class": "EI120",
            },
        )
        assert result["valid"] is False
        assert "actuator" in result["message"].lower()

    def test_scenario_technical_specs(
        self, client: TestClient, db_session: Session,
    ) -> None:
        """User intent: 'What is the effective area of a 400x300 damper?'

        Expected: calculate_technical_params returns 0.12 m2.
        """
        families = _seed_full_catalog(client)
        fid = families["fire_damper_rectangular"]
        tools = AgentTools(db_session)

        result = tools.calculate_technical_params(
            family_id=fid,
            configuration={
                "width": 400,
                "height": 300,
                "fire_class": "EI60",
            },
        )
        assert result["results"][0]["value"] == "0.1200"
        assert result["results"][0]["unit"] == "m2"

    def test_scenario_full_recommendation_flow(
        self, client: TestClient, db_session: Session,
    ) -> None:
        """User intent: 'Recommend a product for a 500mm round duct with EI60'

        Expected full workflow:
        1. search_products(shape=round, fire_class=EI60) -> round family
        2. get_family_details -> learn about attributes
        3. validate_configuration -> valid
        4. calculate_price -> 450 PLN base
        5. calculate_technical_params -> effective area
        """
        _seed_full_catalog(client)
        tools = AgentTools(db_session)

        # Step 1: Search
        search = tools.search_products(shape="round", fire_class="EI60")
        assert search["total"] == 1
        family = search["families"][0]

        # Step 2: Details
        details = tools.get_family_details(family_id=family["id"])
        required_attrs = [a for a in details["attributes"] if a["is_required"]]
        assert len(required_attrs) == 2  # diameter, fire_class

        config = {"diameter": 500, "fire_class": "EI60"}

        # Step 3: Validate
        validation = tools.validate_configuration(
            family_id=family["id"],
            configuration=config,
        )
        assert validation["valid"] is True

        # Step 4: Price
        price = tools.calculate_price(
            family_id=family["id"],
            configuration=config,
        )
        assert price["total_price"] == "450.00"

        # Step 5: Technical
        tech = tools.calculate_technical_params(
            family_id=family["id"],
            configuration=config,
        )
        assert len(tech["results"]) >= 1


"""
LLM-as-Judge Evaluation (for manual / CI-with-API-key runs)

For full end-to-end evaluation of the agent's prompt quality and
response accuracy, the following approach is recommended:

1. Define golden test cases with:
   - user_query: natural language input
   - expected_tools: list of tools the agent should call
   - expected_in_response: keywords that must appear in the final answer
   - expected_not_in_response: keywords that must NOT appear

2. Run the agent with a real API key and capture:
   - which tools were called (from SSE events)
   - the final text response

3. Score using deterministic checks:
   - tool_precision: did the agent call the right tools?
   - keyword_recall: did the response contain expected information?
   - no_hallucination: did the response avoid forbidden keywords?

4. Optionally use LLM-as-judge for semantic evaluation:
   - Send the response + expected behavior to a second LLM
   - Ask it to rate accuracy, helpfulness, and correctness on 1-5 scale

Example golden cases:

EVAL_CASES = [
    {
        "query": "I need an EI120 rectangular fire damper 400x300",
        "expected_tools": ["search_products", "get_family_details", "calculate_price"],
        "expected_in_response": ["fire_damper_rectangular", "EI120", "400", "300", "PLN"],
        "expected_not_in_response": ["round"],
    },
    {
        "query": "What is the price difference between EI60 and EI120 for a 600x400?",
        "expected_tools": ["search_products", "calculate_price"],
        "expected_in_response": ["200", "surcharge"],
    },
    {
        "query": "Show me all available product families",
        "expected_tools": ["search_products"],
        "expected_in_response": ["rectangular", "round"],
    },
]

This evaluation framework can be extended with:
- Latency budgets (agent should respond within N seconds)
- Cost budgets (agent should not exceed N tokens per query)
- Regression detection (compare scores across model versions)
"""
