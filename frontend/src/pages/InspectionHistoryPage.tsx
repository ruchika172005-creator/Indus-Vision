import React, { useEffect, useState } from "react";
import { ApiService, getAssetUrl } from "../services/api";
import { Inspection, ProductionLineConfig } from "../types";
import { SeverityBadge } from "../components/SeverityBadge";
import { DecisionBadge } from "../components/DecisionBadge";
import { InspectionModal } from "../components/InspectionModal";
import {
  Search,
  Filter,
  FileDown,
  Trash2,
  RefreshCw,
  Eye,
  Calendar,
  Layers,
  Table,
  X,
  AlertTriangle,
  Factory
} from "lucide-react";

interface Props {
  currentLine?: ProductionLineConfig;
}

export const InspectionHistoryPage: React.FC<Props> = ({ currentLine }) => {
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [decisionFilter, setDecisionFilter] = useState("ALL");
  const [selectedInspection, setSelectedInspection] = useState<Inspection | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const data = await ApiService.getHistory({
        search: search.trim() || undefined,
        severity: severityFilter,
        decision: decisionFilter
      });
      setInspections(data);
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [severityFilter, decisionFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchHistory();
  };

  const handleClearFilters = () => {
    setSearch("");
    setSeverityFilter("ALL");
    setDecisionFilter("ALL");
  };

  const handleConfirmDelete = async () => {
    if (!deleteConfirmId) return;
    try {
      setDeleting(true);
      await ApiService.deleteInspection(deleteConfirmId);
      setInspections(inspections.filter((i) => i.id !== deleteConfirmId));
      setDeleteConfirmId(null);
    } catch (err) {
      console.error("Failed to delete inspection:", err);
      alert("Failed to delete inspection record.");
    } finally {
      setDeleting(false);
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
      console.error("Failed to download PDF:", err);
      alert("Error generating PDF report.");
    } finally {
      setDownloadingId(null);
    }
  };

  const hasActiveFilters = Boolean(search.trim() || severityFilter !== "ALL" || decisionFilter !== "ALL");

  return (
    <div className="space-y-6">
      {/* Search and Filters Toolbar */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-xs flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by code, product, or defect..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 text-xs text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-blue-500 font-medium"
          />
        </form>

        {/* Filter Dropdowns & Batch Actions */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto justify-end">
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-500 font-semibold">Severity:</span>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-700 bg-white font-medium"
            >
              <option value="ALL">All Severities</option>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-500 font-semibold">Decision:</span>
            <select
              value={decisionFilter}
              onChange={(e) => setDecisionFilter(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-700 bg-white font-medium"
            >
              <option value="ALL">All Decisions</option>
              <option value="PASS">Pass</option>
              <option value="FAIL">Fail</option>
              <option value="MANUAL_REVIEW">Manual Review</option>
            </select>
          </div>

          {hasActiveFilters && (
            <button
              onClick={handleClearFilters}
              className="px-2.5 py-1.5 rounded-lg border border-rose-200 bg-rose-50 hover:bg-rose-100 text-rose-700 text-xs font-semibold flex items-center gap-1 transition-colors cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
              Reset Filters
            </button>
          )}

          <a
            href={ApiService.getExportCsvUrl()}
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <Table className="w-3.5 h-3.5 text-slate-500" />
            Export CSV
          </a>

          <button
            onClick={fetchHistory}
            className="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition-colors cursor-pointer"
            title="Refresh Records"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-blue-600" : ""}`} />
          </button>
        </div>
      </div>

      {/* Counter bar */}
      <div className="flex items-center justify-between text-xs text-slate-500 px-1">
        <span>
          Showing <strong>{inspections.length}</strong> inspection records
          {hasActiveFilters && " (Filtered)"}
        </span>
        <span className="font-mono text-[11px]">ISO 9001 Optical Inspection Log</span>
      </div>

      {/* History Table */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-3">Thumbnail</th>
                <th className="py-3 px-3">Inspection ID</th>
                <th className="py-3 px-3">Timestamp</th>
                <th className="py-3 px-3">Component</th>
                <th className="py-3 px-3">Detected Defect</th>
                <th className="py-3 px-3">Severity</th>
                <th className="py-3 px-3">Confidence</th>
                <th className="py-3 px-3">Decision</th>
                <th className="py-3 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-16 text-center text-slate-400">
                    <RefreshCw className="w-7 h-7 animate-spin mx-auto mb-2 text-blue-600" />
                    <span className="font-semibold text-slate-700 text-xs">Querying historical database records...</span>
                  </td>
                </tr>
              ) : inspections.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-16 text-center text-slate-400">
                    <div className="max-w-xs mx-auto space-y-2">
                      <Layers className="w-8 h-8 mx-auto text-slate-300" />
                      <p className="font-bold text-slate-700 text-xs">No Matching Inspection Logs</p>
                      <p className="text-[11px] text-slate-500">
                        {hasActiveFilters
                          ? "No records matched your search filters. Try clearing your filters."
                          : "No inspections recorded yet in the database."}
                      </p>
                      {hasActiveFilters && (
                        <button
                          onClick={handleClearFilters}
                          className="mt-2 px-3 py-1.5 rounded-lg bg-blue-600 text-white text-xs font-semibold hover:bg-blue-700 transition-colors cursor-pointer"
                        >
                          Clear All Filters
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ) : (
                inspections.map((insp) => (
                  <tr key={insp.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-2.5 px-3">
                      <div className="w-9 h-9 rounded bg-slate-900 overflow-hidden border border-slate-200 shrink-0">
                        <img
                          src={getAssetUrl(insp.annotated_image_url || insp.original_image_url)}
                          alt={insp.product_name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            (e.target as HTMLElement).style.display = "none";
                          }}
                        />
                      </div>
                    </td>
                    <td className="py-3 px-3 font-mono font-bold text-slate-900">
                      {insp.inspection_code}
                    </td>
                    <td className="py-3 px-3 text-slate-500 whitespace-nowrap">
                      {new Date(insp.timestamp).toLocaleString(undefined, {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit"
                      })}
                    </td>
                    <td className="py-3 px-3 text-slate-800 font-medium">
                      {insp.product_name}
                      <span className="block text-[10px] text-slate-400 font-normal">
                        {insp.product_category}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-semibold text-slate-800">
                      {insp.explanation?.defect_name || (insp.defects.length > 0 ? insp.defects[0].defect_name : "None")}
                    </td>
                    <td className="py-3 px-3">
                      <SeverityBadge severity={insp.max_severity} size="sm" />
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-600 font-semibold">
                      {(insp.confidence_avg * 100).toFixed(0)}%
                    </td>
                    <td className="py-3 px-3">
                      <DecisionBadge decision={insp.overall_decision} size="sm" />
                    </td>
                    <td className="py-3 px-3 text-right space-x-1.5 whitespace-nowrap">
                      <button
                        onClick={() => setSelectedInspection(insp)}
                        className="p-1.5 rounded-md hover:bg-blue-50 text-slate-600 hover:text-blue-600 transition-colors cursor-pointer"
                        title="View Full Inspection"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDownloadPdf(insp.id)}
                        disabled={downloadingId === insp.id}
                        className="p-1.5 rounded-md hover:bg-emerald-50 text-slate-600 hover:text-emerald-600 transition-colors inline-flex items-center disabled:opacity-50 cursor-pointer"
                        title="Download PDF"
                      >
                        <FileDown className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setDeleteConfirmId(insp.id)}
                        className="p-1.5 rounded-md hover:bg-rose-50 text-slate-400 hover:text-rose-600 transition-colors cursor-pointer"
                        title="Delete Record"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Custom Delete Confirmation Modal */}
      {deleteConfirmId !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 max-w-sm w-full p-6 text-center animate-in fade-in zoom-in-95 duration-150">
            <div className="w-12 h-12 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center mx-auto mb-3">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-slate-900 mb-1">Delete Inspection Record</h3>
            <p className="text-xs text-slate-500 mb-5 leading-relaxed">
              Are you sure you want to permanently delete inspection record <strong>#{deleteConfirmId}</strong>? This action cannot be undone.
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="flex-1 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDelete}
                disabled={deleting}
                className="flex-1 py-2 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition-colors cursor-pointer disabled:opacity-50"
              >
                {deleting ? "Deleting..." : "Delete Permanently"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Inspection Modal */}
      <InspectionModal
        inspection={selectedInspection}
        onClose={() => setSelectedInspection(null)}
      />
    </div>
  );
};

