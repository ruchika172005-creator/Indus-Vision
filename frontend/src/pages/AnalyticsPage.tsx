import React, { useEffect, useState } from "react";
import { ApiService } from "../services/api";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line
} from "recharts";
import { BarChart3, TrendingUp, AlertOctagon, CheckCircle2, RefreshCw, Radio, Factory } from "lucide-react";
import { ProductionLineConfig } from "../types";

const PIE_COLORS = ["#2563EB", "#0284C7", "#0D9488", "#10B981", "#F59E0B", "#F97316", "#8B5CF6"];

const SEV_COLOR_MAP: Record<string, string> = {
  LOW: "#10B981",
  MEDIUM: "#F59E0B",
  HIGH: "#F97316",
  CRITICAL: "#EF4444"
};

interface Props {
  currentLine?: ProductionLineConfig;
}

export const AnalyticsPage: React.FC<Props> = ({ currentLine }) => {
  const [defectData, setDefectData] = useState<any>(null);
  const [trendData, setTrendData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [periodDays, setPeriodDays] = useState<number>(14);

  const fetchAnalytics = async (days: number = periodDays) => {
    try {
      setLoading(true);
      const [defects, trends] = await Promise.all([
        ApiService.getDefectAnalytics(),
        ApiService.getTrendAnalytics(days)
      ]);
      setDefectData(defects);
      setTrendData(trends.trends);
    } catch (err) {
      console.error("Failed to load analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics(periodDays);
  }, [periodDays]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-slate-400">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mb-3" />
        <span className="text-sm font-bold text-slate-700">Synthesizing Statistical Process Quality Telemetry...</span>
        <p className="text-xs text-slate-400 mt-1">Aggregating failure modes and severity distributions</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Analytics Toolbar */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">
              Statistical Process Control (SPC) & Quality Trends
            </h3>
            <div className="flex items-center gap-2 flex-wrap text-xs text-slate-500">
              <span>Quantitative yield telemetry, Pareto failure ranking, and multi-day defect rates</span>
              {currentLine && (
                <>
                  <span>•</span>
                  <span className="inline-flex items-center gap-1 font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                    <Factory className="w-3 h-3 text-blue-600" />
                    Facility: {currentLine.name} ({currentLine.category})
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="inline-flex p-1 bg-slate-100 rounded-lg text-xs font-semibold">
            {[7, 14, 30].map((d) => (
              <button
                key={d}
                onClick={() => setPeriodDays(d)}
                className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
                  periodDays === d
                    ? "bg-white text-blue-600 shadow-xs font-bold"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {d} Days
              </button>
            ))}
          </div>

          <button
            onClick={() => fetchAnalytics(periodDays)}
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition-colors cursor-pointer"
            title="Refresh Analytics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Analytics Summary Banner */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200/90 shadow-xs">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
            Total Inspected
          </span>
          <h3 className="text-2xl font-bold text-slate-900">{defectData?.total_analyzed || 0}</h3>
          <p className="text-[11px] text-slate-400 mt-1">Processed components in window</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/90 shadow-xs">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
            Total Defect Instances
          </span>
          <h3 className="text-2xl font-bold text-slate-900">{defectData?.total_defects_found || 0}</h3>
          <p className="text-[11px] text-slate-400 mt-1">Isolated defect anomalies</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/90 shadow-xs">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
            Process Defect Rate
          </span>
          <h3 className="text-2xl font-bold text-amber-600">{defectData?.defect_rate_overall || 0}%</h3>
          <p className="text-[11px] text-slate-400 mt-1">First-pass rejection ratio</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/90 shadow-xs">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
            Top Failure Mode
          </span>
          <h3 className="text-xl font-bold text-slate-900 truncate">
            {defectData?.most_frequent?.[0]?.name || "None"}
          </h3>
          <p className="text-[11px] text-slate-400 mt-1">
            {defectData?.most_frequent?.[0]?.percentage || 0}% of all defects
          </p>
        </div>
      </div>

      {/* Row 1: Defect Distribution Donut + Severity Distribution Bar */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Category Donut Chart */}
        <div className="lg:col-span-6 bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
          <h3 className="text-sm font-bold text-slate-900 tracking-tight mb-1">
            Defect Mode Proportion
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            Percentage breakdown of detected surface defect categories
          </p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={defectData?.by_category || []}
                  dataKey="count"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                >
                  {(defectData?.by_category || []).map((_: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: any, name: any, item: any) => [
                    `${val} instances (${item.payload.percentage}%)`,
                    item.payload.name
                  ]}
                  contentStyle={{
                    backgroundColor: "#0F172A",
                    borderColor: "#334155",
                    color: "#fff",
                    borderRadius: "8px",
                    fontSize: "12px"
                  }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Bar Chart */}
        <div className="lg:col-span-6 bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
          <h3 className="text-sm font-bold text-slate-900 tracking-tight mb-1">
            Defects by Evaluated Severity Level
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            Volume of anomalies categorized by structural engineering risk
          </p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={defectData?.by_severity || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="severity" tick={{ fontSize: 11, fill: "#64748B", fontWeight: 600 }} />
                <YAxis tick={{ fontSize: 11, fill: "#64748B" }} allowDecimals={false} />
                <Tooltip
                  formatter={(val: any, name: any, item: any) => [
                    `${val} defects (${item.payload.percentage}%)`,
                    item.payload.severity
                  ]}
                  contentStyle={{
                    backgroundColor: "#0F172A",
                    borderColor: "#334155",
                    color: "#fff",
                    borderRadius: "8px",
                    fontSize: "12px"
                  }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {(defectData?.by_severity || []).map((entry: any, index: number) => (
                    <Cell
                      key={`sev-${index}`}
                      fill={SEV_COLOR_MAP[entry.severity] || "#2563EB"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 2: 14-Day Production Defect Rate Trend */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
        <h3 className="text-sm font-bold text-slate-900 tracking-tight mb-1">
          14-Day Manufacturing Defect Rate Trend
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Daily percentage of parts requiring quarantine or manual engineering review
        </p>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendData} margin={{ top: 10, right: 15, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#64748B" }} />
              <YAxis unit="%" tick={{ fontSize: 11, fill: "#64748B" }} />
              <Tooltip
                formatter={(val: any) => [`${val}%`, "Defect Rate"]}
                contentStyle={{
                  backgroundColor: "#0F172A",
                  borderColor: "#334155",
                  color: "#fff",
                  borderRadius: "8px",
                  fontSize: "12px"
                }}
              />
              <Line
                type="monotone"
                dataKey="defect_rate"
                name="Defect Rate %"
                stroke="#F97316"
                strokeWidth={2.5}
                dot={{ r: 3, fill: "#F97316" }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 3: Top 5 Failure Modes Table */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">
              Top Failure Modes (Pareto 80/20 Distribution Ranking)
            </h3>
            <p className="text-xs text-slate-500">
              Isolates the vital 20% of defect modes driving 80% of manufacturing yield loss
            </p>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-semibold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Rank</th>
                <th className="py-2.5 px-3">Defect Category</th>
                <th className="py-2.5 px-3">Occurrences</th>
                <th className="py-2.5 px-3">Proportion</th>
                <th className="py-2.5 px-3">Cumulative</th>
                <th className="py-2.5 px-3">Primary Countermeasure</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {(() => {
                let cum = 0;
                const items = defectData?.most_frequent || [];
                if (items.length === 0) {
                  return (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-slate-400">
                        No failure modes recorded. All inspected parts meet quality standards.
                      </td>
                    </tr>
                  );
                }
                return items.map((item: any, idx: number) => {
                  cum += Number(item.percentage) || 0;
                  const cumRounded = Math.min(100, Math.round(cum * 10) / 10);
                  const isVitalFew = cumRounded <= 80;
                  return (
                    <tr key={idx} className="hover:bg-slate-50/70">
                      <td className="py-2.5 px-3 font-mono font-bold text-blue-600">#{idx + 1}</td>
                      <td className="py-2.5 px-3 font-bold text-slate-900">{item.name}</td>
                      <td className="py-2.5 px-3 text-slate-700">{item.count} parts</td>
                      <td className="py-2.5 px-3 font-mono text-slate-800">{item.percentage}%</td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`text-[11px] font-mono font-bold px-2 py-0.5 rounded ${
                            isVitalFew
                              ? "bg-amber-50 text-amber-800 border border-amber-200"
                              : "bg-slate-100 text-slate-700"
                          }`}
                        >
                          {cumRounded}%
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-slate-600 text-[11px]">
                        {item.name.toLowerCase().includes("scratch")
                          ? "Polish guide plates & check line strip tension"
                          : item.name.toLowerCase().includes("crazing")
                          ? "Descale work roll cooling nozzles on Stand 3-4"
                          : item.name.toLowerCase().includes("inclusion")
                          ? "Audit tundish refractory wear & argon flow rate"
                          : item.name.toLowerCase().includes("patch")
                          ? "Calibrate descaling pump water pressure transducers"
                          : item.name.toLowerCase().includes("pitted")
                          ? "Regulate acid pickling temperature and bath immersion duration"
                          : item.name.toLowerCase().includes("rolled")
                          ? "Inspect descaler header pressure and work roll profile wear"
                          : "Perform visual profilometry & adjust roll alignment"}
                      </td>
                    </tr>
                  );
                });
              })()}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
