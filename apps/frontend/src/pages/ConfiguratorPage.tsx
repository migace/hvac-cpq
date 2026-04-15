import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material/styles";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import { useConfigurator } from "../hooks/useConfigurator";
import FamilySelector from "../components/FamilySelector";
import ConfigurationForm from "../components/ConfigurationForm";
import ResultsPanel from "../components/ResultsPanel";
import MobileResultsBar from "../components/MobileResultsBar";
import ChatPanel from "../components/ChatPanel";
import type { SuggestedConfiguration } from "../types";

export default function ConfiguratorPage() {
  const {
    families,
    familiesLoading,
    selectedFamily,
    values,
    pricing,
    orderCode,
    technical,
    calculating,
    fieldErrors,
    generalErrors,
    disabledFields,
    hasValues,
    quote,
    saving,
    canGenerateQuote,
    selectFamily,
    setValue,
    touchField,
    resetValues,
    requestQuote,
    applySuggestedConfiguration,
  } = useConfigurator();

  const handleSuggestedConfig = (config: SuggestedConfiguration) => {
    applySuggestedConfiguration(config.family_id, config.values);
  };

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  return (
    <>
      <Typography variant="h4" sx={{ mb: 0.5 }}>
        Product Configurator
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Select a product family and configure parameters to see pricing, order
        code, and technical specifications in real time.
      </Typography>

      {!selectedFamily ? (
        <>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Choose product family
          </Typography>
          <FamilySelector
            families={families}
            loading={familiesLoading}
            selected={selectedFamily}
            onSelect={selectFamily}
          />
        </>
      ) : (
        <>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              mb: 2,
            }}
          >
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={() => selectFamily(null)}
              size="small"
            >
              Back to family selection
            </Button>

            {hasValues && (
              <Button
                startIcon={<RestartAltIcon />}
                onClick={resetValues}
                size="small"
                color="inherit"
              >
                Reset
              </Button>
            )}
          </Box>

          <Grid container spacing={3}>
            {/* Configuration form — full width on mobile */}
            <Grid size={{ xs: 12, md: 7 }}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 0.5 }}>
                    {selectedFamily.name}
                  </Typography>
                  {selectedFamily.description && (
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 2 }}
                    >
                      {selectedFamily.description}
                    </Typography>
                  )}
                  <ConfigurationForm
                    attributes={selectedFamily.attributes}
                    values={values}
                    fieldErrors={fieldErrors}
                    disabledFields={disabledFields}
                    onChange={setValue}
                    onBlur={touchField}
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* Desktop: sticky results panel */}
            {!isMobile && (
              <Grid size={{ md: 5 }}>
                <Box sx={{ position: "sticky", top: 16 }}>
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
                    onGenerateQuote={requestQuote}
                  />
                </Box>
              </Grid>
            )}
          </Grid>

          {/* Mobile: floating bottom bar + swipeable drawer */}
          {isMobile && (
            <MobileResultsBar
              pricing={pricing}
              orderCode={orderCode}
              technical={technical}
              calculating={calculating}
              generalErrors={generalErrors}
              hasValues={hasValues}
              quote={quote}
              saving={saving}
              canGenerateQuote={canGenerateQuote}
              onGenerateQuote={requestQuote}
            />
          )}
        </>
      )}

      <ChatPanel onSuggestedConfiguration={handleSuggestedConfig} />
    </>
  );
}
