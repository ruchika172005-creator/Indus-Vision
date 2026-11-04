import React, { useEffect, useState } from "react";
import { ApiService } from "../services/api";
import { ModelItem, TrainingJobStatus, DatasetItem } from "../types";
import {
  Cpu,
  Play,
  CheckCircle,
  AlertCircle,
  AlertTriangle,
  Layers,
  HardDrive,
  BarChart,
  RefreshCw,
  Zap,
  Clock,
  Sparkles
} from "lucide-react";

export const ModelManagementPage: React.FC = () => {
  const [models, setModels] = useState<ModelItem[]>([]);
  const [datasets, setDatasets] = useState<DatasetItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Training form state
  const [modelName, setModelName] = useState("yolov8n_finetuned_defect");
  const [selectedDataset, setSelectedDataset] = useState("neu_det");
  const [epochs, setEpochs] = useState(30);
  const [batchSize, setBatchSize] = useState(16);
  const [imgSize, setImgSize] = useState(640);
  const [device, setDevice] = useState("cpu");

  // Asynchronous training job tracking
  const [activeJob, setActiveJob] = useState<TrainingJobStatus | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [notification, setNotification] = useState<{ text: string; error?: boolean } | null>(null);

  const fetchModels = async () => {
    try {
      setLoading(true);
      const [modelsData, datasetsData] = await Promise.all([
        ApiService.getModels(),
        ApiService.getDatasets().catch(() => [])
      ]);
      setModels(modelsData);
      setDatasets(datasetsData);
    } catch (err) {
      console.error("Failed to fetch models:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  // Poll active training job
  useEffect(() => {
    if (!activeJob || activeJob.status === "COMPLETED" || activeJob.status === "FAILED") {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const updated = await ApiService.getTrainingStatus(activeJob.job_id);
        setActiveJob(updated);
        if (updated.status === "COMPLETED") {
          setNotification({ text: `Training job '${updated.job_id}' completed! New weights registered.` });
          fetchModels();
        } else if (updated.status === "FAILED") {
          setNotification({ text: updated.error_message || "Training job failed.", error: true });
        }
      } catch (err) {
        console.error("Failed to poll training status:", err);
      }
    }, 1200);

    return () => clearInterval(interval);
  }, [activeJob]);

  const handleSelectActiveModel = async (name: string) => {
    try {
      await ApiService.selectActiveModel(name);
      setNotification({ text: `Model '${name}' set as active inference detector.` });
      await fetchModels();
      setTimeout(() => setNotification(null), 4000);
    } catch (err) {
      console.error("Failed to select active model:", err);
      setNotification({ text: "Failed to switch active model.", error: true });
    }
  };

  const handleStartTraining = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setNotification(null);
    try {
      const job = await ApiService.trainModel({
        model_name: modelName,
        dataset_name: selectedDataset,
        epochs,
        batch_size: batchSize,
        img_size: imgSize,
        device
      });
      setActiveJob(job);
      setNotification({ text: `Training job '${job.job_id}' queued in background worker.` });
    } catch (err: any) {
      console.error("Failed to start training:", err);
      setNotification({
        text: err?.response?.data?.detail || "Training job failed to start.",
        error: true
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-900 tracking-tight">
            YOLOv8 Defect Detection Models & Fine-Tuning Manager
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Ultralytics YOLO checkpoint registry, benchmark evaluation metrics (mAP, Precision, Recall), and background training.
          </p>
        </div>
        <button
          onClick={fetchModels}
          className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 flex items-center gap-1.5 cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {notification && (
        <div
          className={`p-3.5 rounded-xl border text-xs font-semibold flex items-center gap-2 ${
            notification.error
              ? "bg-rose-50 border-rose-200 text-rose-800"
              : "bg-emerald-50 border-emerald-200 text-emerald-800"
          }`}
        >
          {notification.error ? (
            <AlertCircle className="w-4 h-4 shrink-0" />
          ) : (
            <CheckCircle className="w-4 h-4 shrink-0" />
          )}
          <span>{notification.text}</span>
        </div>
      )}

      {/* Models Catalog Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {models.map((m) => {
          return (
            <div
              key={m.id}
              className={`bg-white rounded-xl border shadow-xs transition-all flex flex-col overflow-hidden relative ${
                m.is_active ? "border-blue-500 ring-2 ring-blue-500/20" : "border-slate-200/90"
              }`}
            >
              {m.is_active && (
                <div className="bg-blue-600 text-white text-[10px] font-bold px-3 py-1 text-center tracking-wider uppercase">
                  Active Model for Live Inspections
                </div>
              )}

              <div className="p-5 flex-1 space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 font-mono">{m.name}</h4>
                    <span className="text-[11px] text-slate-500 block">
                      Target Dataset: <strong>{m.dataset_name.toUpperCase()}</strong>
                    </span>
                  </div>
                  <span
                    className={`inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full ${
                      m.file_exists
                        ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                        : "bg-amber-50 text-amber-700 border border-amber-200"
                    }`}
                  >
                    {m.file_exists ? "Trained Weights Ready" : "Untrained (Demo Fallback)"}
                  </span>
                </div>

                {/* Validation Metrics Grid */}
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200/80">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-2">
                    Verified Benchmark Metrics
                  </span>
                  {m.file_exists && (m.precision > 0 || m.map50 > 0) ? (
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <span className="text-[10px] text-slate-400 block">Precision</span>
                        <span className="font-bold text-slate-800 font-mono text-sm">
                          {(m.precision * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 block">Recall</span>
                        <span className="font-bold text-slate-800 font-mono text-sm">
                          {(m.recall * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 block">mAP@50</span>
                        <span className="font-bold text-blue-700 font-mono text-sm">
                          {(m.map50 * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 block">mAP@50-95</span>
                        <span className="font-bold text-indigo-700 font-mono text-sm">
                          {(m.map50_95 * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="py-2.5 px-2 text-center rounded bg-slate-100/70 border border-slate-200/50">
                      <span className="text-xs font-semibold text-slate-700 block">Untrained Checkpoint</span>
                      <p className="text-[10px] text-slate-500 mt-0.5 leading-snug">
                        No weights on disk. Fine-tune this model on prepared splits to generate verified mAP metrics.
                      </p>
                    </div>
                  )}
                </div>

                <div className="text-[11px] text-slate-500 space-y-1">
                  <div className="flex justify-between">
                    <span>Architecture:</span>
                    <strong className="text-slate-700">{m.model_type}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Device Execution:</span>
                    <strong className="text-slate-700 uppercase font-mono">{m.device_used}</strong>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-slate-50 border-t border-slate-100">
                {!m.is_active ? (
                  <button
                    onClick={() => handleSelectActiveModel(m.name)}
                    className="w-full py-1.5 px-3 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 text-slate-800 text-xs font-semibold transition-colors"
                  >
                    Set as Active Detection Model
                  </button>
                ) : (
                  <div className="text-center text-xs font-bold text-blue-600 flex items-center justify-center gap-1 py-1">
                    <CheckCircle className="w-3.5 h-3.5" /> Selected
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Asynchronous Model Training Console */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-xs">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <Zap className="w-4 h-4 text-blue-600" />
              Launch Asynchronous YOLO Fine-Tuning Job
            </h3>
            <p className="text-xs text-slate-500">
              Spawns non-blocking background training worker on prepared dataset splits.
            </p>
          </div>
        </div>

        <form onSubmit={handleStartTraining} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Model Checkpoint Name
              </label>
              <input
                type="text"
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-800 font-mono font-medium focus:ring-2 focus:ring-blue-500 focus:outline-hidden"
                required
              />
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Training Dataset
              </label>
              <select
                value={selectedDataset}
                onChange={(e) => setSelectedDataset(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-800 font-medium bg-white"
              >
                <option value="neu_det">NEU-DET Steel Surface (6 classes)</option>
                <option value="gc10_det">GC10-DET Metallic (10 classes)</option>
              </select>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Epoch Count: <span className="text-blue-600 font-mono">{epochs}</span>
              </label>
              <input
                type="number"
                min="5"
                max="200"
                value={epochs}
                onChange={(e) => setEpochs(parseInt(e.target.value) || 20)}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-800 font-medium"
              />
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Batch Size
              </label>
              <select
                value={batchSize}
                onChange={(e) => setBatchSize(parseInt(e.target.value))}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-800 font-medium bg-white"
              >
                <option value={8}>8 (Low VRAM)</option>
                <option value={16}>16 (Standard)</option>
                <option value={32}>32 (High Throughput)</option>
              </select>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Image Resolution (px)
              </label>
              <select
                value={imgSize}
                onChange={(e) => setImgSize(parseInt(e.target.value))}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-800 font-medium bg-white"
              >
                <option value={640}>640 x 640 (Default)</option>
                <option value={512}>512 x 512</option>
                <option value={320}>320 x 320 (Ultra Fast)</option>
              </select>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Execution Hardware
              </label>
              <select
                value={device}
                onChange={(e) => setDevice(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-slate-800 font-medium bg-white"
              >
                <option value="cpu">CPU (Standard Host)</option>
                <option value="cuda">CUDA GPU 0 (Auto Accelerate)</option>
              </select>
            </div>
          </div>

          {/* Dataset Splits Readiness Check */}
          {(() => {
            const ds = datasets.find((d) => d.name === selectedDataset);
            if (ds && !ds.is_prepared) {
              return (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-900 text-xs flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                  <span>
                    <strong>Dataset Splits Pending: </strong> The selected dataset (
                    <strong>{ds.display_name}</strong>) does not have YOLO train/val splits built on disk.
                    Please download images and click <strong>"Prepare Splits"</strong> in the <strong>Datasets</strong> tab first.
                  </span>
                </div>
              );
            }
            return null;
          })()}

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={isSubmitting || activeJob?.status === "RUNNING"}
              className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md shadow-blue-500/20 transition-all flex items-center gap-2 disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-white" />
              {activeJob?.status === "RUNNING" ? "Job In Progress..." : "Launch Background Training Job"}
            </button>
          </div>
        </form>

        {/* Live Training Job Monitor */}
        {activeJob && (
          <div className="mt-6 pt-5 border-t border-slate-100 bg-slate-50 p-4 rounded-xl border border-slate-200/80">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-slate-800">
                  Job: {activeJob.job_id} ({activeJob.model_name})
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    activeJob.status === "COMPLETED"
                      ? "bg-emerald-100 text-emerald-800"
                      : activeJob.status === "RUNNING"
                      ? "bg-blue-100 text-blue-800 animate-pulse"
                      : activeJob.status === "FAILED"
                      ? "bg-rose-100 text-rose-800"
                      : "bg-slate-200 text-slate-700"
                  }`}
                >
                  {activeJob.status}
                </span>
              </div>
              <span className="text-xs font-mono font-bold text-blue-600">
                {activeJob.progress.toFixed(1)}% Completed
              </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden mb-3">
              <div
                className={`h-full transition-all duration-300 ${
                  activeJob.status === "FAILED" ? "bg-rose-500" : "bg-blue-600"
                }`}
                style={{ width: `${activeJob.progress}%` }}
              />
            </div>

            {/* Error Message Notice */}
            {activeJob.status === "FAILED" && activeJob.error_message && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 text-xs flex items-center gap-2 mt-2">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>{activeJob.error_message}</span>
              </div>
            )}

            {/* Live Metrics */}
            {activeJob.status !== "FAILED" && (
              <div className="grid grid-cols-4 gap-2 text-xs font-mono text-slate-600">
                <div>
                  Epoch: <strong>{activeJob.current_epoch} / {activeJob.total_epochs}</strong>
                </div>
                <div>
                  Train Loss: <strong>{activeJob.train_loss.toFixed(4)}</strong>
                </div>
                <div>
                  Val Loss: <strong>{activeJob.val_loss.toFixed(4)}</strong>
                </div>
                <div>
                  Dataset: <strong>{activeJob.dataset_name}</strong>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
