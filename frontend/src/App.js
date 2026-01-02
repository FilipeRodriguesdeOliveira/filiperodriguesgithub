import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { Toaster } from "@/components/ui/sonner";

// Pages
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import DashboardLayout from "@/layouts/DashboardLayout";
import DashboardOverview from "@/pages/DashboardOverview";
import ConnectionsPage from "@/pages/ConnectionsPage";
import GoalsPage from "@/pages/GoalsPage";
import DataCollectionPage from "@/pages/DataCollectionPage";
import AIBrainPage from "@/pages/AIBrainPage";
import AISpecialistsPage from "@/pages/AISpecialistsPage";
import CampaignsPage from "@/pages/CampaignsPage";
import PlatformIntegrationsPage from "@/pages/PlatformIntegrationsPage";
import OnboardingPage from "@/pages/OnboardingPage";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardOverview />} />
            <Route path="connections" element={<ConnectionsPage />} />
            <Route path="platform-integrations" element={<PlatformIntegrationsPage />} />
            <Route path="goals" element={<GoalsPage />} />
            <Route path="data" element={<DataCollectionPage />} />
            <Route path="ai-brain" element={<AIBrainPage />} />
            <Route path="ai-specialists" element={<AISpecialistsPage />} />
            <Route path="campaigns" element={<CampaignsPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Toaster position="top-right" theme="dark" />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;