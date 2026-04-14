import type { Page } from "@playwright/test";

/**
 * Mock API data matching the backend seed structure.
 * Keeps E2E tests deterministic and independent of the backend.
 */

export const families = [
  {
    id: 1,
    code: "fire_damper_rectangular",
    name: "Fire Damper Rectangular",
    description: "Rectangular fire damper for HVAC systems",
    is_active: true,
    attributes: [
      {
        id: 1,
        code: "width",
        name: "Width",
        description: "Width of the damper",
        attribute_type: "integer",
        is_required: true,
        unit: "mm",
        min_int: 200,
        max_int: 2000,
        min_decimal: null,
        max_decimal: null,
        enum_options: [],
      },
      {
        id: 2,
        code: "height",
        name: "Height",
        description: "Height of the damper",
        attribute_type: "integer",
        is_required: true,
        unit: "mm",
        min_int: 200,
        max_int: 1500,
        min_decimal: null,
        max_decimal: null,
        enum_options: [],
      },
      {
        id: 3,
        code: "fire_class",
        name: "Fire Class",
        description: null,
        attribute_type: "enum",
        is_required: true,
        unit: null,
        min_int: null,
        max_int: null,
        min_decimal: null,
        max_decimal: null,
        enum_options: [
          { id: 1, value: "EI60", label: "EI60", sort_order: 1 },
          { id: 2, value: "EI120", label: "EI120", sort_order: 2 },
        ],
      },
      {
        id: 4,
        code: "actuator_type",
        name: "Actuator Type",
        description: null,
        attribute_type: "enum",
        is_required: false,
        unit: null,
        min_int: null,
        max_int: null,
        min_decimal: null,
        max_decimal: null,
        enum_options: [
          { id: 3, value: "standard", label: "Standard", sort_order: 1 },
          { id: 4, value: "reinforced", label: "Reinforced", sort_order: 2 },
        ],
      },
      {
        id: 5,
        code: "installation_type",
        name: "Installation Type",
        description: null,
        attribute_type: "enum",
        is_required: false,
        unit: null,
        min_int: null,
        max_int: null,
        min_decimal: null,
        max_decimal: null,
        enum_options: [
          { id: 5, value: "wall", label: "Wall", sort_order: 1 },
          { id: 6, value: "ceiling", label: "Ceiling", sort_order: 2 },
        ],
      },
    ],
  },
  {
    id: 2,
    code: "fire_damper_round",
    name: "Fire Damper Round",
    description: "Round fire damper for circular ducts",
    is_active: true,
    attributes: [
      {
        id: 6,
        code: "diameter",
        name: "Diameter",
        description: "Diameter of the damper",
        attribute_type: "integer",
        is_required: true,
        unit: "mm",
        min_int: 100,
        max_int: 1000,
        min_decimal: null,
        max_decimal: null,
        enum_options: [],
      },
      {
        id: 7,
        code: "fire_class",
        name: "Fire Class",
        description: null,
        attribute_type: "enum",
        is_required: true,
        unit: null,
        min_int: null,
        max_int: null,
        min_decimal: null,
        max_decimal: null,
        enum_options: [
          { id: 7, value: "EI60", label: "EI60", sort_order: 1 },
          { id: 8, value: "EI120", label: "EI120", sort_order: 2 },
        ],
      },
    ],
  },
  {
    id: 3,
    code: "multi_blade_fire_damper",
    name: "Multi Blade Fire Damper",
    description: "Multi-blade fire damper for large openings",
    is_active: true,
    attributes: [
      {
        id: 8,
        code: "width",
        name: "Width",
        description: null,
        attribute_type: "integer",
        is_required: true,
        unit: "mm",
        min_int: 300,
        max_int: 2500,
        min_decimal: null,
        max_decimal: null,
        enum_options: [],
      },
      {
        id: 9,
        code: "height",
        name: "Height",
        description: null,
        attribute_type: "integer",
        is_required: true,
        unit: "mm",
        min_int: 300,
        max_int: 2000,
        min_decimal: null,
        max_decimal: null,
        enum_options: [],
      },
      {
        id: 10,
        code: "fire_class",
        name: "Fire Class",
        description: null,
        attribute_type: "enum",
        is_required: true,
        unit: null,
        min_int: null,
        max_int: null,
        min_decimal: null,
        max_decimal: null,
        enum_options: [
          { id: 9, value: "EI60", label: "EI60", sort_order: 1 },
          { id: 10, value: "EI120", label: "EI120", sort_order: 2 },
        ],
      },
      {
        id: 11,
        code: "blade_type",
        name: "Blade Type",
        description: null,
        attribute_type: "enum",
        is_required: true,
        unit: null,
        min_int: null,
        max_int: null,
        min_decimal: null,
        max_decimal: null,
        enum_options: [
          { id: 11, value: "standard", label: "Standard", sort_order: 1 },
          { id: 12, value: "insulated", label: "Insulated", sort_order: 2 },
        ],
      },
    ],
  },
];

export const pricingResponse = {
  currency: "PLN",
  base_price: 500,
  surcharge_total: 0,
  total_price: 500,
  breakdown: [{ rule_name: "base_price", label: "Base price", amount: 500 }],
};

export const pricingWithSurcharge = {
  currency: "PLN",
  base_price: 500,
  surcharge_total: 275,
  total_price: 775,
  breakdown: [
    { rule_name: "base_price", label: "Base price", amount: 500 },
    { rule_name: "ei120_surcharge", label: "EI120 surcharge", amount: 200 },
    {
      rule_name: "large_width_surcharge",
      label: "Large width surcharge",
      amount: 75,
    },
  ],
};

export const orderCodeResponse = {
  order_code: "FDR-EI60-500x400",
};

export const technicalResponse = {
  family_code: "fire_damper_rectangular",
  results: [
    { name: "Effective area", code: "effective_area", value: 0.2, unit: "m²" },
  ],
};

export const savedConfiguration = {
  id: 42,
  product_family_id: 1,
  product_family_code: "fire_damper_rectangular",
  name: "Fire Damper Rectangular — 2026-04-14",
  status: "active",
};

export const quoteResponse = {
  id: 1,
  product_configuration_id: 42,
  quote_number: "Q-00000001",
  status: "generated",
  currency: "PLN",
  base_price: 500,
  surcharge_total: 0,
  total_price: 500,
  configuration_snapshot: {},
  pricing_snapshot: {},
  created_at: "2026-04-14T12:00:00Z",
};

/**
 * Sets up API route mocking for all configurator endpoints.
 * Call this in test.beforeEach to isolate tests from the backend.
 */
export async function mockApiRoutes(
  page: Page,
  overrides?: {
    pricing?: typeof pricingResponse;
    orderCode?: typeof orderCodeResponse;
    technical?: typeof technicalResponse;
  }
) {
  await page.route("**/api/product-families", (route) =>
    route.fulfill({ json: families })
  );

  await page.route("**/api/product-configurations/calculate-price", (route) =>
    route.fulfill({ json: overrides?.pricing ?? pricingResponse })
  );

  await page.route(
    "**/api/product-configurations/generate-order-code",
    (route) => route.fulfill({ json: overrides?.orderCode ?? orderCodeResponse })
  );

  await page.route(
    "**/api/product-configurations/calculate-technical",
    (route) => route.fulfill({ json: overrides?.technical ?? technicalResponse })
  );

  await page.route("**/api/product-configurations", (route) => {
    if (route.request().method() === "POST") {
      return route.fulfill({ status: 201, json: savedConfiguration });
    }
    return route.continue();
  });

  await page.route("**/api/product-quotes", (route) => {
    if (route.request().method() === "POST") {
      return route.fulfill({ status: 201, json: quoteResponse });
    }
    return route.continue();
  });
}
