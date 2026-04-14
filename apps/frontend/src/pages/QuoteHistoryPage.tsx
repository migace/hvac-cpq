import { useEffect, useState } from "react";
import Typography from "@mui/material/Typography";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Chip from "@mui/material/Chip";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import IconButton from "@mui/material/IconButton";
import Collapse from "@mui/material/Collapse";
import Divider from "@mui/material/Divider";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import QrCodeIcon from "@mui/icons-material/QrCode";
import { fetchQuotes } from "../api/client";
import { formatPrice } from "../utils/format";
import type { QuoteResponse } from "../types";

const STATUS_COLORS: Record<string, "success" | "warning" | "error" | "default"> = {
  generated: "success",
  draft: "default",
  approved: "success",
  rejected: "error",
};

function formatDate(iso: string): string {
  return new Intl.DateTimeFormat("pl-PL", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(iso));
}

interface ConfigSnapshot {
  product_family_name?: string;
  product_family_code?: string;
  configuration_name?: string;
  order_code?: string | null;
  values?: { attribute_name: string; value: unknown; unit?: string | null }[];
}

function QuoteRow({ quote }: { quote: QuoteResponse }) {
  const [open, setOpen] = useState(false);
  const snapshot = quote.configuration_snapshot as ConfigSnapshot;

  return (
    <>
      <TableRow
        hover
        sx={{ cursor: "pointer", "& > *": { borderBottom: "unset" } }}
        onClick={() => setOpen(!open)}
      >
        <TableCell padding="checkbox">
          <IconButton size="small">
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell sx={{ fontFamily: "monospace", fontWeight: 700 }}>
          {quote.quote_number}
        </TableCell>
        <TableCell>{snapshot.product_family_name ?? "—"}</TableCell>
        <TableCell>
          {snapshot.order_code ? (
            <Chip
              label={snapshot.order_code}
              size="small"
              variant="outlined"
              color="primary"
              icon={<QrCodeIcon />}
              sx={{ fontFamily: "monospace", fontWeight: 600 }}
            />
          ) : (
            <Typography variant="body2" color="text.secondary">—</Typography>
          )}
        </TableCell>
        <TableCell>
          <Chip
            label={quote.status}
            size="small"
            color={STATUS_COLORS[quote.status] ?? "default"}
          />
        </TableCell>
        <TableCell
          align="right"
          sx={{ fontFamily: "monospace", fontWeight: 600 }}
        >
          {formatPrice(quote.total_price, quote.currency)}
        </TableCell>
        <TableCell align="right">
          {quote.created_at ? formatDate(quote.created_at) : "—"}
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell sx={{ py: 0 }} colSpan={7}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ py: 2, pl: 2, pr: 1 }}>
              <Typography variant="subtitle2" sx={{ mb: 1.5 }}>
                Configuration details
              </Typography>

              {snapshot.values && snapshot.values.length > 0 ? (
                <Grid container spacing={1.5} sx={{ maxWidth: 600 }}>
                  {snapshot.values.map((v, i) => (
                    <Grid size={{ xs: 6, sm: 4 }} key={i}>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ display: "block", lineHeight: 1.2 }}
                      >
                        {v.attribute_name}
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{ fontFamily: "monospace", fontWeight: 600 }}
                      >
                        {String(v.value)}
                        {v.unit ? ` ${v.unit}` : ""}
                      </Typography>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No configuration values recorded.
                </Typography>
              )}

              {snapshot.order_code && (
                <>
                  <Divider sx={{ my: 1.5, maxWidth: 600 }} />
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <QrCodeIcon fontSize="small" color="primary" />
                    <Typography variant="caption" color="text.secondary">
                      Order code:
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{ fontFamily: "monospace", fontWeight: 700 }}
                    >
                      {snapshot.order_code}
                    </Typography>
                  </Box>
                </>
              )}
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
}

export default function QuoteHistoryPage() {
  const [quotes, setQuotes] = useState<QuoteResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchQuotes()
      .then((data) => {
        const sorted = [...data].sort(
          (a, b) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        setQuotes(sorted);
      })
      .catch((err) => {
        setError(err?.message || "Failed to load quotes");
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <Typography variant="h4" sx={{ mb: 0.5 }}>
        Quote History
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Browse previously generated quotes and their configuration snapshots.
      </Typography>

      {loading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {!loading && !error && quotes.length === 0 && (
        <Card variant="outlined">
          <CardContent>
            <Typography
              color="text.secondary"
              sx={{ textAlign: "center", py: 4 }}
            >
              No quotes generated yet. Configure a product and generate a quote
              to see it here.
            </Typography>
          </CardContent>
        </Card>
      )}

      {!loading && quotes.length > 0 && (
        <TableContainer component={Card} variant="outlined">
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox" />
                <TableCell>Quote #</TableCell>
                <TableCell>Product Family</TableCell>
                <TableCell>Order Code</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Total</TableCell>
                <TableCell align="right">Created</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {quotes.map((q) => (
                <QuoteRow key={q.id} quote={q} />
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </>
  );
}
