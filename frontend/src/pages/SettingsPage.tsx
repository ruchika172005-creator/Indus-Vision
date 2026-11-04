import React, { useEffect, useState } from "react";
import { ApiService } from "../services/api";
import { SystemSettings } from "../types";
import {
  Settings,
  Sparkles,
  Sliders,
  CheckCircle2,
  AlertCircle,
  Save,
  RotateCcw,
  ShieldCheck,
  Cpu,
  HardDrive,
  Info
} from "lucide-react";

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Form inputs
  const [geminiApiKey, setGeminiApiKey] = useState("");
  const [geminiModel, setGeminiModel] = useState("gemini-1.5-flash");
  const [confidenceThresh, setConfidenceThresh] = useState(0.35);
  const [iouThresh, setIouThresh] = useState(0.45);
  const [criticalArea, setCriticalArea] = useState(0.15);
  const [highArea, setHighArea] = useState(0.08);
  const [mediumArea, setMediumArea] = useState(0.03);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const data = await ApiService.getSettings();
      setSettings(data);
      setGeminiModel(data.gemini_model);
      setConfidenceThresh(data.confidence_threshold);
      setIouThresh(data.iou_threshold);
      setCriticalArea(data.critical_area_ratio);
      setHighArea(data.high_area_ratio);
      setMediumArea(data.medium_area_ratio);
    } catch (err) {
      console.error("Failed to load settings:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleResetDefaults = () => {
    setGeminiModel("gemini-1.5-flash");
    setConfidenceThresh(0.35);
    setIouThresh(0.45);
    setCriticalArea(0.15);
    setHighArea(0.08);
    setMediumArea(0.03);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);

    const payload: Partial<SystemSettings> = {
      gemini_model: geminiModel,
      confidence_threshold: confidenceThresh,
      iou_threshold: iouThresh,
      critical_area_ratio: criticalArea,
      high_area_ratio: highArea,
      medium_area_ratio: mediumArea
    };

    if (geminiApiKey.trim()) {
      (payload as any).gemini_api_key = geminiApiKey.trim();
    }

    try {
      const updated = await ApiService.updateSettings(payload);
      setSettings(updated);
      setSaveSuccess(true);
      setGeminiApiKey(""); // Clear input after successful save
      setTimeout(() => setSaveSuccess(false), 4000);
    } catch (err) {
      console.error("Failed to save settings:", err);
      alert("Failed to save settings. Check backend connection.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-slate-400">
        <span className="text-sm font-semibold">Loading Configuration...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <form onSubmit={handleSave} className="space-y-6">
        {saveSuccess && (
          <div className="p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs font-semibold flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            System parameters and thresholds updated successfully.
          </div>
        )}

        {/* Section 1: Multimodal Generative AI (Google Gemini) */}
        <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                  Multimodal Generative AI (Google Gemini API)
                </h3>
                <p className="text-xs text-slate-500">
                  Vision-language model interprets optical defect imagery and synthesizes root causes.
                </p>
              </div>
            </div>

            <span
              className={`text-[11px] font-bold px-2.5 py-1 rounded-full border ${
                settings?.gemini_api_key_configured
                  ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                  : "bg-amber-50 text-amber-700 border-amber-200"
              }`}
            >
              {settings?.gemini_api_key_configured ? "API Key Configured" : "Rule Fallback Active"}
            </span>
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Google AI Studio Gemini API Key
              </label>
              <input
                type="password"
                placeholder={
                  settings?.gemini_api_key_configured
                    ? "•••••••••••••••••••••••••••••••• (Leave blank to keep existing)"
                    : "Enter your Google AI Studio Gemini API Key..."
                }
                value={geminiApiKey}
                onChange={(e) => setGeminiApiKey(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-800 font-mono text-xs focus:ring-2 focus:ring-blue-500 focus:outline-hidden"
              />
              <p className="text-[11px] text-slate-400 mt-1">
                If no API key is provided, the application operates in 100% functional Rule-Based Industrial Expert mode.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Vision Model Architecture
                </label>
                <select
                  value={geminiModel}
                  onChange={(e) => setGeminiModel(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-800 font-medium bg-white"
                >
                  <option value="gemini-1.5-flash">gemini-1.5-flash (Fast & Recommended)</option>
                  <option value="gemini-1.5-pro">gemini-1.5-pro (In-depth Metallurgical Reasoning)</option>
                  <option value="gemini-2.0-flash">gemini-2.0-flash (Experimental)</option>
                </select>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 flex flex-col justify-center">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Active Mode</span>
                <span className="text-xs font-bold text-slate-800 mt-0.5">
                  {settings?.gemini_api_key_configured
                    ? "Multimodal Cloud VLM"
                    : "Local Metallurgical Domain Engine"}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: Defect Detection & Thresholds */}
        <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
          <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-slate-100">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                Computer Vision Detection Parameters
              </h3>
              <p className="text-xs text-slate-500">
                Confidence filtering and non-maximum suppression (IoU) overlap control.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
            <div>
              <div className="flex justify-between font-semibold text-slate-700 mb-1">
                <span>Default Confidence Threshold</span>
                <span className="font-mono text-blue-600">{(confidenceThresh * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.90"
                step="0.05"
                value={confidenceThresh}
                onChange={(e) => setConfidenceThresh(parseFloat(e.target.value))}
                className="w-full accent-blue-600 cursor-pointer"
              />
              <p className="text-[11px] text-slate-400 mt-1">
                Minimum detector confidence required to record a bounding box.
              </p>
            </div>

            <div>
              <div className="flex justify-between font-semibold text-slate-700 mb-1">
                <span>IoU (NMS Overlap Threshold)</span>
                <span className="font-mono text-blue-600">{(iouThresh * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.20"
                max="0.80"
                step="0.05"
                value={iouThresh}
                onChange={(e) => setIouThresh(parseFloat(e.target.value))}
                className="w-full accent-blue-600 cursor-pointer"
              />
              <p className="text-[11px] text-slate-400 mt-1">
                Overlapping boxes exceeding this ratio are merged.
              </p>
            </div>
          </div>
        </div>

        {/* Section 3: Explainable Severity Assessment Engine */}
        <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
          <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-slate-100">
            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                Severity Assessment Engine Thresholds
              </h3>
              <p className="text-xs text-slate-500">
                Transparent area ratio criteria used to categorize defect consequences (LOW, MEDIUM, HIGH, CRITICAL).
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-3 bg-rose-50/50 rounded-lg border border-rose-200/70">
              <span className="font-bold text-rose-800 block mb-1">CRITICAL Severity Area</span>
              <div className="flex justify-between font-mono text-rose-700 mb-1">
                <span>Trigger Ratio:</span>
                <strong>{(criticalArea * 100).toFixed(0)}%</strong>
              </div>
              <input
                type="range"
                min="0.08"
                max="0.30"
                step="0.01"
                value={criticalArea}
                onChange={(e) => setCriticalArea(parseFloat(e.target.value))}
                className="w-full accent-rose-600 cursor-pointer"
              />
            </div>

            <div className="p-3 bg-orange-50/50 rounded-lg border border-orange-200/70">
              <span className="font-bold text-orange-800 block mb-1">HIGH Severity Area</span>
              <div className="flex justify-between font-mono text-orange-700 mb-1">
                <span>Trigger Ratio:</span>
                <strong>{(highArea * 100).toFixed(0)}%</strong>
              </div>
              <input
                type="range"
                min="0.04"
                max="0.15"
                step="0.01"
                value={highArea}
                onChange={(e) => setHighArea(parseFloat(e.target.value))}
                className="w-full accent-orange-600 cursor-pointer"
              />
            </div>

            <div className="p-3 bg-amber-50/50 rounded-lg border border-amber-200/70">
              <span className="font-bold text-amber-800 block mb-1">MEDIUM Severity Area</span>
              <div className="flex justify-between font-mono text-amber-700 mb-1">
                <span>Trigger Ratio:</span>
                <strong>{(mediumArea * 100).toFixed(0)}%</strong>
              </div>
              <input
                type="range"
                min="0.01"
                max="0.06"
                step="0.005"
                value={mediumArea}
                onChange={(e) => setMediumArea(parseFloat(e.target.value))}
                className="w-full accent-amber-600 cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Section 4: System Information Card */}
        <div className="bg-slate-50 rounded-xl border border-slate-200 p-4 text-xs text-slate-600">
          <div className="flex items-center gap-2 mb-2 font-bold text-slate-800">
            <Info className="w-4 h-4 text-slate-500" />
            Host Diagnostics & Deployment Status
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 font-mono text-[11px]">
            <div>Platform: <strong>Windows / FastAPI</strong></div>
            <div>CUDA: <strong>{settings?.cuda_available ? "Enabled" : "CPU Fallback"}</strong></div>
            <div>Engine: <strong>Ultralytics YOLOv8</strong></div>
            <div>Version: <strong>{settings?.version || "1.0.0"}</strong></div>
          </div>
        </div>

        {/* Save Bar */}
        <div className="flex items-center justify-between gap-3 pt-2">
          <button
            type="button"
            onClick={handleResetDefaults}
            className="px-4 py-2.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold flex items-center gap-2 transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
            Reset to Recommended Defaults
          </button>

          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md shadow-blue-500/20 transition-all flex items-center gap-2 disabled:opacity-50 cursor-pointer"
          >
            <Save className="w-4 h-4" />
            {saving ? "Saving Changes..." : "Save System Configuration"}
          </button>
        </div>
      </form>
    </div>
  );
};
