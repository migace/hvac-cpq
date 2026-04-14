export interface AttributeOption {
  id: number;
  value: string;
  label: string;
  sort_order: number;
}

export interface AttributeDefinition {
  id: number;
  code: string;
  name: string;
  description: string | null;
  attribute_type: "string" | "integer" | "decimal" | "boolean" | "enum";
  is_required: boolean;
  unit: string | null;
  min_int: number | null;
  max_int: number | null;
  min_decimal: number | null;
  max_decimal: number | null;
  enum_options: AttributeOption[];
}

export interface ProductFamily {
  id: number;
  code: string;
  name: string;
  description: string | null;
  is_active: boolean;
  attributes: AttributeDefinition[];
}

export interface AttributeValuePayload {
  attribute_code: string;
  value: string | number | boolean;
}

export interface ConfigurationPayload {
  product_family_id: number;
  name: string;
  status: string;
  values: AttributeValuePayload[];
}

export interface PricingBreakdownItem {
  rule_name: string;
  label: string;
  amount: number;
}

export interface PricingResponse {
  currency: string;
  base_price: number;
  surcharge_total: number;
  total_price: number;
  breakdown: PricingBreakdownItem[];
}

export interface OrderCodeResponse {
  order_code: string;
}

export interface TechnicalCalculationItem {
  name: string;
  code: string;
  value: number;
  unit: string;
}

export interface TechnicalCalculationResponse {
  family_code: string;
  results: TechnicalCalculationItem[];
}

export interface QuoteResponse {
  id: number;
  product_configuration_id: number;
  quote_number: string;
  status: string;
  currency: string;
  base_price: number;
  surcharge_total: number;
  total_price: number;
  configuration_snapshot: Record<string, unknown>;
  pricing_snapshot: Record<string, unknown>;
  created_at: string;
}

export interface ApiError {
  type: string;
  message: string;
  code: string;
  request_id: string;
  details?: Record<string, unknown>;
}
