import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import type {
  ProductFamily,
  AttributeDefinition,
  ConfigurationPayload,
  PricingResponse,
  TechnicalCalculationResponse,
  QuoteResponse,
  ApiError,
} from "../types";
import {
  fetchFamilies,
  calculatePrice,
  generateOrderCode,
  calculateTechnical,
  createConfiguration,
  createQuote,
} from "../api/client";

const STORAGE_KEY = "hvac-cpq-configurator";

interface PersistedConfig {
  familyId: number;
  values: Record<string, string | number | boolean>;
}

interface ConfiguratorState {
  families: ProductFamily[];
  familiesLoading: boolean;
  selectedFamily: ProductFamily | null;
  values: Record<string, string | number | boolean>;
  pricing: PricingResponse | null;
  orderCode: string | null;
  technical: TechnicalCalculationResponse | null;
  calculating: boolean;
  serverErrors: string[];
  touched: Record<string, boolean>;
  quote: QuoteResponse | null;
  saving: boolean;
}

export function useConfigurator() {
  const [state, setState] = useState<ConfiguratorState>({
    families: [],
    familiesLoading: true,
    selectedFamily: null,
    values: {},
    pricing: null,
    orderCode: null,
    technical: null,
    calculating: false,
    serverErrors: [],
    touched: {},
    quote: null,
    saving: false,
  });

  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  const abortRef = useRef<AbortController>(undefined);
  const restoredRef = useRef(false);

  // --- Load families + restore from localStorage ---
  useEffect(() => {
    fetchFamilies()
      .then((families) => {
        let restoredFamily: ProductFamily | null = null;
        let restoredValues: Record<string, string | number | boolean> = {};

        if (!restoredRef.current) {
          restoredRef.current = true;
          try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (raw) {
              const saved: PersistedConfig = JSON.parse(raw);
              const match = families.find((f) => f.id === saved.familyId);
              if (match) {
                restoredFamily = match;
                restoredValues = saved.values;
              }
            }
          } catch {
            // corrupt localStorage — ignore
          }
        }

        setState((s) => ({
          ...s,
          families,
          familiesLoading: false,
          ...(restoredFamily
            ? { selectedFamily: restoredFamily, values: restoredValues }
            : {}),
        }));
      })
      .catch(() => setState((s) => ({ ...s, familiesLoading: false })));
  }, []);

  // --- Persist to localStorage on values/family change ---
  useEffect(() => {
    if (state.selectedFamily) {
      const data: PersistedConfig = {
        familyId: state.selectedFamily.id,
        values: state.values,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    }
  }, [state.selectedFamily, state.values]);

  const selectFamily = useCallback((family: ProductFamily | null) => {
    if (!family) {
      localStorage.removeItem(STORAGE_KEY);
    }
    setState((s) => ({
      ...s,
      selectedFamily: family,
      values: {},
      pricing: null,
      orderCode: null,
      technical: null,
      serverErrors: [],
      touched: {},
      quote: null,
      saving: false,
    }));
  }, []);

  const setValue = useCallback(
    (code: string, value: string | number | boolean) => {
      setState((s) => ({
        ...s,
        values: { ...s.values, [code]: value },
        touched: { ...s.touched, [code]: true },
        quote: null,
      }));
    },
    []
  );

  const touchField = useCallback((code: string) => {
    setState((s) => ({
      ...s,
      touched: { ...s.touched, [code]: true },
    }));
  }, []);

  const resetValues = useCallback(() => {
    setState((s) => ({
      ...s,
      values: {},
      pricing: null,
      orderCode: null,
      technical: null,
      serverErrors: [],
      touched: {},
      quote: null,
    }));
  }, []);

  // --- Client-side field validation ---
  const clientFieldErrors = useMemo(() => {
    if (!state.selectedFamily) return {};
    return validateClient(
      state.selectedFamily.attributes,
      state.values,
      state.touched
    );
  }, [state.selectedFamily, state.values, state.touched]);

  // --- Server-side field errors (parsed from API messages) ---
  const serverFieldErrors = useMemo(
    () => parseFieldErrors(state.serverErrors),
    [state.serverErrors]
  );

  // --- Merged field errors (client takes priority) ---
  const fieldErrors = useMemo(() => {
    return { ...serverFieldErrors, ...clientFieldErrors };
  }, [clientFieldErrors, serverFieldErrors]);

  // --- Non-field errors (shown as alerts) ---
  const generalErrors = useMemo(() => {
    const fieldCodes = new Set(Object.keys(serverFieldErrors));
    return state.serverErrors.filter((msg) => {
      const match = msg.match(/[Aa]ttribute '(\w+)'/);
      if (match && fieldCodes.has(match[1])) return false;
      const missingMatch = msg.match(/[Mm]issing required attributes?:\s*/);
      if (missingMatch) return false;
      return true;
    });
  }, [state.serverErrors, serverFieldErrors]);

  // --- Build payload ---
  const buildPayload = useCallback((): ConfigurationPayload | null => {
    if (!state.selectedFamily) return null;

    const filledValues = Object.entries(state.values)
      .filter(([, v]) => v !== "" && v !== undefined && v !== null)
      .map(([attribute_code, value]) => ({ attribute_code, value }));

    if (filledValues.length === 0) return null;

    return {
      product_family_id: state.selectedFamily.id,
      name: "live-preview",
      status: "draft",
      values: filledValues,
    };
  }, [state.selectedFamily, state.values]);

  // --- Debounced API calls with AbortController ---
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    abortRef.current?.abort();

    const payload = buildPayload();

    if (!payload) {
      debounceRef.current = setTimeout(() => {
        setState((s) => ({
          ...s,
          pricing: null,
          orderCode: null,
          technical: null,
          serverErrors: [],
          calculating: false,
        }));
      }, 0);
      return () => {
        if (debounceRef.current) clearTimeout(debounceRef.current);
      };
    }

    const controller = new AbortController();
    abortRef.current = controller;

    debounceRef.current = setTimeout(async () => {
      setState((s) => ({ ...s, calculating: true }));

      try {
        const [pricingResult, orderCodeResult, technicalResult] =
          await Promise.allSettled([
            calculatePrice(payload, controller.signal),
            generateOrderCode(payload, controller.signal),
            calculateTechnical(payload, controller.signal),
          ]);

        if (controller.signal.aborted) return;

        setState((s) => ({
          ...s,
          calculating: false,
          pricing:
            pricingResult.status === "fulfilled"
              ? pricingResult.value
              : null,
          orderCode:
            orderCodeResult.status === "fulfilled"
              ? orderCodeResult.value.order_code
              : null,
          technical:
            technicalResult.status === "fulfilled"
              ? technicalResult.value
              : null,
          serverErrors: extractErrors([
            pricingResult,
            orderCodeResult,
            technicalResult,
          ]),
        }));
      } catch {
        if (!controller.signal.aborted) {
          setState((s) => ({ ...s, calculating: false }));
        }
      }
    }, 500);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      controller.abort();
    };
  }, [buildPayload]);

  // --- Check if quote can be generated ---
  const canGenerateQuote = useMemo(() => {
    if (!state.selectedFamily || state.saving || state.calculating) return false;
    if (Object.keys(clientFieldErrors).length > 0) return false;

    const requiredAttrs = state.selectedFamily.attributes.filter(
      (a) => a.is_required
    );
    return requiredAttrs.every((attr) => {
      const val = state.values[attr.code];
      return val !== "" && val !== undefined && val !== null;
    });
  }, [
    state.selectedFamily,
    state.values,
    state.saving,
    state.calculating,
    clientFieldErrors,
  ]);

  // --- Generate quote (save configuration + create quote) ---
  const requestQuote = useCallback(async () => {
    if (!state.selectedFamily) return;

    // Touch all fields to surface any remaining client-side errors
    const allTouched: Record<string, boolean> = {};
    for (const attr of state.selectedFamily.attributes) {
      allTouched[attr.code] = true;
    }
    setState((s) => ({ ...s, touched: { ...s.touched, ...allTouched } }));

    const payload = buildPayload();
    if (!payload) return;

    setState((s) => ({ ...s, saving: true }));

    try {
      const familyName = state.selectedFamily.name;
      const dateStr = new Date().toISOString().split("T")[0];
      const configPayload: ConfigurationPayload = {
        ...payload,
        name: `${familyName} — ${dateStr}`,
        status: "active",
      };

      const config = await createConfiguration(configPayload);
      const quote = await createQuote(config.id);

      setState((s) => ({ ...s, saving: false, quote }));
    } catch (err) {
      const apiErr = err as ApiError;
      const msg = apiErr?.message || "Failed to generate quote";
      setState((s) => ({
        ...s,
        saving: false,
        serverErrors: [...s.serverErrors, msg],
      }));
    }
  }, [state.selectedFamily, buildPayload]);

  const applySuggestedConfiguration = useCallback(
    (familyId: number, values: Record<string, string | number | boolean>) => {
      const family = state.families.find((f) => f.id === familyId);
      if (!family) return;

      const touched: Record<string, boolean> = {};
      for (const code of Object.keys(values)) {
        touched[code] = true;
      }

      setState((s) => ({
        ...s,
        selectedFamily: family,
        values,
        touched: { ...s.touched, ...touched },
        quote: null,
      }));
    },
    [state.families]
  );

  const hasValues = Object.values(state.values).some(
    (v) => v !== "" && v !== undefined && v !== null
  );

  return {
    families: state.families,
    familiesLoading: state.familiesLoading,
    selectedFamily: state.selectedFamily,
    values: state.values,
    pricing: state.pricing,
    orderCode: state.orderCode,
    technical: state.technical,
    calculating: state.calculating,
    touched: state.touched,
    quote: state.quote,
    saving: state.saving,
    fieldErrors,
    generalErrors,
    hasValues,
    canGenerateQuote,
    selectFamily,
    setValue,
    touchField,
    resetValues,
    requestQuote,
    applySuggestedConfiguration,
  };
}

// --- Client-side validation (instant, no API call) ---
function validateClient(
  attributes: AttributeDefinition[],
  values: Record<string, string | number | boolean>,
  touched: Record<string, boolean>
): Record<string, string> {
  const errors: Record<string, string> = {};

  for (const attr of attributes) {
    if (!touched[attr.code]) continue;

    const val = values[attr.code];
    const isEmpty = val === "" || val === undefined || val === null;

    if (attr.is_required && isEmpty) {
      errors[attr.code] = `${attr.name} is required`;
      continue;
    }
    if (isEmpty) continue;

    if (attr.attribute_type === "integer") {
      const num = Number(val);
      if (attr.min_int != null && num < attr.min_int) {
        errors[attr.code] =
          `Minimum value: ${attr.min_int}${attr.unit ? " " + attr.unit : ""}`;
      } else if (attr.max_int != null && num > attr.max_int) {
        errors[attr.code] =
          `Maximum value: ${attr.max_int}${attr.unit ? " " + attr.unit : ""}`;
      }
    }

    if (attr.attribute_type === "decimal") {
      const num = Number(val);
      if (attr.min_decimal != null && num < attr.min_decimal) {
        errors[attr.code] =
          `Minimum value: ${attr.min_decimal}${attr.unit ? " " + attr.unit : ""}`;
      } else if (attr.max_decimal != null && num > attr.max_decimal) {
        errors[attr.code] =
          `Maximum value: ${attr.max_decimal}${attr.unit ? " " + attr.unit : ""}`;
      }
    }
  }

  return errors;
}

// --- Parse backend errors into field-level errors ---
function parseFieldErrors(
  messages: string[]
): Record<string, string> {
  const errors: Record<string, string> = {};

  for (const msg of messages) {
    // "Attribute 'height' is required to ..."
    const attrMatch = msg.match(/[Aa]ttribute '(\w+)'/);
    if (attrMatch) {
      const code = attrMatch[1];
      if (!errors[code]) {
        errors[code] = msg;
      }
      continue;
    }

    // "Missing required attributes: width, height"
    const missingMatch = msg.match(
      /[Mm]issing required attributes?:\s*(.+)/
    );
    if (missingMatch) {
      const codes = missingMatch[1].split(/,\s*/);
      for (const code of codes) {
        const trimmed = code.trim();
        if (trimmed && !errors[trimmed]) {
          errors[trimmed] = "This field is required";
        }
      }
    }
  }

  return errors;
}

// --- Extract error messages from settled promises ---
function extractErrors(
  results: PromiseSettledResult<unknown>[]
): string[] {
  const errors: string[] = [];
  const seen = new Set<string>();

  for (const r of results) {
    if (r.status === "rejected") {
      const err = r.reason as ApiError;
      const msg = err?.message || "Unknown error";
      if (!seen.has(msg)) {
        seen.add(msg);
        errors.push(msg);
      }
    }
  }

  return errors;
}
