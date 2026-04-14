"""OpenAI function-calling tool definitions.

These JSON schemas are sent to the OpenAI API so the model knows what tools
it can call, what parameters each tool expects, and what each tool does.
"""

TOOL_DEFINITIONS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": (
                "Search available HVAC product families. "
                "Use this to find products matching user criteria like shape, fire class, or keywords. "
                "Returns a list of matching product families with their attributes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Free-text search query to match against product names and descriptions.",
                    },
                    "fire_class": {
                        "type": "string",
                        "description": "Fire resistance class filter, e.g. 'EI60' or 'EI120'.",
                    },
                    "shape": {
                        "type": "string",
                        "description": "Product shape filter: 'rectangular', 'round', or 'multi_blade'.",
                        "enum": ["rectangular", "round", "multi_blade"],
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_family_details",
            "description": (
                "Get full details of a specific product family including all attributes, "
                "business validation rules, and pricing rules. "
                "Use this after search_products to get complete information about a specific family."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "family_id": {
                        "type": "integer",
                        "description": "The ID of the product family to retrieve.",
                    },
                },
                "required": ["family_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_price",
            "description": (
                "Calculate the price for a specific product configuration. "
                "Requires a family ID and a configuration object mapping attribute codes to values. "
                "Returns pricing breakdown with base price, surcharges, and total."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "family_id": {
                        "type": "integer",
                        "description": "The ID of the product family.",
                    },
                    "configuration": {
                        "type": "object",
                        "description": (
                            "Configuration values as key-value pairs where keys are attribute codes "
                            "and values are the selected values. "
                            "Example: {\"width\": 400, \"height\": 300, \"fire_class\": \"EI120\"}"
                        ),
                    },
                },
                "required": ["family_id", "configuration"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "validate_configuration",
            "description": (
                "Check whether a product configuration is valid according to business rules. "
                "Returns validation result with error messages if invalid."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "family_id": {
                        "type": "integer",
                        "description": "The ID of the product family.",
                    },
                    "configuration": {
                        "type": "object",
                        "description": "Configuration values as key-value pairs.",
                    },
                },
                "required": ["family_id", "configuration"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_order_code",
            "description": (
                "Generate a unique order code for a valid product configuration. "
                "The configuration must be valid before generating an order code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "family_id": {
                        "type": "integer",
                        "description": "The ID of the product family.",
                    },
                    "configuration": {
                        "type": "object",
                        "description": "Configuration values as key-value pairs.",
                    },
                },
                "required": ["family_id", "configuration"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_technical_params",
            "description": (
                "Calculate technical parameters (e.g. effective area) for a product configuration. "
                "Useful when the user asks about technical specifications."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "family_id": {
                        "type": "integer",
                        "description": "The ID of the product family.",
                    },
                    "configuration": {
                        "type": "object",
                        "description": "Configuration values as key-value pairs.",
                    },
                },
                "required": ["family_id", "configuration"],
                "additionalProperties": False,
            },
        },
    },
]
