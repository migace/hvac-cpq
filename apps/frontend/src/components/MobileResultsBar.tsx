import { useState } from "react";
import Paper from "@mui/material/Paper";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import IconButton from "@mui/material/IconButton";
import SwipeableDrawer from "@mui/material/SwipeableDrawer";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import CloseIcon from "@mui/icons-material/Close";
import CircularProgress from "@mui/material/CircularProgress";
import ResultsPanel from "./ResultsPanel";
import { formatPrice } from "../utils/format";
import type {
  PricingResponse,
  TechnicalCalculationResponse,
  QuoteResponse,
} from "../types";

interface MobileResultsBarProps {
  pricing: PricingResponse | null;
  orderCode: string | null;
  technical: TechnicalCalculationResponse | null;
  calculating: boolean;
  generalErrors: string[];
  hasValues: boolean;
  quote: QuoteResponse | null;
  saving: boolean;
  canGenerateQuote: boolean;
  onGenerateQuote: () => void;
}

export default function MobileResultsBar({
  pricing,
  orderCode,
  technical,
  calculating,
  generalErrors,
  hasValues,
  quote,
  saving,
  canGenerateQuote,
  onGenerateQuote,
}: MobileResultsBarProps) {
  const [drawerOpen, setDrawerOpen] = useState(false);

  if (!hasValues) return null;

  const hasResults = pricing || orderCode || (technical && technical.results.length > 0);
  const hasErrors = generalErrors.length > 0;

  if (!hasResults && !hasErrors && !calculating) return null;

  return (
    <>
      {/* Fixed bottom bar */}
      <Paper
        elevation={8}
        sx={{
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 1200,
          px: 2,
          py: 1.5,
          borderRadius: 0,
          borderTop: 1,
          borderColor: "divider",
          cursor: "pointer",
        }}
        onClick={() => setDrawerOpen(true)}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, minWidth: 0 }}>
            {calculating && <CircularProgress size={18} />}

            {pricing && (
              <Typography
                variant="subtitle1"
                sx={{ fontWeight: 700, fontFamily: "monospace" }}
              >
                {formatPrice(pricing.total_price, pricing.currency)}
              </Typography>
            )}

            {orderCode && (
              <Chip
                label={orderCode}
                size="small"
                variant="outlined"
                color="primary"
                sx={{ fontFamily: "monospace", fontWeight: 600 }}
              />
            )}

            {quote && (
              <Chip
                label={quote.quote_number}
                size="small"
                color="success"
                sx={{ fontFamily: "monospace", fontWeight: 600 }}
              />
            )}

            {hasErrors && !pricing && (
              <Typography variant="body2" color="warning.main">
                Configuration incomplete
              </Typography>
            )}
          </Box>

          <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
            <Typography variant="caption" color="text.secondary">
              Details
            </Typography>
            <KeyboardArrowUpIcon fontSize="small" color="action" />
          </Box>
        </Box>
      </Paper>

      {/* Bottom drawer with full results */}
      <SwipeableDrawer
        anchor="bottom"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onOpen={() => setDrawerOpen(true)}
        disableSwipeToOpen
        slotProps={{
          paper: {
            sx: {
              maxHeight: "80vh",
              borderTopLeftRadius: 16,
              borderTopRightRadius: 16,
            },
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
            <Typography variant="h6">Configuration Results</Typography>
            <IconButton
              size="small"
              onClick={() => setDrawerOpen(false)}
            >
              <CloseIcon />
            </IconButton>
          </Box>
          <ResultsPanel
            pricing={pricing}
            orderCode={orderCode}
            technical={technical}
            calculating={calculating}
            validationErrors={generalErrors}
            hasValues={hasValues}
            quote={quote}
            saving={saving}
            canGenerateQuote={canGenerateQuote}
            onGenerateQuote={onGenerateQuote}
          />
        </Box>
      </SwipeableDrawer>

      {/* Spacer so content isn't hidden behind fixed bar */}
      <Box sx={{ height: 64 }} />
    </>
  );
}
