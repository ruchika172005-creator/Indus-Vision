import React, { useState, useEffect } from "react";
import { MainLayout } from "./layouts/MainLayout";
import { PageId } from "./layouts/Sidebar";
import { DashboardPage } from "./pages/DashboardPage";
import { LiveInspectionPage } from "./pages/LiveInspectionPage";
import { DatasetManagementPage } from "./pages/DatasetManagementPage";
import { ModelManagementPage } from "./pages/ModelManagementPage";
import { InspectionHistoryPage } from "./pages/InspectionHistoryPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { SettingsPage } from "./pages/SettingsPage";
import { ApiService } from "./services/api";
import { PRODUCTION_LINES, ProductionLineConfig } from "./types";

export const App: React.FC = () => {
  const [activePage, setActivePage] = useState<PageId>("dashboard");
  const [selectedLineId, setSelectedLineId] = useState<string>("line_4");
  const [systemStatus, setSystemStatus] = useState<{
    healthy: boolean;
    device: string;
    geminiConfigured: boolean;
  }>({
    healthy: true,
    device: "CPU Engine",
    geminiConfigured: false
  });

  const currentLine: ProductionLineConfig =
    PRODUCTION_LINES[selectedLineId] || PRODUCTION_LINES["line_4"];

  const checkHealth = async () => {
    try {
      const health = await ApiService.getHealth();
      setSystemStatus({
        healthy: health.status === "healthy",
        device: health.device || "CPU",
        geminiConfigured: health.gemini_configured
      });
    } catch {
      setSystemStatus((prev) => ({ ...prev, healthy: false }));
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 25000);
    return () => clearInterval(interval);
  }, []);

  return (
    <MainLayout
      activePage={activePage}
      onSelectPage={setActivePage}
      systemStatus={systemStatus}
      selectedLineId={selectedLineId}
      onSelectLine={setSelectedLineId}
    >
      {activePage === "dashboard" && (
        <DashboardPage
          currentLine={currentLine}
          onNavigateToInspection={() => setActivePage("inspection")}
          onNavigateToDatasets={() => setActivePage("datasets")}
          onNavigateToModels={() => setActivePage("models")}
        />
      )}
      {activePage === "inspection" && (
        <LiveInspectionPage currentLine={currentLine} />
      )}
      {activePage === "datasets" && <DatasetManagementPage />}
      {activePage === "models" && <ModelManagementPage />}
      {activePage === "history" && (
        <InspectionHistoryPage currentLine={currentLine} />
      )}
      {activePage === "analytics" && (
        <AnalyticsPage currentLine={currentLine} />
      )}
      {activePage === "reports" && <ReportsPage />}
      {activePage === "settings" && <SettingsPage />}
    </MainLayout>
  );
};

export default App;
