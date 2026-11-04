import React, { useEffect, useState } from "react";
import { ApiService, getAssetUrl } from "../services/api";
import { ReportItem, Inspection } from "../types";
import {
  FileText,
  Download,
  FileDown,
  Table,
  CheckCircle,
  Clock,
  Layers,
  RefreshCw,
  ExternalLink,
  Search,
  AlertCircle
} from "lucide-react";

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [recentInspections, setRecentInspections] = useState<Inspection[]>([]);
  const [loading, setLoading] = useState(true);
  const [generatingId, setGeneratingId] = useState<number | null>(null);
  const [reportSearch, setReportSearch] = useState("");
  const [successBanner, setSuccessBanner] = useState<string | null>(null);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const [reps, insp] = await Promise.all([
        ApiService.getReports(),
        ApiService.getHistory({ limit: 10 })
      ]);
      setReports(reps);
      setRecentInspections(insp);
    } catch (err) {
      console.error("Failed to load reports:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleGeneratePdf = async (inspectionId: number) => {
    setGeneratingId(inspectionId);
    setSuccessBanner(null);
    try {
      const res = await ApiService.createPdfReport(inspectionId);
      await fetchReports();
      setSuccessBanner(`Report '${res.filename}' successfully compiled with ReportLab.`);
      if (res.download_url) {
        window.open(getAssetUrl(res.download_url), "_blank");
      }
      setTimeout(() => setSuccessBanner(null), 5000);
    } catch (err) {
      console.error("Failed to generate report:", err);
      alert("Error generating PDF audit report. Please check server logs.");
    } finally {
      setGeneratingId(null);
    }
  };

  const handleExportCsv = () => {
    window.open(ApiService.getExportCsvUrl(), "_blank");
  };

  const filteredReports = reports.filter((r) =>
    r.filename.toLowerCase().includes(reportSearch.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Export Banner */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 tracking-tight">
            Quality Assurance Compliance & Export Hub
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Generate formal ISO 9001 audit PDF reports with embedded defect telemetry or export datasets to CSV.
          </p>
        </div>

        <button
          onClick={handleExportCsv}
          className="px-4 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold flex items-center gap-2 shadow-xs transition-colors shrink-0 cursor-pointer"
        >
          <Table className="w-4 h-4" />
          Export All Inspections to CSV
        </button>
      </div>

      {successBanner && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs font-semibold flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{successBanner}</span>
        </div>
      )}

      {/* Row 1: Generate Report on Recent Inspections */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
        <h3 className="text-sm font-bold text-slate-900 tracking-tight mb-1">
          Generate PDF Audit Report
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Select an inspection below to compile its optical localization and GenAI explanation into a formal ReportLab PDF.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-semibold border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Inspection Code</th>
                <th className="py-2.5 px-3">Component Name</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Defect Found</th>
                <th className="py-2.5 px-3">Decision</th>
                <th className="py-2.5 px-3 text-right">Generate Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {recentInspections.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-10 text-center text-slate-400">
                    <Layers className="w-8 h-8 mx-auto text-slate-300 mb-2" />
                    No inspection records available to compile. Run an optical inspection first.
                  </td>
                </tr>
              ) : (
                recentInspections.map((i) => (
                  <tr key={i.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-2.5 px-3 font-mono font-bold text-slate-900">
                      {i.inspection_code}
                    </td>
                    <td className="py-2.5 px-3 text-slate-800">{i.product_name}</td>
                    <td className="py-2.5 px-3 text-slate-500">{i.product_category}</td>
                    <td className="py-2.5 px-3 font-semibold text-slate-700">
                      {i.explanation?.defect_name || (i.defects[0]?.defect_name ?? "Clean")}
                    </td>
                    <td className="py-2.5 px-3 font-bold">
                      <span
                        className={`text-[11px] ${
                          i.overall_decision === "PASS"
                            ? "text-emerald-700"
                            : i.overall_decision === "FAIL"
                            ? "text-rose-700"
                            : "text-amber-700"
                        }`}
                      >
                        {i.overall_decision}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <button
                        onClick={() => handleGeneratePdf(i.id)}
                        disabled={generatingId === i.id}
                        className="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 font-bold text-[11px] transition-colors disabled:opacity-50 inline-flex items-center gap-1.5 cursor-pointer"
                      >
                        <FileDown className="w-3.5 h-3.5" />
                        {generatingId === i.id ? "Compiling PDF..." : "Generate PDF"}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Row 2: Generated Reports Archive Table */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">
              Generated Reports Library
            </h3>
            <p className="text-xs text-slate-500">
              Previously synthesized quality inspection documents stored on server
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative w-48">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search PDF filename..."
                value={reportSearch}
                onChange={(e) => setReportSearch(e.target.value)}
                className="w-full pl-8 pr-3 py-1 rounded-lg border border-slate-200 text-xs text-slate-800 font-medium focus:ring-2 focus:ring-blue-500 focus:outline-hidden"
              />
            </div>
            <button
              onClick={fetchReports}
              className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition-colors cursor-pointer"
              title="Refresh Reports"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {filteredReports.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-xs">
            <FileText className="w-8 h-8 mx-auto text-slate-300 mb-2" />
            {reportSearch
              ? `No reports found matching '${reportSearch}'.`
              : 'No PDF reports generated yet. Click "Generate PDF" on any inspection above.'}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Filename</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">File Size</th>
                  <th className="py-2.5 px-3">Generated At</th>
                  <th className="py-2.5 px-3 text-right">Download</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {filteredReports.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-2.5 px-3 font-mono font-bold text-slate-800 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-blue-600 shrink-0" />
                      {r.filename}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded-sm bg-slate-100 text-slate-700 font-bold text-[10px]">
                        {r.report_type}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-600 font-mono">
                      {r.file_size_kb} KB
                    </td>
                    <td className="py-2.5 px-3 text-slate-500">
                      {new Date(r.generated_at).toLocaleString()}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <a
                        href={getAssetUrl(r.download_url)}
                        target="_blank"
                        rel="noreferrer"
                        className="px-3 py-1 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold inline-flex items-center gap-1.5 transition-colors"
                      >
                        <Download className="w-3.5 h-3.5" />
                        Download
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

