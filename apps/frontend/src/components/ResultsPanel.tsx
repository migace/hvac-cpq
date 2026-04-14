import { useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Alert from "@mui/material/Alert";
import LinearProgress from "@mui/material/LinearProgress";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import Snackbar from "@mui/material/Snackbar";
import QrCodeIcon from "@mui/icons-material/QrCode";
import CalculateIcon from "@mui/icons-material/Calculate";
import ScienceIcon from "@mui/icons-material/Science";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import ReceiptLongIcon from "@mui/icons-material/ReceiptLong";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CircularProgress from "@mui/material/CircularProgress";
import { formatPrice } from "../utils/format";
import type {
  PricingResponse,
  TechnicalCalculationResponse,
  QuoteResponse,
} from "../types";

interface ResultsPanelProps {
  pricing: PricingResponse | null;
  orderCode: string | null;
  technical: TechnicalCalculationResponse | null;
  calculating: boolean;
  validationErrors: string[];
  hasValues: boolean;
  quote: QuoteResponse | null;
  saving: boolean;
  canGenerateQuote: boolean;
  onGenerateQuote: () => void;
}

export default function ResultsPanel({
  pricing,
  orderCode,
  technical,
  calculating,
  validationErrors,
  hasValues,
  quote,
  saving,
  canGenerateQuote,
  onGenerateQuote,
}: ResultsPanelProps) {
  if (!hasValues) {
    return (
      <Card variant="outlined" sx={{ height: "100%" }}>
        <CardContent>
          <Typography color="text.secondary" sx={{ textAlign: "center", py: 4 }}>
            Configure product parameters to see real-time results.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      {calculating && <LinearProgress />}

      {validationErrors.length > 0 && (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
          {validationErrors.map((err, i) => (
            <Alert severity="warning" key={i} variant="outlined">
              {err}
            </Alert>
          ))}
        </Box>
      )}

      {orderCode && <OrderCodeCard orderCode={orderCode} />}
      {pricing && <PricingCard pricing={pricing} />}
      {technical && technical.results.length > 0 && (
        <TechnicalCard technical={technical} />
      )}

      {quote && <QuoteCard quote={quote} orderCode={orderCode} />}

      {pricing && !quote && (
        <Button
          variant="contained"
          size="large"
          startIcon={
            saving ? (
              <CircularProgress size={18} color="inherit" />
            ) : (
              <ReceiptLongIcon />
            )
          }
          onClick={onGenerateQuote}
          disabled={!canGenerateQuote || saving}
          fullWidth
        >
          {saving ? "Generating..." : "Generate Quote"}
        </Button>
      )}
    </Box>
  );
}

function OrderCodeCard({ orderCode }: { orderCode: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(orderCode);
      setCopied(true);
    } catch {
      // clipboard API not available — silent fail
    }
  };

  return (
    <Card variant="outlined">
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1.5 }}>
          <QrCodeIcon fontSize="small" color="primary" />
          <Typography variant="subtitle2">Order Code</Typography>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Chip
            label={orderCode}
            color="primary"
            variant="outlined"
            sx={{
              fontSize: "1.1rem",
              fontWeight: 600,
              fontFamily: "monospace",
              py: 2,
              px: 1,
            }}
          />
          <Tooltip title="Copy to clipboard">
            <IconButton size="small" onClick={handleCopy} aria-label="Copy order code">
              <ContentCopyIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <Snackbar
          open={copied}
          autoHideDuration={2000}
          onClose={() => setCopied(false)}
          message="Order code copied"
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        />
      </CardContent>
    </Card>
  );
}

function PricingCard({ pricing }: { pricing: PricingResponse }) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1.5 }}>
          <CalculateIcon fontSize="small" color="primary" />
          <Typography variant="subtitle2">Pricing</Typography>
        </Box>

        <Table size="small">
          <TableBody>
            {pricing.breakdown.map((item, i) => (
              <TableRow key={i}>
                <TableCell sx={{ border: 0, pl: 0, py: 0.5 }}>
                  {item.label}
                </TableCell>
                <TableCell
                  align="right"
                  sx={{ border: 0, pr: 0, py: 0.5, fontFamily: "monospace" }}
                >
                  {formatPrice(item.amount, pricing.currency)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <Divider sx={{ my: 1.5 }} />

        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "baseline",
          }}
        >
          <Typography variant="body2" color="text.secondary">
            Total
          </Typography>
          <Typography variant="h6" color="primary.main" sx={{ fontFamily: "monospace" }}>
            {formatPrice(pricing.total_price, pricing.currency)}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

function TechnicalCard({
  technical,
}: {
  technical: TechnicalCalculationResponse;
}) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1.5 }}>
          <ScienceIcon fontSize="small" color="primary" />
          <Typography variant="subtitle2">Technical Parameters</Typography>
        </Box>

        <Table size="small">
          <TableBody>
            {technical.results.map((item) => (
              <TableRow key={item.code}>
                <TableCell sx={{ border: 0, pl: 0, py: 0.5 }}>
                  {item.name}
                </TableCell>
                <TableCell
                  align="right"
                  sx={{ border: 0, pr: 0, py: 0.5, fontFamily: "monospace" }}
                >
                  {item.value} {item.unit}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

function QuoteCard({ quote, orderCode }: { quote: QuoteResponse; orderCode: string | null }) {
  return (
    <Card
      variant="outlined"
      sx={{ borderColor: "success.main", bgcolor: "success.50" }}
    >
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1.5 }}>
          <CheckCircleIcon fontSize="small" color="success" />
          <Typography variant="subtitle2" color="success.main">
            Quote Generated
          </Typography>
        </Box>

        <Table size="small">
          <TableBody>
            <TableRow>
              <TableCell sx={{ border: 0, pl: 0, py: 0.5 }}>
                Quote number
              </TableCell>
              <TableCell
                align="right"
                sx={{
                  border: 0,
                  pr: 0,
                  py: 0.5,
                  fontFamily: "monospace",
                  fontWeight: 700,
                }}
              >
                {quote.quote_number}
              </TableCell>
            </TableRow>
            {orderCode && (
              <TableRow>
                <TableCell sx={{ border: 0, pl: 0, py: 0.5 }}>
                  Order code
                </TableCell>
                <TableCell
                  align="right"
                  sx={{
                    border: 0,
                    pr: 0,
                    py: 0.5,
                    fontFamily: "monospace",
                    fontWeight: 700,
                  }}
                >
                  {orderCode}
                </TableCell>
              </TableRow>
            )}
            <TableRow>
              <TableCell sx={{ border: 0, pl: 0, py: 0.5 }}>
                Status
              </TableCell>
              <TableCell align="right" sx={{ border: 0, pr: 0, py: 0.5 }}>
                <Chip label={quote.status} size="small" color="success" />
              </TableCell>
            </TableRow>
            <TableRow>
              <TableCell sx={{ border: 0, pl: 0, py: 0.5 }}>
                Total
              </TableCell>
              <TableCell
                align="right"
                sx={{
                  border: 0,
                  pr: 0,
                  py: 0.5,
                  fontFamily: "monospace",
                  fontWeight: 700,
                }}
              >
                {formatPrice(quote.total_price, quote.currency)}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
