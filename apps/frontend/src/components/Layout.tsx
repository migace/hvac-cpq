import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import PrecisionManufacturingIcon from "@mui/icons-material/PrecisionManufacturing";
import BuildIcon from "@mui/icons-material/Build";
import HistoryIcon from "@mui/icons-material/History";
import { Link, useLocation } from "react-router-dom";
import type { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
}

const NAV_ITEMS = [
  { label: "Configurator", path: "/", icon: <BuildIcon fontSize="small" /> },
  { label: "Quote History", path: "/quotes", icon: <HistoryIcon fontSize="small" /> },
];

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <PrecisionManufacturingIcon sx={{ mr: 1.5 }} />
          <Typography
            variant="h6"
            component={Link}
            to="/"
            sx={{
              color: "inherit",
              textDecoration: "none",
              mr: 4,
            }}
          >
            HVAC CPQ
          </Typography>

          <Box sx={{ display: "flex", gap: 0.5 }}>
            {NAV_ITEMS.map((item) => (
              <Button
                key={item.path}
                component={Link}
                to={item.path}
                startIcon={item.icon}
                sx={{
                  color: "inherit",
                  opacity: location.pathname === item.path ? 1 : 0.7,
                  borderBottom: location.pathname === item.path ? "2px solid white" : "2px solid transparent",
                  borderRadius: 0,
                  px: 2,
                  "&:hover": { opacity: 1 },
                }}
              >
                {item.label}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ py: 3, flex: 1 }}>
        {children}
      </Container>
    </Box>
  );
}
