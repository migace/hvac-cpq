import { useRef, useEffect } from "react";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import FormHelperText from "@mui/material/FormHelperText";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import InputAdornment from "@mui/material/InputAdornment";
import Alert from "@mui/material/Alert";
import type { AttributeDefinition } from "../types";

interface ConfigurationFormProps {
  attributes: AttributeDefinition[];
  values: Record<string, string | number | boolean>;
  fieldErrors: Record<string, string>;
  onChange: (code: string, value: string | number | boolean) => void;
  onBlur: (code: string) => void;
}

export default function ConfigurationForm({
  attributes,
  values,
  fieldErrors,
  onChange,
  onBlur,
}: ConfigurationFormProps) {
  const required = attributes.filter((a) => a.is_required);
  const optional = attributes.filter((a) => !a.is_required);
  const firstRequiredRef = useRef<HTMLInputElement>(null);

  const hasAnyValue = Object.values(values).some(
    (v) => v !== "" && v !== undefined && v !== null
  );

  // Auto-focus first required field on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      firstRequiredRef.current?.focus();
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2.5 }}>
      {!hasAnyValue && (
        <Alert severity="info" variant="outlined" sx={{ mb: 0.5 }}>
          Start by filling in the required parameters below. Results will
          appear automatically as you configure.
        </Alert>
      )}

      {required.length > 0 && (
        <>
          <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 0.5 }}>
            Required parameters
          </Typography>
          {required.map((attr, i) => (
            <AttributeField
              key={attr.code}
              attribute={attr}
              value={values[attr.code]}
              error={fieldErrors[attr.code]}
              onChange={onChange}
              onBlur={onBlur}
              inputRef={i === 0 ? firstRequiredRef : undefined}
            />
          ))}
        </>
      )}

      {optional.length > 0 && (
        <>
          <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 1 }}>
            Optional parameters
          </Typography>
          {optional.map((attr) => (
            <AttributeField
              key={attr.code}
              attribute={attr}
              value={values[attr.code]}
              error={fieldErrors[attr.code]}
              onChange={onChange}
              onBlur={onBlur}
            />
          ))}
        </>
      )}
    </Box>
  );
}

interface AttributeFieldProps {
  attribute: AttributeDefinition;
  value: string | number | boolean | undefined;
  error: string | undefined;
  onChange: (code: string, value: string | number | boolean) => void;
  onBlur: (code: string) => void;
  inputRef?: React.Ref<HTMLInputElement>;
}

function AttributeField({
  attribute,
  value,
  error,
  onChange,
  onBlur,
  inputRef,
}: AttributeFieldProps) {
  const { code, name, attribute_type, is_required, unit, enum_options } =
    attribute;

  const hasError = !!error;

  switch (attribute_type) {
    case "enum":
      return (
        <TextField
          select
          label={name}
          value={value ?? ""}
          onChange={(e) => onChange(code, e.target.value)}
          onBlur={() => onBlur(code)}
          required={is_required}
          error={hasError}
          helperText={error || attribute.description}
          fullWidth
          size="small"
          inputRef={inputRef}
        >
          <MenuItem value="">
            <em>-- select --</em>
          </MenuItem>
          {[...enum_options]
            .sort((a, b) => a.sort_order - b.sort_order)
            .map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>
                {opt.label}
              </MenuItem>
            ))}
        </TextField>
      );

    case "integer":
      return (
        <TextField
          type="number"
          label={name}
          value={value ?? ""}
          onChange={(e) => {
            const v = e.target.value;
            onChange(code, v === "" ? "" : parseInt(v, 10));
          }}
          onBlur={() => onBlur(code)}
          required={is_required}
          error={hasError}
          helperText={error || buildRangeHint(attribute)}
          fullWidth
          size="small"
          inputRef={inputRef}
          slotProps={{
            htmlInput: {
              min: attribute.min_int ?? undefined,
              max: attribute.max_int ?? undefined,
              step: 1,
            },
            input: unit
              ? {
                  endAdornment: (
                    <InputAdornment position="end">{unit}</InputAdornment>
                  ),
                }
              : undefined,
          }}
        />
      );

    case "decimal":
      return (
        <TextField
          type="number"
          label={name}
          value={value ?? ""}
          onChange={(e) => {
            const v = e.target.value;
            onChange(code, v === "" ? "" : parseFloat(v));
          }}
          onBlur={() => onBlur(code)}
          required={is_required}
          error={hasError}
          helperText={error || buildRangeHint(attribute)}
          fullWidth
          size="small"
          inputRef={inputRef}
          slotProps={{
            htmlInput: {
              min: attribute.min_decimal ?? undefined,
              max: attribute.max_decimal ?? undefined,
              step: "any",
            },
            input: unit
              ? {
                  endAdornment: (
                    <InputAdornment position="end">{unit}</InputAdornment>
                  ),
                }
              : undefined,
          }}
        />
      );

    case "boolean":
      return (
        <Box>
          <FormControlLabel
            control={
              <Switch
                checked={!!value}
                onChange={(e) => onChange(code, e.target.checked)}
                onBlur={() => onBlur(code)}
              />
            }
            label={name}
          />
          {hasError && (
            <FormHelperText error>{error}</FormHelperText>
          )}
        </Box>
      );

    case "string":
    default:
      return (
        <TextField
          label={name}
          value={value ?? ""}
          onChange={(e) => onChange(code, e.target.value)}
          onBlur={() => onBlur(code)}
          required={is_required}
          error={hasError}
          helperText={error || attribute.description}
          fullWidth
          size="small"
          inputRef={inputRef}
        />
      );
  }
}

function buildRangeHint(attr: AttributeDefinition): string {
  const parts: string[] = [];
  const min = attr.min_int ?? attr.min_decimal;
  const max = attr.max_int ?? attr.max_decimal;

  if (min != null && max != null) {
    parts.push(`Range: ${min} – ${max}`);
  } else if (min != null) {
    parts.push(`Min: ${min}`);
  } else if (max != null) {
    parts.push(`Max: ${max}`);
  }
  if (attr.unit) parts.push(attr.unit);
  if (attr.description) parts.push(attr.description);

  return parts.join(" | ");
}
