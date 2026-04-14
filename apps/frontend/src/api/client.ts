import type {
  ProductFamily,
  ConfigurationPayload,
  PricingResponse,
  OrderCodeResponse,
  TechnicalCalculationResponse,
  QuoteResponse,
} from "../types";

const API_BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({
      message: response.statusText,
    }));
    throw body.error ?? body;
  }

  return response.json();
}

export function fetchFamilies(): Promise<ProductFamily[]> {
  return request<ProductFamily[]>("/product-families");
}

export function fetchFamily(id: number): Promise<ProductFamily> {
  return request<ProductFamily>(`/product-families/${id}`);
}

export function calculatePrice(
  payload: ConfigurationPayload,
  signal?: AbortSignal
): Promise<PricingResponse> {
  return request<PricingResponse>(
    "/product-configurations/calculate-price",
    { method: "POST", body: JSON.stringify(payload), signal }
  );
}

export function generateOrderCode(
  payload: ConfigurationPayload,
  signal?: AbortSignal
): Promise<OrderCodeResponse> {
  return request<OrderCodeResponse>(
    "/product-configurations/generate-order-code",
    { method: "POST", body: JSON.stringify(payload), signal }
  );
}

export function calculateTechnical(
  payload: ConfigurationPayload,
  signal?: AbortSignal
): Promise<TechnicalCalculationResponse> {
  return request<TechnicalCalculationResponse>(
    "/product-configurations/calculate-technical",
    { method: "POST", body: JSON.stringify(payload), signal }
  );
}

export function createConfiguration(
  payload: ConfigurationPayload
): Promise<{ id: number }> {
  return request<{ id: number }>("/product-configurations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createQuote(configurationId: number): Promise<QuoteResponse> {
  return request<QuoteResponse>("/product-quotes", {
    method: "POST",
    body: JSON.stringify({ product_configuration_id: configurationId }),
  });
}

export function fetchQuotes(): Promise<QuoteResponse[]> {
  return request<QuoteResponse[]>("/product-quotes");
}
