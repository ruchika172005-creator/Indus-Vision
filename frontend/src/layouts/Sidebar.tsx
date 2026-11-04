import React from "react";
import {
  LayoutDashboard,
  Scan,
  Database,
  Cpu,
  History,
  BarChart3,
  FileText,
  Settings,
  ShieldCheck,
  Activity,
  CheckCircle2,
  AlertCircle
} from "lucide-react";

export type PageId =
  | "dashboard"
  | "inspection"
  | "datasets"
  | "models"
  | "history"
  | "analytics"
  | "reports"
  | "settings";

interface Props {
  activePage: PageId;
  onSelectPage: (page: PageId) => void;
  systemStatus?: {
    healthy: boolean;
    device: string;
    geminiConfigured: boolean;
  };
}

export const Sidebar: React.FC<Props> = ({
  activePage,
  onSelectPage,
  systemStatus
}) => {
  const navItems: { id: PageId; label: string; icon: React.ReactNode; badge?: string }[] = [
    { id: "dashboard", label: "Dashboard", icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: "inspection", label: "Live Inspection", icon: <Scan className="w-4 h-4" />, badge: "AI Core" },
    { id: "datasets", label: "Dataset Management", icon: <Database className="w-4 h-4" /> },
    { id: "models", label: "Model Management", icon: <Cpu className="w-4 h-4" /> },
    { id: "history", label: "Inspection History", icon: <History className="w-4 h-4" /> },
    { id: "analytics", label: "Quality Analytics", icon: <BarChart3 className="w-4 h-4" /> },
    { id: "reports", label: "Audit Reports", icon: <FileText className="w-4 h-4" /> },
    { id: "settings", label: "System Settings", icon: <Settings className="w-4 h-4" /> }
  ];

  return (
    <aside className="w-64 bg-[#0B132B] text-slate-300 flex flex-col h-screen select-none shrink-0 border-r border-slate-800/80">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/70 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-1.5">
            Indus<span className="text-blue-400">Vision</span>
          </h1>
          <p className="text-[10px] text-slate-400 font-medium tracking-wide uppercase">
            Industrial Vision & VLM
          </p>
        </div>
      </div>

      {/* Live System Connectivity Chip */}
      <div className="px-4 py-3 mx-3 my-2 bg-slate-900/80 rounded-lg border border-slate-800 text-[11px] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span
              className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                systemStatus?.healthy ? "bg-emerald-400" : "bg-amber-400"
              }`}
            />
            <span
              className={`relative inline-flex rounded-full h-2 w-2 ${
                systemStatus?.healthy ? "bg-emerald-500" : "bg-amber-500"
              }`}
            />
          </span>
          <span className="font-semibold text-slate-200">
            {systemStatus?.healthy ? "Backend Online" : "Connecting..."}
          </span>
        </div>
        <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded-sm">
          {systemStatus?.device?.includes("CUDA") ? "CUDA GPU" : "CPU Engine"}
        </span>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectPage(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition-all duration-150 ${
                isActive
                  ? "bg-blue-600 text-white shadow-sm shadow-blue-600/30 font-bold"
                  : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/60"
              }`}
            >
              <div className="flex items-center gap-3">
                <span className={isActive ? "text-white" : "text-slate-400"}>
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={`text-[9px] font-bold px-1.5 py-0.5 rounded-sm uppercase tracking-wider ${
                    isActive ? "bg-blue-500 text-white" : "bg-slate-800 text-blue-400"
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/70 text-[11px] text-slate-400 space-y-1 bg-slate-950/40">
        <div className="flex items-center justify-between text-slate-400">
          <span>GenAI Status:</span>
          <span className="flex items-center gap-1 font-semibold text-slate-300">
            {systemStatus?.geminiConfigured ? (
              <span className="text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Gemini Active
              </span>
            ) : (
              <span className="text-amber-400 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" /> Rule Fallback
              </span>
            )}
          </span>
        </div>
        <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1">
          <span>Version: 1.0.0 (B.Tech Final)</span>
          <span>FastAPI + YOLOv8</span>
        </div>
      </div>
    </aside>
  );
};
