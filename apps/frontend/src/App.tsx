import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import ConfiguratorPage from "./pages/ConfiguratorPage";
import QuoteHistoryPage from "./pages/QuoteHistoryPage";

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<ConfiguratorPage />} />
        <Route path="/quotes" element={<QuoteHistoryPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
