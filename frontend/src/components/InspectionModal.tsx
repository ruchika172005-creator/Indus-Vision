import React, { useState } from "react";
import { Inspection } from "../types";
import { SeverityBadge } from "./SeverityBadge";
import { DecisionBadge } from "./DecisionBadge";
import { getAssetUrl, ApiService } from "../services/api";
import {
  X,
  FileDown,
  Sparkles,
  Layers,
  Clock,
  Cpu,
  ShieldCheck,
  CheckCircle,
  AlertCircle
} from "lucide-react";

interface Props {
  inspection: Inspection | null;
  onClose: () => void;
}

export const InspectionModal: React.FC<Props> = ({ inspection, onClose }) => {
  const [viewMode, setViewMode] = useState<"annotated" | "original">("annotated");
  const [downloading, setDownloading] = useState(false);

  if (!inspection) return null;

  const handleDownloadPdf = async () => {
    try {
      setDownloading(true);
      const res = await ApiService.createPdfReport(inspection.id);
      if (res.download_url) {
        window.open(getAssetUrl(res.download_url), "_blank");
      }
    } catch (err) {
      console.error("Failed to generate PDF report:", err);
      alert("Failed to generate PDF report. Check server logs.");
    } finally {
      setDownloading(false);
    }
  };

  const currentImgUrl =
    viewMode === "annotated" && inspection.annotated_image_url
      ? getAssetUrl(inspection.annotated_image_url)
      : getAssetUrl(inspection.original_image_url);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-5xl max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-base font-bold tracking-tight">
                Inspection Details: {inspection.inspection_code}
              </h2>
              <p className="text-xs text-slate-400">
                {inspection.product_name} • {inspection.product_category} •{" "}
                {new Date(inspection.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <DecisionBadge decision={inspection.overall_decision} size="md" />
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50">
          {/* Top telemetry bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
            <div>
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Max Severity</span>
              <div className="mt-1">
                <SeverityBadge severity={inspection.max_severity} size="sm" />
              </div>
            </div>
            <div>
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Total Defects</span>
              <p className="text-sm font-bold text-slate-800 mt-1">{inspection.total_defects}</p>
            </div>
            <div>
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Detection Model</span>
              <p className="text-sm font-semibold text-slate-800 mt-1 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-blue-600" />
                {inspection.model_name}
              </p>
            </div>
            <div>
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Inference Time</span>
              <p className="text-sm font-semibold text-slate-800 mt-1 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                {inspection.inference_time_ms} ms
              </p>
            </div>
          </div>

          {/* Image & Defects Split */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Image Preview */}
            <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200/80 p-4 shadow-xs flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                  <Layers className="w-4 h-4 text-blue-600" />
                  Optical Inspection Imagery
                </span>
                <div className="inline-flex p-1 bg-slate-100 rounded-lg text-xs font-medium">
                  <button
                    onClick={() => setViewMode("annotated")}
                    className={`px-3 py-1 rounded-md transition-all ${
                      viewMode === "annotated"
                        ? "bg-white text-blue-600 shadow-xs font-semibold"
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    Annotated
                  </button>
                  <button
                    onClick={() => setViewMode("original")}
                    className={`px-3 py-1 rounded-md transition-all ${
                      viewMode === "original"
                        ? "bg-white text-blue-600 shadow-xs font-semibold"
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    Original
                  </button>
                </div>
              </div>

              <div className="flex-1 bg-slate-950 rounded-lg overflow-hidden flex items-center justify-center min-h-[320px] relative border border-slate-800">
                <img
                  src={currentImgUrl}
                  alt="Inspection Part"
                  className="max-h-[380px] w-auto object-contain"
                />
                {inspection.is_demo && (
                  <div className="absolute top-3 left-3 bg-blue-600/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-sm tracking-wide uppercase shadow-sm">
                    Verified Demo Dataset Sample
                  </div>
                )}
              </div>
            </div>

            {/* Defect Telemetry List */}
            <div className="lg:col-span-5 bg-white rounded-xl border border-slate-200/80 p-4 shadow-xs flex flex-col">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
                Detected Defect Instances ({inspection.defects.length})
              </span>

              {inspection.defects.length === 0 ? (
                <div className="flex-1 flex flex-col items-center justify-center p-6 text-center bg-emerald-50/50 rounded-lg border border-emerald-100">
                  <CheckCircle className="w-10 h-10 text-emerald-500 mb-2" />
                  <p className="text-sm font-bold text-emerald-900">Zero Defects Detected</p>
                  <p className="text-xs text-emerald-700 mt-1">
                    Component meets all optical tolerance specifications.
                  </p>
                </div>
              ) : (
                <div className="space-y-2.5 overflow-y-auto max-h-[340px] pr-1">
                  {inspection.defects.map((d, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-xs font-bold text-slate-800">{d.defect_name}</span>
                        <SeverityBadge severity={d.severity_level} size="sm" />
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-500 font-mono mt-1">
                        <div>Conf: {(d.confidence * 100).toFixed(1)}%</div>
                        <div>Area: {(d.area_ratio * 100).toFixed(2)}%</div>
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono mt-1">
                        Box: [{d.bbox.map((n) => Math.round(n)).join(", ")}]
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Multimodal GenAI Defect Explanation Card */}
          {inspection.explanation && (
            <div className="bg-white rounded-xl border border-blue-200 p-5 shadow-xs relative overflow-hidden">
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500" />
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-blue-600" />
                  <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                    Multimodal AI Defect Explanation & Recommendations
                  </h4>
                </div>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-medium">
                  {inspection.explanation.provider_used}
                </span>
              </div>

              <div className="space-y-4 text-xs">
                <div>
                  <span className="font-semibold text-slate-700">Observed Characteristics:</span>
                  <p className="text-slate-600 mt-1 leading-relaxed bg-slate-50 p-2.5 rounded-md border border-slate-100">
                    {inspection.explanation.description} (Location: {inspection.explanation.location})
                  </p>
                </div>

                {inspection.explanation.possible_causes && inspection.explanation.possible_causes.length > 0 && (
                  <div>
                    <span className="font-semibold text-slate-700">Possible Causes (Engineering Hypotheses):</span>
                    <ul className="mt-1 space-y-1 list-disc list-inside text-slate-600 bg-slate-50 p-2.5 rounded-md border border-slate-100">
                      {inspection.explanation.possible_causes.map((c, i) => (
                        <li key={i}>{c}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {inspection.explanation.recommended_actions && inspection.explanation.recommended_actions.length > 0 && (
                  <div>
                    <span className="font-semibold text-slate-700">Recommended Corrective Actions:</span>
                    <ul className="mt-1 space-y-1 list-disc list-inside text-slate-600 bg-slate-50 p-2.5 rounded-md border border-slate-100">
                      {inspection.explanation.recommended_actions.map((a, i) => (
                        <li key={i}>{a}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {inspection.explanation.quality_summary && (
                  <div className="p-3 bg-blue-50/70 rounded-lg border border-blue-100 text-blue-950 font-medium">
                    <span className="font-bold">Engineering Disposition: </span>
                    {inspection.explanation.quality_summary}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 bg-white border-t border-slate-200 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            Source: <strong className="text-slate-700">{inspection.inference_source}</strong>
          </span>
          <div className="flex items-center gap-3">
            <button
              onClick={handleDownloadPdf}
              disabled={downloading}
              className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold text-xs flex items-center gap-2 hover:bg-blue-700 transition-colors shadow-xs disabled:opacity-50"
            >
              <FileDown className="w-4 h-4" />
              {downloading ? "Generating PDF..." : "Download Official PDF Report"}
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-slate-100 text-slate-700 font-semibold text-xs hover:bg-slate-200 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
