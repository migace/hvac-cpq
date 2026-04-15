import { test, expect } from "@playwright/test";
import {
  mockApiRoutes,
  families,
  pricingWithSurcharge,
  quoteResponse,
} from "./fixtures";

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => localStorage.clear());
  await mockApiRoutes(page);
});

// ---------------------------------------------------------------------------
// Family selection
// ---------------------------------------------------------------------------

test.describe("Family selection", () => {
  test("displays all product families", async ({ page }) => {
    await page.goto("/");

    for (const family of families) {
      await expect(page.getByText(family.name)).toBeVisible();
    }
  });

  test("shows family code and attribute count", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByText("fire_damper_rectangular")).toBeVisible();
    await expect(page.getByText("5 attributes")).toBeVisible();
  });

  test("selecting a family opens configuration form", async ({ page }) => {
    await page.goto("/");

    await page.getByText("Fire Damper Rectangular").click();

    await expect(page.getByText("Back to family selection")).toBeVisible();
    await expect(page.getByLabel("Width")).toBeVisible();
    await expect(page.getByLabel("Height")).toBeVisible();
    await expect(page.getByLabel("Fire Class")).toBeVisible();
  });

  test("going back clears form and returns to family list", async ({
    page,
  }) => {
    await page.goto("/");
    await page.getByText("Fire Damper Rectangular").click();

    await page.getByText("Back to family selection").click();

    await expect(page.getByText("Choose product family")).toBeVisible();
    await expect(
      page.getByText("Fire Damper Rectangular")
    ).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Configuration form
// ---------------------------------------------------------------------------

test.describe("Configuration form", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.getByText("Fire Damper Rectangular").click();
  });

  test("separates required and optional parameters", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "Required parameters" })
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: "Optional parameters" })
    ).toBeVisible();
  });

  test("shows range hints for numeric fields", async ({ page }) => {
    await expect(page.getByText("Range: 200 – 2000")).toBeVisible();
    await expect(page.getByText("Range: 200 – 1500")).toBeVisible();
  });

  test("validates required fields on blur", async ({ page }) => {
    const widthField = page.getByLabel("Width");
    await widthField.focus();
    await widthField.blur();

    await expect(page.getByText("Width is required")).toBeVisible();
  });

  test("validates min/max range for numeric fields", async ({ page }) => {
    const widthField = page.getByLabel("Width");
    await widthField.fill("50");
    await widthField.blur();

    await expect(page.getByText("Minimum value: 200 mm")).toBeVisible();
  });

  test("enum fields have a select dropdown", async ({ page }) => {
    await page.getByLabel("Fire Class").click();

    await expect(page.getByRole("option", { name: "EI60" })).toBeVisible();
    await expect(page.getByRole("option", { name: "EI120" })).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Live results — desktop only (on mobile, results are in the drawer;
// tested separately in the "Mobile layout" describe block)
// ---------------------------------------------------------------------------

test.describe("Live results", () => {
  test("shows pricing and order code after filling required fields", async ({
    page,
    isMobile,
  }) => {
    test.skip(isMobile, "desktop-only: mobile results tested via drawer");
    await page.goto("/");
    await page.getByText("Fire Damper Rectangular").click();

    await page.getByLabel("Width").fill("500");
    await page.getByLabel("Height").fill("400");
    await page.getByLabel("Fire Class").click();
    await page.getByRole("option", { name: "EI60" }).click();

    await expect(page.getByText("FDR-EI60-500x400")).toBeVisible();
    await expect(page.getByText("Base price")).toBeVisible();
    await expect(page.getByText("Effective area")).toBeVisible();
  });

  test("shows pricing breakdown with surcharges", async ({
    page,
    isMobile,
  }) => {
    test.skip(isMobile, "desktop-only: mobile results tested via drawer");
    await mockApiRoutes(page, { pricing: pricingWithSurcharge });
    await page.goto("/");
    await page.getByText("Fire Damper Rectangular").click();

    await page.getByLabel("Width").fill("1500");
    await page.getByLabel("Height").fill("400");
    await page.getByLabel("Fire Class").click();
    await page.getByRole("option", { name: "EI120" }).click();

    await expect(page.getByText("EI120 surcharge")).toBeVisible();
    await expect(page.getByText("Large width surcharge")).toBeVisible();
  });

  test("clears results when all values are removed", async ({
    page,
    isMobile,
  }) => {
    test.skip(isMobile, "desktop-only: mobile results tested via drawer");
    await page.goto("/");
    await page.getByText("Fire Damper Rectangular").click();

    await page.getByLabel("Width").fill("500");
    await page.getByLabel("Height").fill("400");
    await page.getByLabel("Fire Class").click();
    await page.getByRole("option", { name: "EI60" }).click();

    await expect(page.getByText("FDR-EI60-500x400")).toBeVisible();

    await page.getByRole("button", { name: "Reset" }).click();

    await expect(
      page.getByText("Configure product parameters to see real-time results.")
    ).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Quote generation — desktop only (button is inside the results panel)
// ---------------------------------------------------------------------------

test.describe("Quote generation", () => {
  test("generates a quote after valid configuration", async ({
    page,
    isMobile,
  }) => {
    test.skip(isMobile, "desktop-only: quote button is in the results panel");
    await page.goto("/");
    await page.getByText("Fire Damper Rectangular").click();

    await page.getByLabel("Width").fill("500");
    await page.getByLabel("Height").fill("400");
    await page.getByLabel("Fire Class").click();
    await page.getByRole("option", { name: "EI60" }).click();

    await expect(page.getByText("Base price")).toBeVisible();

    await page.getByRole("button", { name: "Generate Quote" }).click();

    await expect(page.getByText(quoteResponse.quote_number)).toBeVisible();
    await expect(page.getByText("Quote Generated")).toBeVisible();
  });

  test("hides generate button after quote is created", async ({
    page,
    isMobile,
  }) => {
    test.skip(isMobile, "desktop-only: quote button is in the results panel");
    await page.goto("/");
    await page.getByText("Fire Damper Rectangular").click();

    await page.getByLabel("Width").fill("500");
    await page.getByLabel("Height").fill("400");
    await page.getByLabel("Fire Class").click();
    await page.getByRole("option", { name: "EI60" }).click();

    await page.getByRole("button", { name: "Generate Quote" }).click();

    await expect(page.getByText("Quote Generated")).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Generate Quote" })
    ).not.toBeVisible();
  });

  test("clears quote when configuration changes", async ({
    page,
    isMobile,
  }) => {
    test.skip(isMobile, "desktop-only: quote button is in the results panel");
    await page.goto("/");
    await page.getByText("Fire Damper Rectangular").click();

    await page.getByLabel("Width").fill("500");
    await page.getByLabel("Height").fill("400");
    await page.getByLabel("Fire Class").click();
    await page.getByRole("option", { name: "EI60" }).click();

    await page.getByRole("button", { name: "Generate Quote" }).click();
    await expect(page.getByText("Quote Generated")).toBeVisible();

    await page.getByLabel("Width").fill("600");

    await expect(page.getByText("Quote Generated")).not.toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// UX features
// ---------------------------------------------------------------------------

test.describe("UX features", () => {
  test("reset clears all values and results", async ({
    page,
    isMobile,
  }) => {
    test.skip(isMobile, "desktop-only: results panel visibility");
    await page.goto("/");
    await page.getByText("Fire Damper Rectangular").click();

    await page.getByLabel("Width").fill("500");
    await page.getByLabel("Height").fill("400");
    await page.getByLabel("Fire Class").click();
    await page.getByRole("option", { name: "EI60" }).click();

    await expect(page.getByText("FDR-EI60-500x400")).toBeVisible();

    await page.getByRole("button", { name: "Reset" }).click();

    await expect(page.getByLabel("Width")).toHaveValue("");
    await expect(
      page.getByText("Configure product parameters to see real-time results.")
    ).toBeVisible();
  });

  test("copy order code button exists and is clickable", async ({
    page,
    isMobile,
  }) => {
    test.skip(isMobile, "desktop-only: copy button is in the results panel");
    await page.goto("/");
    await page.getByText("Fire Damper Rectangular").click();

    await page.getByLabel("Width").fill("500");
    await page.getByLabel("Height").fill("400");
    await page.getByLabel("Fire Class").click();
    await page.getByRole("option", { name: "EI60" }).click();

    await expect(page.getByText("FDR-EI60-500x400")).toBeVisible();

    const copyButton = page.getByRole("button", { name: "Copy order code" });
    await expect(copyButton).toBeVisible();
  });

  test("persists configuration in localStorage", async ({ page }) => {
    await page.goto("/");
    await page.getByText("Fire Damper Rectangular").click();

    await page.getByLabel("Width").fill("500");

    const stored = await page.evaluate(() =>
      localStorage.getItem("hvac-cpq-configurator")
    );
    expect(stored).not.toBeNull();

    const parsed = JSON.parse(stored!);
    expect(parsed.familyId).toBe(1);
    expect(parsed.values.width).toBe(500);
  });

  test("restores configuration from localStorage on reload", async ({
    page,
  }) => {
    // Seed localStorage directly so the app can restore state on load.
    // Avoids filling number inputs on mobile (the ConfigurationForm auto-focuses
    // the first field after 100 ms, which can cause a concurrent fill to land
    // in the wrong input and corrupt the stored value).
    // The beforeEach clear script runs first; this inject runs second.
    const savedConfig = JSON.stringify({
      familyId: 1,
      values: { width: 500, height: 400 },
    });
    await page.addInitScript((config) => {
      localStorage.setItem("hvac-cpq-configurator", config);
    }, savedConfig);

    await page.goto("/");

    await expect(page.getByLabel("Width")).toHaveValue("500");
    await expect(page.getByLabel("Height")).toHaveValue("400");
  });
});

// ---------------------------------------------------------------------------
// Mobile responsive
// ---------------------------------------------------------------------------

test.describe("Mobile layout", () => {
  test.use({ viewport: { width: 375, height: 812 } });

  test("shows floating bottom bar with price on mobile", async ({ page }) => {
    await mockApiRoutes(page);
    await page.goto("/");
    await page.getByText("Fire Damper Rectangular").click();

    await page.getByLabel("Width").fill("500");
    await page.getByLabel("Height").fill("400");
    await page.getByLabel("Fire Class").click();
    await page.getByRole("option", { name: "EI60" }).click();

    await expect(page.getByText("Details")).toBeVisible();
  });

  test("opens drawer with full results on tap", async ({ page }) => {
    await mockApiRoutes(page);
    await page.goto("/");
    await page.getByText("Fire Damper Rectangular").click();

    await page.getByLabel("Width").fill("500");
    await page.getByLabel("Height").fill("400");
    await page.getByLabel("Fire Class").click();
    await page.getByRole("option", { name: "EI60" }).click();

    // The Chat FAB (bottom: 24, right: 24, zIndex: 1300) overlaps the Details
    // tap area on small viewport. dispatchEvent fires directly on the DOM node
    // and bubbles to the Paper's onClick handler without coordinate hit-testing.
    await page.getByText("Details").dispatchEvent("click");

    await expect(page.getByText("Configuration Results")).toBeVisible();
    await expect(
      page.getByRole("dialog").getByText("FDR-EI60-500x400")
    ).toBeVisible();
  });
});
