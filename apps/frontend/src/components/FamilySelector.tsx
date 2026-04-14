import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardActionArea from "@mui/material/CardActionArea";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import Chip from "@mui/material/Chip";
import Skeleton from "@mui/material/Skeleton";
import Box from "@mui/material/Box";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import type { ProductFamily } from "../types";

interface FamilySelectorProps {
  families: ProductFamily[];
  loading: boolean;
  selected: ProductFamily | null;
  onSelect: (family: ProductFamily | null) => void;
}

export default function FamilySelector({
  families,
  loading,
  selected,
  onSelect,
}: FamilySelectorProps) {
  if (loading) {
    return (
      <Grid container spacing={2}>
        {[1, 2, 3].map((i) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={i}>
            <Skeleton variant="rounded" height={140} sx={{ borderRadius: 3 }} />
          </Grid>
        ))}
      </Grid>
    );
  }

  if (families.length === 0) {
    return (
      <Typography color="text.secondary" sx={{ py: 4, textAlign: "center" }}>
        No product families available. Seed demo data first.
      </Typography>
    );
  }

  return (
    <Grid container spacing={2}>
      {families.map((family) => {
        const isSelected = selected?.id === family.id;
        return (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={family.id}>
            <Card
              variant={isSelected ? "elevation" : "outlined"}
              sx={{
                border: isSelected ? 2 : 1,
                borderColor: isSelected ? "primary.main" : "divider",
                transition: "all 0.2s",
              }}
            >
              <CardActionArea
                onClick={() => onSelect(isSelected ? null : family)}
                sx={{ p: 0.5 }}
              >
                <CardContent>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      mb: 1,
                    }}
                  >
                    <Typography variant="h6" component="div" sx={{ fontSize: "1rem" }}>
                      {family.name}
                    </Typography>
                    {isSelected && (
                      <CheckCircleIcon color="primary" fontSize="small" />
                    )}
                  </Box>
                  {family.description && (
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 1.5 }}
                    >
                      {family.description}
                    </Typography>
                  )}
                  <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap" }}>
                    <Chip
                      label={family.code}
                      size="small"
                      variant="outlined"
                    />
                    <Chip
                      label={`${family.attributes.length} attributes`}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        );
      })}
    </Grid>
  );
}
