import React, { useState, useEffect } from "react";
import { Sidebar, PageId } from "./Sidebar";
import { Zap, Clock, ShieldCheck, Download, RefreshCw, CheckCircle, Radio, Activity } from "lucide-react";
import { ApiService } from "../services/api";
import { PRODUCTION_LINES, ProductionLineConfig } from "../types";

interface Props {
  activePage: PageId;
  onSelectPage: (page: PageId) => void;
  systemStatus?: {
    healthy: boolean;
    device: string;
    geminiConfigured: boolean;
  };
  selectedLineId: string;
  onSelectLine: (lineId: string) => void;
  children: React.ReactNode;
}

export const MainLayout: React.FC<Props> = ({
  activePage,
  onSelectPage,
  systemStatus,
  selectedLineId,
  onSelectLine,
  children
}) => {
  const [currentTime, setCurrentTime] = useState<string>("");
  const [notification, setNotification] = useState<string | null>(null);

  const activeLineConfig: ProductionLineConfig =
    PRODUCTION_LINES[selectedLineId] || PRODUCTION_LINES["line_4"];

  const handleLineChange = (newLineId: string) => {
    onSelectLine(newLineId);
    const lineObj = PRODUCTION_LINES[newLineId];
    if (lineObj) {
      setNotification(`Switched active feed: ${lineObj.name} (${lineObj.stationName} • ${lineObj.lineSpeed})`);
      setTimeout(() => setNotification(null), 4000);
    }
  };

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleDateString(undefined, {
          weekday: "short",
          month: "short",
          day: "numeric",
          year: "numeric"
        }) + " • " + now.toLocaleTimeString()
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const pageTitles: Record<PageId, { title: string; subtitle: string }> = {
    dashboard: {
      title: "Manufacturing Quality Command Center",
      subtitle: "Real-time automated surface inspection metrics, throughput trends, and engineering dispositions."
    },
    inspection: {
      title: "Optical Quality Inspection & VLM Explanation",
      subtitle: "Computer vision defect localization and Multimodal AI root-cause interpretation."
    },
    datasets: {
      title: "Industrial Defect Benchmark Datasets",
      subtitle: "NEU-DET, GC10-DET, and MVTec AD catalog, annotation conversion, and split management."
    },
    models: {
      title: "YOLOv8 Detection Model Management",
      subtitle: "Model weight status, mAP benchmarks, and asynchronous background training orchestration."
    },
    history: {
      title: "Quality Inspection Audit Trail",
      subtitle: "Complete repository of historical optical inspection logs with telemetry search and filters."
    },
    analytics: {
      title: "Defect Statistical Analytics & Trends",
      subtitle: "Quantitative failure mode distribution, severity matrices, and production defect rates."
    },
    reports: {
      title: "Industrial Audit Reports & Compliance",
      subtitle: "Generate downloadable ISO 9001-compliant PDF reports and batch CSV data exports."
    },
    settings: {
      title: "System Parameters & API Configuration",
      subtitle: "Configure Multimodal Gemini API keys, detection thresholds, and severity assessment rules."
    }
  };

  const currentInfo = pageTitles[activePage];

  return (
    <div className="flex h-screen bg-[#F8FAFC] overflow-hidden font-sans">
      {/* Sidebar */}
      <Sidebar
        activePage={activePage}
        onSelectPage={onSelectPage}
        systemStatus={systemStatus}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Header Bar */}
        <header className="h-16 bg-white/95 backdrop-blur-md border-b border-slate-200/90 px-6 flex items-center justify-between shrink-0 shadow-2xs z-10">
          <div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
              {currentInfo.title}
            </h2>
            <p className="text-xs text-slate-500 hidden sm:block">
              {currentInfo.subtitle}
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Live Clock */}
            <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 bg-slate-50 rounded-lg border border-slate-200/80 text-[11px] font-mono text-slate-600">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>{currentTime || "Factory Time"}</span>
            </div>

            {/* Production Line Selector */}
            <div className="hidden md:flex items-center gap-2 text-xs font-semibold text-slate-700 bg-slate-100/90 px-3 py-1.5 rounded-lg border border-slate-200 shadow-2xs">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <select
                value={selectedLineId}
                onChange={(e) => handleLineChange(e.target.value)}
                className="bg-transparent border-none text-xs font-bold text-slate-800 focus:outline-hidden cursor-pointer"
              >
                <option value="line_4">Plant A • Mill Line 4</option>
                <option value="line_2">Plant A • Mill Line 2</option>
                <option value="line_1">Plant B • Casting Line 1</option>
              </select>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-sm bg-slate-200/80 text-slate-600">
                {activeLineConfig.lineSpeed}
              </span>
            </div>

            {activePage !== "inspection" && (
              <button
                onClick={() => onSelectPage("inspection")}
                className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold flex items-center gap-1.5 shadow-xs transition-colors cursor-pointer"
              >
                <Zap className="w-3.5 h-3.5" />
                Live Inspection
              </button>
            )}
          </div>
        </header>

        {/* Floating Line Switch Notification */}
        {notification && (
          <div className="fixed top-20 right-8 z-50 animate-in fade-in slide-in-from-top-4 duration-200">
            <div className="bg-slate-900/95 text-white backdrop-blur-md px-4 py-2.5 rounded-xl border border-blue-500/40 shadow-xl flex items-center gap-2.5 text-xs">
              <Radio className="w-4 h-4 text-emerald-400 animate-pulse" />
              <span className="font-semibold text-slate-100">{notification}</span>
            </div>
          </div>
        )}

        {/* Scrollable Workspace */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="max-w-7xl mx-auto space-y-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

