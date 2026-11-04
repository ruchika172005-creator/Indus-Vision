import React, { useEffect, useState } from "react";
import { ApiService, getAssetUrl } from "../services/api";
import { DashboardSummary, Inspection, ProductionLineConfig } from "../types";
import { MetricCard } from "../components/MetricCard";
import { SeverityBadge } from "../components/SeverityBadge";
import { DecisionBadge } from "../components/DecisionBadge";
import { InspectionModal } from "../components/InspectionModal";
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  Percent,
  Layers,
  ArrowRight,
  RefreshCw,
  Cpu,
  Sparkles,
  Database,
  FileDown,
  Play,
  Table,
  Zap,
  Info,
  Factory
} from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from "recharts";

interface Props {
  currentLine?: ProductionLineConfig;
  onNavigateToInspection: () => void;
  onNavigateToDatasets: () => void;
  onNavigateToModels: () => void;
}

const BAR_COLORS = ["#2563EB", "#0284C7", "#0D9488", "#10B981", "#F59E0B", "#F97316"];

export const DashboardPage: React.FC<Props> = ({
  currentLine,
  onNavigateToInspection,
  onNavigateToDatasets,
  onNavigateToModels
}) => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedInspection, setSelectedInspection] = useState<Inspection | null>(null);
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  const fetchDashboard = async (isManualRefresh = false) => {
    try {
      if (isManualRefresh) setRefreshing(true);
      else setLoading(true);
      const res = await ApiService.getDashboardSummary();
      setData(res);
    } catch (err) {
      console.error("Failed to load dashboard summary:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    // Auto-reconnect if backend was offline
    const interval = setInterval(() => {
      setData((current) => {
        if (!current) {
          fetchDashboard();
        }
        return current;
      });
    }, 3500);
    return () => clearInterval(interval);
  }, []);

  const handleOpenInspection = async (id: number) => {
    try {
      const full = await ApiService.getInspection(id);
      setSelectedInspection(full);
    } catch (err) {
      console.error("Failed to fetch inspection details:", err);
    }
  };

  const handleDownloadPdf = async (id: number) => {
    setDownloadingId(id);
    try {
      const res = await ApiService.createPdfReport(id);
      if (res.download_url) {
        window.open(getAssetUrl(res.download_url), "_blank");
      }
    } catch (err) {
      console.error("Failed to generate PDF:", err);
      alert("Failed to download PDF report.");
    } finally {
      setDownloadingId(null);
    }
  };

  const handleExportCsv = () => {
    window.open(ApiService.getExportCsvUrl(), "_blank");
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-28 text-slate-400">
        <div className="w-12 h-12 rounded-full border-4 border-blue-200 border-t-blue-600 animate-spin mb-4" />
        <span className="text-sm font-bold text-slate-700 tracking-wide">
          Synthesizing Quality Intelligence Telemetry...
        </span>
        <p className="text-xs text-slate-400 mt-1">Connecting to inspection database and edge models</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-white p-10 rounded-2xl border border-slate-200 text-center shadow-xs max-w-lg mx-auto my-12">
        <div className="w-12 h-12 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center mx-auto mb-3">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <h3 className="text-sm font-bold text-slate-900 mb-1">Backend Service Unreachable</h3>
        <p className="text-xs text-slate-500 mb-4 leading-relaxed">
          Unable to establish communication with the FastAPI backend on port 8000. Ensure the server process is running.
        </p>
        <button
          onClick={() => fetchDashboard()}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition-colors cursor-pointer"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Command Center Action Toolbar */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Automated Optical Inspection (AOI) Status: <span className="text-emerald-600">OPERATIONAL</span>
            </h3>
            <div className="flex items-center gap-2 flex-wrap text-[11px] text-slate-500 mt-0.5">
              <span>Active Model: <strong className="font-mono text-slate-700">{data.active_model}</strong></span>
              <span>•</span>
              <span>Compute: <strong className="text-slate-700">{data.device_info}</strong></span>
              {currentLine && (
                <>
                  <span>•</span>
                  <span className="inline-flex items-center gap-1.5 font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    {currentLine.name} ({currentLine.category} • {currentLine.stationName})
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto justify-end">
          <button
            onClick={() => fetchDashboard(true)}
            disabled={refreshing}
            className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
            title="Refresh Metrics"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin text-blue-600" : ""}`} />
            Refresh
          </button>

          <button
            onClick={handleExportCsv}
            className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <Table className="w-3.5 h-3.5 text-slate-500" />
            Export CSV
          </button>

          <button
            onClick={onNavigateToInspection}
            className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold flex items-center gap-1.5 shadow-xs transition-colors cursor-pointer"
          >
            <Play className="w-3.5 h-3.5 fill-white" />
            Launch Inspection
          </button>
        </div>
      </div>

      {/* 5 KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Total Inspected"
          value={data.metrics.total_inspections}
          subtitle="Processed parts"
          icon={<Layers className="w-5 h-5 text-blue-600" />}
          accentColor="border-blue-600"
        />
        <MetricCard
          title="Defective Units"
          value={data.metrics.defective_products}
          subtitle="Anomalies detected"
          icon={<ShieldAlert className="w-5 h-5 text-rose-600" />}
          accentColor="border-rose-500"
        />
        <MetricCard
          title="Defect-Free Units"
          value={data.metrics.defect_free_products}
          subtitle="Standard compliance"
          icon={<ShieldCheck className="w-5 h-5 text-emerald-600" />}
          accentColor="border-emerald-500"
        />
        <MetricCard
          title="Overall Defect Rate"
          value={`${data.metrics.defect_rate}%`}
          subtitle="Process yield tracking"
          icon={<Percent className="w-5 h-5 text-amber-600" />}
          accentColor="border-amber-500"
        />
        <MetricCard
          title="High/Critical Risk"
          value={data.metrics.high_critical_defects}
          subtitle="Requires quarantine"
          icon={<ShieldAlert className="w-5 h-5 text-purple-600" />}
          accentColor="border-purple-500"
        />
      </div>

      {/* Two Analytical Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Inspection Volume Trends */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                7-Day Inspection Volume & Defect Trends
              </h3>
              <p className="text-xs text-slate-500">
                Daily inspection throughput vs detected defect volume
              </p>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.inspection_trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="totalGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563EB" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#2563EB" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="defectiveGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#64748B" }} />
                <YAxis tick={{ fontSize: 11, fill: "#64748B" }} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0F172A",
                    borderColor: "#334155",
                    color: "#fff",
                    borderRadius: "8px",
                    fontSize: "12px"
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="total"
                  name="Total Inspected"
                  stroke="#2563EB"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#totalGrad)"
                />
                <Area
                  type="monotone"
                  dataKey="defective"
                  name="Defective Units"
                  stroke="#EF4444"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#defectiveGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Defect Category Breakdown */}
        <div className="lg:col-span-5 bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                Defect Category Distribution
              </h3>
              <p className="text-xs text-slate-500">
                Frequency by metallurgical surface defect mode
              </p>
            </div>
          </div>
          <div className="h-64 w-full">
            {data.defect_distribution.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 bg-slate-50 rounded-lg border border-dashed border-slate-200">
                <CheckCircle2 className="w-8 h-8 text-emerald-500 mb-2" />
                <p className="text-xs font-bold text-slate-800">No Defects Recorded</p>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Execute inspection runs on defective components to populate breakdown.
                </p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={data.defect_distribution}
                  layout="vertical"
                  margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10, fill: "#64748B" }} allowDecimals={false} />
                  <YAxis
                    dataKey="name"
                    type="category"
                    tick={{ fontSize: 10, fill: "#334155", fontWeight: 600 }}
                    width={90}
                  />
                  <Tooltip
                    formatter={(val: any, name: any, item: any) => [
                      `${val} instances (${item.payload.percentage}%)`,
                      "Occurrences"
                    ]}
                    contentStyle={{
                      backgroundColor: "#0F172A",
                      borderColor: "#334155",
                      color: "#fff",
                      borderRadius: "8px",
                      fontSize: "12px"
                    }}
                  />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {data.defect_distribution.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Bottom Grid: Recent Inspections & System Readiness */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Inspections Table */}
        <div className="lg:col-span-8 bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                Recent Quality Inspection Records
              </h3>
              <p className="text-xs text-slate-500">
                Latest automated defect evaluations and engineering dispositions
              </p>
            </div>
            <button
              onClick={onNavigateToInspection}
              className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1 cursor-pointer"
            >
              Start New Inspection <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="py-2.5 px-3">Thumbnail</th>
                  <th className="py-2.5 px-3">Code</th>
                  <th className="py-2.5 px-3">Product Name</th>
                  <th className="py-2.5 px-3">Detected Defect</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Decision</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.recent_inspections.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-400">
                      <div className="max-w-xs mx-auto space-y-2">
                        <Layers className="w-8 h-8 mx-auto text-slate-300" />
                        <p className="font-semibold text-slate-700 text-xs">No Inspection Records Found</p>
                        <p className="text-[11px] text-slate-500">
                          Execute an optical inspection using sample defects or live camera to record evaluations.
                        </p>
                        <button
                          onClick={onNavigateToInspection}
                          className="mt-2 px-3.5 py-1.5 rounded-lg bg-blue-600 text-white text-xs font-bold hover:bg-blue-700 transition-colors cursor-pointer"
                        >
                          Launch First Inspection
                        </button>
                      </div>
                    </td>
                  </tr>
                ) : (
                  data.recent_inspections.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-2.5 px-3">
                        <div className="w-9 h-9 rounded bg-slate-900 overflow-hidden border border-slate-200 shrink-0">
                          <img
                            src={getAssetUrl(r.annotated_image_url || r.original_image_url)}
                            alt={r.product_name}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              // Fallback placeholder
                              (e.target as HTMLElement).style.display = "none";
                            }}
                          />
                        </div>
                      </td>
                      <td className="py-3 px-3 font-mono font-bold text-slate-900">
                        {r.inspection_code}
                      </td>
                      <td className="py-3 px-3 text-slate-700 font-medium">
                        {r.product_name}
                        <span className="block text-[10px] text-slate-400 font-normal">
                          {r.product_category}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-slate-700 font-semibold">
                        {r.defect_name}
                      </td>
                      <td className="py-3 px-3">
                        <SeverityBadge severity={r.max_severity} size="sm" />
                      </td>
                      <td className="py-3 px-3">
                        <DecisionBadge decision={r.overall_decision} size="sm" />
                      </td>
                      <td className="py-3 px-3 text-right space-x-1.5 whitespace-nowrap">
                        <button
                          onClick={() => handleOpenInspection(r.id)}
                          className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] font-semibold transition-colors cursor-pointer"
                        >
                          Details
                        </button>
                        <button
                          onClick={() => handleDownloadPdf(r.id)}
                          disabled={downloadingId === r.id}
                          className="p-1 rounded-md hover:bg-blue-50 text-slate-500 hover:text-blue-600 transition-colors inline-flex items-center disabled:opacity-50 cursor-pointer"
                          title="Download PDF"
                        >
                          <FileDown className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* System & Hardware Readiness Widget */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 tracking-tight mb-3 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-blue-600" />
              Inspection Hardware & Models
            </h3>
            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-slate-600 font-medium">Active Detection Model:</span>
                <span className="font-bold text-blue-700 font-mono">{data.active_model}</span>
              </div>
              <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-slate-600 font-medium">Compute Device:</span>
                <span className="font-semibold text-slate-800">{data.device_info}</span>
              </div>
              <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-slate-600 font-medium">Multimodal GenAI:</span>
                <span className={`font-semibold flex items-center gap-1.5 ${data.gemini_status ? "text-emerald-700" : "text-amber-700"}`}>
                  <Sparkles className="w-3.5 h-3.5" />
                  {data.gemini_status ? "Google Gemini (Active)" : "Rule-Based Engine"}
                </span>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <button
                onClick={onNavigateToModels}
                className="text-blue-600 font-semibold hover:underline cursor-pointer"
              >
                Model Details →
              </button>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 tracking-tight mb-3 flex items-center gap-2">
              <Database className="w-4 h-4 text-blue-600" />
              Dataset Benchmark Status
            </h3>
            <div className="space-y-2 text-xs">
              {Object.entries(data.dataset_status).map(([name, status]) => (
                <div
                  key={name}
                  className="flex items-center justify-between p-2 bg-slate-50 rounded-md border border-slate-100"
                >
                  <span className="font-semibold text-slate-700 uppercase font-mono text-[11px]">
                    {name.replace("_", "-")}
                  </span>
                  <span
                    className={`text-[11px] font-semibold ${
                      status.downloaded ? "text-emerald-700" : "text-slate-500"
                    }`}
                  >
                    {status.downloaded ? `Downloaded (${status.images} imgs)` : "Ready for Download"}
                  </span>
                </div>
              ))}
            </div>
            <div className="mt-3 pt-2 text-xs">
              <button
                onClick={onNavigateToDatasets}
                className="text-blue-600 font-semibold hover:underline cursor-pointer"
              >
                Manage Datasets →
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Inspection Modal */}
      <InspectionModal
        inspection={selectedInspection}
        onClose={() => setSelectedInspection(null)}
      />
    </div>
  );
};

