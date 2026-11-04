import React, { useEffect, useState } from "react";
import { ApiService } from "../services/api";
import { DatasetItem } from "../types";
import { DatasetGuideModal } from "../components/DatasetGuideModal";
import {
  Database,
  Download,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  Layers,
  HardDrive,
  FileCode,
  FolderOpen,
  FolderTree,
  RefreshCw
} from "lucide-react";

export const DatasetManagementPage: React.FC = () => {
  const [datasets, setDatasets] = useState<DatasetItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDataset, setSelectedDataset] = useState<DatasetItem | null>(null);
  const [isPreparing, setIsPreparing] = useState(false);
  const [actionMessage, setActionMessage] = useState<{ text: string; error?: boolean } | null>(null);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const data = await ApiService.getDatasets();
      setDatasets(data);
    } catch (err) {
      console.error("Failed to load datasets:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handlePrepare = async (name: string) => {
    setIsPreparing(true);
    setActionMessage(null);
    try {
      const res = await ApiService.prepareDataset(name);
      setActionMessage({ text: res.message });
      await fetchDatasets();
    } catch (err: any) {
      setActionMessage({
        text: err?.response?.data?.detail || "Preparation failed. Raw dataset files not found on disk. Click 'Init Demo Samples' or follow the Download Guide.",
        error: true
      });
    } finally {
      setIsPreparing(false);
    }
  };

  const handleInitDemo = async (name: string) => {
    setIsPreparing(true);
    setActionMessage(null);
    try {
      const res = await ApiService.initDemoDataset(name);
      setActionMessage({ text: res.message });
      await fetchDatasets();
    } catch (err: any) {
      setActionMessage({
        text: err?.response?.data?.detail || "Failed to initialize demonstration samples.",
        error: true
      });
    } finally {
      setIsPreparing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header notice */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-900 tracking-tight">
            Industrial Defect Detection & Anomaly Benchmarks
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Verified download sources, Pascal VOC XML annotation parsing, and automated YOLO format partitioning.
          </p>
        </div>
        <button
          onClick={fetchDatasets}
          className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh Status
        </button>
      </div>

      {actionMessage && (
        <div
          className={`p-3.5 rounded-xl border text-xs font-semibold flex items-center gap-2 ${
            actionMessage.error
              ? "bg-rose-50 border-rose-200 text-rose-800"
              : "bg-emerald-50 border-emerald-200 text-emerald-800"
          }`}
        >
          {actionMessage.error ? (
            <AlertCircle className="w-4 h-4 shrink-0" />
          ) : (
            <CheckCircle className="w-4 h-4 shrink-0" />
          )}
          <span>{actionMessage.text}</span>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20 text-slate-400">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mb-2" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {datasets.map((dataset) => {
            return (
              <div
                key={dataset.id}
                className="bg-white rounded-xl border border-slate-200/90 shadow-xs hover:shadow-md transition-all flex flex-col overflow-hidden"
              >
                {/* Top Card Banner */}
                <div className="p-5 border-b border-slate-100 flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <span className="font-mono text-xs font-bold text-blue-600 uppercase tracking-wider bg-blue-50 px-2 py-0.5 rounded-md">
                      {dataset.name.replace("_", "-")}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full ${
                        dataset.is_downloaded
                          ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                          : "bg-amber-50 text-amber-700 border border-amber-200"
                      }`}
                    >
                      {dataset.is_downloaded ? (
                        <>
                          <CheckCircle className="w-3 h-3" /> Downloaded
                        </>
                      ) : (
                        <>
                          <AlertCircle className="w-3 h-3" /> Not on Disk
                        </>
                      )}
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-slate-900 leading-snug">
                    {dataset.display_name}
                  </h4>
                  <p className="text-xs text-slate-500 mt-2 line-clamp-2 leading-relaxed">
                    {dataset.description}
                  </p>

                  {/* Quantitative Stats */}
                  <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-slate-100 text-xs">
                    <div className="p-2 bg-slate-50 rounded-lg">
                      <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                        Total Images
                      </span>
                      <span className="font-bold text-slate-800 text-sm">
                        {dataset.total_images}
                      </span>
                    </div>

                    <div className="p-2 bg-slate-50 rounded-lg">
                      <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                        Defect Classes
                      </span>
                      <span className="font-bold text-slate-800 text-sm">
                        {dataset.num_classes} classes
                      </span>
                    </div>

                    <div className="p-2 bg-slate-50 rounded-lg">
                      <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                        Disk Size
                      </span>
                      <span className="font-bold text-slate-800 text-sm">
                        {dataset.disk_size_mb} MB
                      </span>
                    </div>

                    <div className="p-2 bg-slate-50 rounded-lg">
                      <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                        YOLO Splits
                      </span>
                      <span
                        className={`font-bold text-xs ${
                          dataset.is_prepared ? "text-emerald-700" : "text-slate-500"
                        }`}
                      >
                        {dataset.is_prepared ? "Prepared" : "Not Built"}
                      </span>
                    </div>
                  </div>

                  {/* Classes tags */}
                  <div className="mt-4">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase block mb-1.5">
                      Class Definitions:
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {dataset.classes.slice(0, 6).map((c) => (
                        <span
                          key={c}
                          className="px-2 py-0.5 rounded-sm bg-slate-100 text-slate-700 font-medium text-[10px]"
                        >
                          {c}
                        </span>
                      ))}
                      {dataset.classes.length > 6 && (
                        <span className="px-1.5 py-0.5 text-slate-400 text-[10px]">
                          +{dataset.classes.length - 6} more
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Card Action Buttons */}
                <div className="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between gap-2">
                  <button
                    onClick={() => setSelectedDataset(dataset)}
                    className="flex-1 py-1.5 px-3 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition-colors flex items-center justify-center gap-1.5"
                  >
                    <FolderOpen className="w-3.5 h-3.5 text-slate-500" />
                    Download Guide
                  </button>

                  {dataset.name !== "mvtec_ad" && (
                    dataset.is_downloaded ? (
                      <button
                        onClick={() => handlePrepare(dataset.name)}
                        disabled={isPreparing}
                        className="py-1.5 px-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition-colors disabled:opacity-50 flex items-center gap-1.5 shadow-xs"
                      >
                        <Layers className="w-3.5 h-3.5" />
                        {isPreparing ? "Working..." : "Prepare Splits"}
                      </button>
                    ) : (
                      <button
                        onClick={() => handleInitDemo(dataset.name)}
                        disabled={isPreparing}
                        className="py-1.5 px-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-colors disabled:opacity-50 flex items-center gap-1.5 shadow-xs"
                        title="Populate authentic demonstration samples with Pascal VOC annotations to test conversion without downloading 500MB"
                      >
                        <FolderTree className="w-3.5 h-3.5" />
                        {isPreparing ? "Initializing..." : "Init Demo Samples"}
                      </button>
                    )
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Dataset Guide Modal */}
      <DatasetGuideModal
        dataset={selectedDataset}
        onClose={() => setSelectedDataset(null)}
        onPrepare={handlePrepare}
        onInitDemo={handleInitDemo}
        isPreparing={isPreparing}
      />
    </div>
  );
};
