import React, { useState, useEffect, useRef } from "react";
import { ApiService, getAssetUrl } from "../services/api";
import {
  Inspection,
  SampleImage,
  ProductionLineConfig,
  DatasetImageItem,
  LoadedDatasetResponse
} from "../types";
import { SeverityBadge } from "../components/SeverityBadge";
import { DecisionBadge } from "../components/DecisionBadge";
import { WebcamCaptureModal } from "../components/WebcamCaptureModal";
import {
  Upload,
  Camera,
  Play,
  FileDown,
  Layers,
  Sparkles,
  CheckCircle,
  AlertTriangle,
  RotateCcw,
  Cpu,
  Clock,
  ShieldCheck,
  ChevronRight,
  ChevronLeft,
  HelpCircle,
  ZoomIn,
  X,
  Radio,
  Factory,
  Database,
  Filter,
  RefreshCw
} from "lucide-react";

interface Props {
  currentLine?: ProductionLineConfig;
}

export const LiveInspectionPage: React.FC<Props> = ({ currentLine }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [sampleFilename, setSampleFilename] = useState<string | null>(null);

  // Dataset selection & loader state
  const [selectedDatasetKey, setSelectedDatasetKey] = useState<string>("neu_det");
  const [selectedSplit, setSelectedSplit] = useState<string>("all");
  const [loadedDataset, setLoadedDataset] = useState<LoadedDatasetResponse | null>(null);
  const [datasetLoading, setDatasetLoading] = useState<boolean>(false);
  const [activeClassFilter, setActiveClassFilter] = useState<string>("ALL");
  const [selectedImageItem, setSelectedImageItem] = useState<DatasetImageItem | null>(null);

  // Form options
  const [productName, setProductName] = useState(
    currentLine?.defaultProductName || "Cold Rolled Steel Coil #842"
  );
  const [productCategory, setProductCategory] = useState(
    currentLine?.category || "Cold Strip Finishing"
  );
  const [selectedModel, setSelectedModel] = useState("YOLOv8n-NEU-DET");
  const [confThreshold, setConfThreshold] = useState(0.35);

  // Sync with production line changes
  useEffect(() => {
    if (currentLine) {
      setProductName(currentLine.defaultProductName);
      setProductCategory(currentLine.category);
    }
  }, [currentLine]);

  // Status
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<Inspection | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [imageTab, setImageTab] = useState<"annotated" | "original" | "split">("annotated");
  const [isWebcamOpen, setIsWebcamOpen] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [isZoomOpen, setIsZoomOpen] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleLoadDataset = async (
    key: string = selectedDatasetKey,
    split: string = selectedSplit
  ) => {
    setDatasetLoading(true);
    try {
      const res = await ApiService.getDatasetImages(key, split, 120);
      setLoadedDataset(res);
      setActiveClassFilter("ALL");

      if (res.recommended_model) {
        setSelectedModel(res.recommended_model);
      }

      if (res.images.length > 0) {
        handleSelectDatasetImage(res.images[0]);
      }
    } catch (err) {
      console.error("Failed to load dataset images:", err);
    } finally {
      setDatasetLoading(false);
    }
  };

  const handleSelectDatasetImage = (img: DatasetImageItem) => {
    setSelectedFile(null);
    setSelectedImageItem(img);
    setSampleFilename(img.filename);
    setPreviewUrl(getAssetUrl(img.url));
    setProductName(`${img.category} • ${img.defect_type} (${img.filename})`);
    setProductCategory(img.category);
    setResult(null);
    setError(null);
  };

  useEffect(() => {
    handleLoadDataset("neu_det", "all");
  }, []);

  const handleReset = () => {
    setSelectedFile(null);
    setSampleFilename(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setSampleFilename(null);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      setSampleFilename(null);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleSelectSample = (sample: SampleImage) => {
    setSelectedFile(null);
    setSampleFilename(sample.filename);
    setPreviewUrl(getAssetUrl(sample.url));
    setProductName(sample.name);
    setProductCategory(sample.category);
    setResult(null);
    setError(null);
  };

  const handleWebcamCaptured = (file: File) => {
    setSelectedFile(file);
    setSampleFilename(null);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  };

  const handleRunInspection = async () => {
    if (!selectedFile && !sampleFilename) {
      setError("Please select a sample image, upload a component photo, or capture via webcam.");
      return;
    }

    setAnalyzing(true);
    setError(null);

    const formData = new FormData();
    if (selectedFile) {
      formData.append("file", selectedFile);
    } else if (sampleFilename) {
      formData.append("sample_filename", sampleFilename);
    }

    formData.append("product_name", productName);
    formData.append("product_category", productCategory);
    formData.append("model_name", selectedModel);
    formData.append("conf_threshold", confThreshold.toString());

    try {
      const inspectionRes = await ApiService.analyzeInspection(formData);
      setResult(inspectionRes);
      setImageTab("annotated");
    } catch (err: any) {
      console.error("Inspection error:", err);
      setError(err?.response?.data?.detail || "Inspection pipeline failed. Please verify backend status.");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!result) return;
    try {
      setDownloadingPdf(true);
      const res = await ApiService.createPdfReport(result.id);
      if (res.download_url) {
        window.open(getAssetUrl(res.download_url), "_blank");
      }
    } catch (err) {
      console.error("PDF generation error:", err);
      alert("Failed to download PDF report. Check server logs.");
    } finally {
      setDownloadingPdf(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Active Production Line Telemetry Station */}
      {currentLine && (
        <div className="bg-slate-900 text-white rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 border border-slate-800 shadow-md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-500/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
              <Camera className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono font-bold text-blue-400 uppercase tracking-wider bg-blue-950/80 px-2 py-0.5 rounded border border-blue-800">
                  {currentLine.code}
                </span>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <span className="text-[11px] font-semibold text-emerald-400">Optical Camera Stream Station Online</span>
              </div>
              <h3 className="text-sm font-bold text-slate-100 mt-0.5">
                {currentLine.name} — {currentLine.stationName}
              </h3>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="px-2.5 py-1 rounded-md bg-slate-800/90 border border-slate-700 font-mono text-slate-300">
              Throughput: <strong className="text-white">{currentLine.lineSpeed}</strong>
            </span>
            <span className="px-2.5 py-1 rounded-md bg-slate-800/90 border border-slate-700 font-mono text-slate-300">
              Process Temp: <strong className="text-white">{currentLine.operatingTemp}</strong>
            </span>
            <span className="px-2.5 py-1 rounded-md bg-slate-800/90 border border-slate-700 text-slate-300">
              Material Grade: <strong className="text-emerald-300">{currentLine.materialGrade}</strong>
            </span>
            <span className="px-2.5 py-1 rounded-md bg-blue-900/60 border border-blue-700 text-blue-200">
              Shift: <strong>{currentLine.operatorShift}</strong>
            </span>
          </div>
        </div>
      )}

      {/* Industrial Dataset Selection & Loader Station */}
      <div className="bg-white p-5 rounded-xl border border-slate-200/90 shadow-xs space-y-4">
        {/* Top Controls: Dataset Selector + Partition Selector + Load Button */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
                Dataset Benchmark Loader
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold">
                  On-Disk Benchmarks
                </span>
              </h3>
              <p className="text-xs text-slate-500">
                Select an industrial benchmark dataset to load real component images and ground-truth annotations.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Dataset Selector */}
            <select
              value={selectedDatasetKey}
              onChange={(e) => {
                setSelectedDatasetKey(e.target.value);
                handleLoadDataset(e.target.value, selectedSplit);
              }}
              className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 bg-slate-50 hover:bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 cursor-pointer"
            >
              <option value="neu_det">NEU-DET Steel Surface Defects (18 Images • 6 Classes)</option>
              <option value="gc10_det">GC10-DET Metallic Sheet Defects (20 Images • 10 Classes)</option>
              <option value="demo">Factory Demonstration Calibration Samples (7 Plates)</option>
            </select>

            {/* Partition Selector */}
            <select
              value={selectedSplit}
              onChange={(e) => {
                setSelectedSplit(e.target.value);
                handleLoadDataset(selectedDatasetKey, e.target.value);
              }}
              className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 bg-slate-50 hover:bg-white focus:outline-hidden cursor-pointer"
            >
              <option value="all">All Partitions</option>
              <option value="test">Test Split (Evaluation)</option>
              <option value="val">Validation Split</option>
              <option value="train">Train Split</option>
            </select>

            {/* Load Button */}
            <button
              onClick={() => handleLoadDataset(selectedDatasetKey, selectedSplit)}
              disabled={datasetLoading}
              className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition-colors shadow-xs disabled:opacity-50 flex items-center gap-1.5 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${datasetLoading ? "animate-spin" : ""}`} />
              {datasetLoading ? "Loading..." : "Reload Dataset"}
            </button>
          </div>
        </div>

        {/* Dataset Metadata Bar & Class Filters */}
        {loadedDataset && (
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-slate-500 font-semibold">Loaded:</span>
              <strong className="text-slate-800">{loadedDataset.display_name}</strong>
              <span className="px-2 py-0.5 rounded-sm bg-slate-100 font-mono text-slate-600 text-[11px]">
                {loadedDataset.total_images} images loaded
              </span>
              <span className="px-2 py-0.5 rounded-sm bg-blue-50 text-blue-700 font-mono text-[11px] border border-blue-200">
                Calibrated Model: {loadedDataset.recommended_model}
              </span>
            </div>

            {/* Filter pills */}
            <div className="flex items-center gap-1 overflow-x-auto pb-1 max-w-full">
              <span className="text-slate-400 text-[10px] font-semibold uppercase shrink-0 mr-1">Filter Class:</span>
              <button
                onClick={() => setActiveClassFilter("ALL")}
                className={`px-2 py-0.5 rounded-full text-[10px] font-bold transition-all shrink-0 cursor-pointer ${
                  activeClassFilter === "ALL"
                    ? "bg-slate-900 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                All ({loadedDataset.images.length})
              </button>
              {loadedDataset.classes.map((cls) => {
                const count = loadedDataset.images.filter(
                  (im) => im.defect_type.toLowerCase() === cls.toLowerCase()
                ).length;
                if (count === 0) return null;
                return (
                  <button
                    key={cls}
                    onClick={() => setActiveClassFilter(cls)}
                    className={`px-2 py-0.5 rounded-full text-[10px] font-bold transition-all shrink-0 cursor-pointer ${
                      activeClassFilter.toLowerCase() === cls.toLowerCase()
                        ? "bg-blue-600 text-white"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                  >
                    {cls} ({count})
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Gallery / Image Grid */}
        {datasetLoading ? (
          <div className="flex items-center justify-center py-8 text-slate-400 gap-2">
            <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />
            <span className="text-xs font-semibold">Loading dataset benchmark images from disk...</span>
          </div>
        ) : (loadedDataset?.images || []).length > 0 ? (
          <div>
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2.5 max-h-[190px] overflow-y-auto p-1">
              {(loadedDataset?.images || [])
                .filter((img) => activeClassFilter === "ALL" || img.defect_type.toLowerCase() === activeClassFilter.toLowerCase())
                .map((img) => {
                  const isSelected = selectedImageItem?.filename === img.filename || sampleFilename === img.filename;
                  return (
                    <button
                      key={img.id}
                      onClick={() => handleSelectDatasetImage(img)}
                      className={`p-2 rounded-xl border text-left transition-all group relative cursor-pointer ${
                        isSelected
                          ? "bg-blue-50/90 border-blue-500 ring-2 ring-blue-500/30 shadow-xs"
                          : "bg-slate-50/80 border-slate-200 hover:bg-slate-100 hover:border-slate-300"
                      }`}
                    >
                      <div className="h-14 w-full rounded-lg bg-slate-200 overflow-hidden mb-1.5 border border-slate-300/60 relative">
                        <img
                          src={getAssetUrl(img.url)}
                          alt={img.defect_type}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                          loading="lazy"
                        />
                        <span className="absolute bottom-1 right-1 px-1 py-0.2 rounded bg-black/70 text-white text-[8px] font-mono">
                          {img.split}
                        </span>
                      </div>
                      <p className="text-[11px] font-bold text-slate-900 truncate">{img.defect_type}</p>
                      <p className="text-[9px] text-slate-500 truncate font-mono">{img.filename}</p>
                    </button>
                  );
                })}
            </div>
          </div>
        ) : (
          <div className="py-6 text-center text-slate-400 text-xs">
            No images found in the selected partition.
          </div>
        )}
      </div>

      {/* Main Inspection Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Image Upload & Setup */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
                <Upload className="w-4 h-4 text-blue-600" />
                Input Component Image
              </h3>
              {(previewUrl || selectedFile) && (
                <button
                  type="button"
                  onClick={handleReset}
                  className="text-xs font-semibold text-slate-500 hover:text-rose-600 flex items-center gap-1 transition-colors cursor-pointer"
                  title="Reset inspection image"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  Reset
                </button>
              )}
            </div>

            {/* Drag and Drop Box */}
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-slate-300 hover:border-blue-500 hover:bg-blue-50/20 rounded-xl p-5 text-center cursor-pointer transition-colors relative group"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />

              {previewUrl ? (
                <div className="relative aspect-4/3 max-h-[220px] mx-auto rounded-lg overflow-hidden bg-slate-900 border border-slate-300 shadow-inner">
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="w-full h-full object-contain"
                  />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center text-white text-xs font-semibold transition-opacity">
                    Click or drop to replace image
                  </div>
                </div>
              ) : (
                <div className="py-8 space-y-2">
                  <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 mx-auto flex items-center justify-center">
                    <Upload className="w-6 h-6" />
                  </div>
                  <p className="text-xs font-bold text-slate-800">
                    Click to browse or drag & drop industrial image
                  </p>
                  <p className="text-[11px] text-slate-400">
                    Supports high-resolution JPG, PNG, BMP, TIFF (up to 25 MB)
                  </p>
                </div>
              )}
            </div>

            {/* Uploaded File Details Chip */}
            {selectedFile && (
              <div className="mt-2.5 p-2 bg-slate-50 rounded-lg border border-slate-200 text-[11px] flex items-center justify-between font-mono text-slate-600">
                <span className="truncate max-w-[220px] font-semibold text-slate-800">
                  {selectedFile.name}
                </span>
                <span className="text-slate-500">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </span>
              </div>
            )}

            {/* Webcam Button */}
            <div className="mt-3 flex gap-2">
              <button
                type="button"
                onClick={() => setIsWebcamOpen(true)}
                className="w-full py-2 px-3 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold flex items-center justify-center gap-2 transition-colors"
              >
                <Camera className="w-4 h-4 text-slate-500" />
                Live Webcam Snapshot
              </button>
            </div>

            {/* Inspection Parameters */}
            <div className="mt-5 pt-4 border-t border-slate-100 space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Product / Component Name
                </label>
                <input
                  type="text"
                  value={productName}
                  onChange={(e) => setProductName(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-blue-500 font-medium"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Category
                  </label>
                  <select
                    value={productCategory}
                    onChange={(e) => setProductCategory(e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-900 font-medium bg-white"
                  >
                    <option value="Steel Plate">Steel Plate</option>
                    <option value="Cold Rolled Sheet">Cold Rolled Sheet</option>
                    <option value="Coil Steel">Coil Steel</option>
                    <option value="Structural Flange">Structural Flange</option>
                    <option value="Alloy Tube">Alloy Tube</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Model
                  </label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-900 font-medium bg-white font-mono"
                  >
                    <option value="YOLOv8n-NEU-DET">YOLOv8n-NEU-DET</option>
                    <option value="YOLOv8n-GC10-DET">YOLOv8n-GC10-DET</option>
                    <option value="YOLOv8n-Base">YOLOv8n-Base</option>
                  </select>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span>Confidence Threshold</span>
                  <span className="font-mono text-blue-600">{(confThreshold * 100).toFixed(0)}%</span>
                </div>
                <input
                  type="range"
                  min="0.15"
                  max="0.85"
                  step="0.05"
                  value={confThreshold}
                  onChange={(e) => setConfThreshold(parseFloat(e.target.value))}
                  className="w-full accent-blue-600 cursor-pointer"
                />
              </div>

              {error && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 text-xs font-medium">
                  {error}
                </div>
              )}

              <button
                onClick={handleRunInspection}
                disabled={analyzing}
                className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md shadow-blue-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50 mt-4 cursor-pointer"
              >
                {analyzing ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Executing Multimodal Inspection...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-white" />
                    Start Quality Inspection
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Results & Multimodal GenAI Breakdown */}
        <div className="lg:col-span-7 space-y-4">
          {!result && !analyzing && (
            <div className="bg-white rounded-xl border border-slate-200/90 p-12 text-center shadow-xs">
              <div className="w-16 h-16 rounded-full bg-slate-100 text-slate-400 mx-auto mb-4 flex items-center justify-center">
                <Layers className="w-8 h-8" />
              </div>
              <h3 className="text-base font-bold text-slate-800 mb-1">
                Awaiting Inspection Trigger
              </h3>
              <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
                Select one of the sample images above or upload your own component to generate
                bounding boxes, calculate severity, and receive GenAI metallurgical explanations.
              </p>
            </div>
          )}

          {analyzing && (
            <div className="bg-white rounded-xl border border-slate-200/90 p-12 text-center shadow-xs space-y-4">
              <div className="relative w-20 h-20 mx-auto">
                <div className="w-20 h-20 rounded-full border-4 border-blue-100 border-t-blue-600 animate-spin" />
                <Sparkles className="w-8 h-8 text-blue-600 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-900">
                  Executing Automated Inspection Pipeline
                </h4>
                <p className="text-xs text-slate-500 mt-1">
                  1. Localizing surface defects via YOLOv8 • 2. Assessing severity metrics • 3. Synthesizing GenAI engineering explanation
                </p>
              </div>
            </div>
          )}

          {result && (
            <div className="space-y-4 animate-in fade-in duration-200">
              {/* Inference Execution Mode Separation Banner */}
              <div
                className={`p-3.5 rounded-xl border flex items-center justify-between text-xs ${
                  result.is_demo
                    ? "bg-amber-50/80 border-amber-200 text-amber-900"
                    : "bg-emerald-50/80 border-emerald-200 text-emerald-900"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  {result.is_demo ? (
                    <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                  ) : (
                    <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                  )}
                  <div>
                    <div className="font-bold text-xs uppercase tracking-wide flex items-center gap-2">
                      <span>{result.is_demo ? "Demo Mode Active" : "Real Model Inference Active"}</span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-semibold ${
                          result.is_demo
                            ? "bg-amber-100 text-amber-800 border border-amber-300"
                            : "bg-emerald-100 text-emerald-800 border border-emerald-300"
                        }`}
                      >
                        {result.inference_source}
                      </span>
                    </div>
                    <p className="text-[11px] opacity-85 mt-0.5">
                      {result.is_demo
                        ? result.inference_source === "demo_precomputed"
                          ? "Using precomputed industrial calibration ground truth for demonstration."
                          : "Using heuristic optical contour fallback (no trained YOLOv8 weights on disk)."
                        : `Live Ultralytics YOLOv8 inference running on checkpoint ${result.model_name}.`}
                    </p>
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <span className="font-mono text-[10px] font-bold block uppercase opacity-75">
                    {result.is_demo ? "SIMULATED / DEMO" : "PRODUCTION INFERENCE"}
                  </span>
                </div>
              </div>

              {/* Disposition Header Banner */}
              <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2.5 mb-1">
                    <span className="font-mono text-xs font-bold text-slate-500">
                      {result.inspection_code}
                    </span>
                    <DecisionBadge decision={result.overall_decision} size="md" />
                    <SeverityBadge severity={result.max_severity} size="sm" />
                  </div>
                  <p className="text-xs text-slate-600">
                    Defects Found: <strong>{result.total_defects}</strong> • Inference Time:{" "}
                    <strong>{result.inference_time_ms} ms</strong> • Confidence:{" "}
                    <strong>{(result.confidence_avg * 100).toFixed(0)}%</strong>
                  </p>
                </div>

                <button
                  onClick={handleDownloadPdf}
                  disabled={downloadingPdf}
                  className="px-3.5 py-2 rounded-lg bg-blue-600 text-white font-bold text-xs flex items-center gap-2 hover:bg-blue-700 transition-colors shadow-xs disabled:opacity-50"
                >
                  <FileDown className="w-4 h-4" />
                  {downloadingPdf ? "Generating..." : "Download PDF"}
                </button>
              </div>

              {/* Optical Inspection View */}
              <div className="bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                  <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                    <Layers className="w-4 h-4 text-blue-600" />
                    Optical Defect Localization
                  </span>

                  <div className="flex items-center gap-2">
                    <div className="inline-flex p-1 bg-slate-100 rounded-lg text-xs font-medium">
                      <button
                        onClick={() => setImageTab("annotated")}
                        className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                          imageTab === "annotated"
                            ? "bg-white text-blue-600 shadow-xs font-bold"
                            : "text-slate-600 hover:text-slate-900"
                        }`}
                      >
                        Annotated
                      </button>
                      <button
                        onClick={() => setImageTab("original")}
                        className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                          imageTab === "original"
                            ? "bg-white text-blue-600 shadow-xs font-bold"
                            : "text-slate-600 hover:text-slate-900"
                        }`}
                      >
                        Original
                      </button>
                      <button
                        onClick={() => setImageTab("split")}
                        className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                          imageTab === "split"
                            ? "bg-white text-blue-600 shadow-xs font-bold"
                            : "text-slate-600 hover:text-slate-900"
                        }`}
                      >
                        Split View
                      </button>
                    </div>

                    <button
                      onClick={() => setIsZoomOpen(true)}
                      className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition-colors cursor-pointer"
                      title="Inspect High-Res Zoom"
                    >
                      <ZoomIn className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {imageTab === "split" ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                    <div className="relative flex flex-col items-center justify-center min-h-[280px] bg-black/60 rounded-lg overflow-hidden border border-slate-800/80">
                      <span className="absolute top-2 left-2 z-10 text-[9px] bg-slate-800/90 text-slate-300 px-2 py-0.5 rounded font-mono font-bold tracking-wider">
                        RAW SURFACE
                      </span>
                      <img
                        src={getAssetUrl(result.original_image_url)}
                        alt="Raw Surface"
                        className="max-h-[360px] w-auto object-contain"
                      />
                    </div>
                    <div className="relative flex flex-col items-center justify-center min-h-[280px] bg-black/60 rounded-lg overflow-hidden border border-slate-800/80">
                      <span className="absolute top-2 left-2 z-10 text-[9px] bg-blue-600/90 text-white px-2 py-0.5 rounded font-mono font-bold tracking-wider">
                        YOLOv8 LOCALIZATION
                      </span>
                      <img
                        src={getAssetUrl(result.annotated_image_url || result.original_image_url)}
                        alt="AI Localization"
                        className="max-h-[360px] w-auto object-contain"
                      />
                    </div>
                  </div>
                ) : (
                  <div className="bg-slate-950 rounded-xl overflow-hidden flex items-center justify-center min-h-[300px] max-h-[420px] relative border border-slate-800 group">
                    <img
                      src={
                        imageTab === "annotated" && result.annotated_image_url
                          ? getAssetUrl(result.annotated_image_url)
                          : getAssetUrl(result.original_image_url)
                      }
                      alt="Inspection Result"
                      className="max-h-[400px] w-auto object-contain cursor-zoom-in"
                      onClick={() => setIsZoomOpen(true)}
                    />

                    {/* Inference Tag */}
                    <div
                      className={`absolute bottom-3 right-3 text-[10px] font-mono px-2.5 py-1 rounded-md border shadow-sm backdrop-blur-xs flex items-center gap-1.5 ${
                        result.is_demo
                          ? "bg-amber-950/90 text-amber-300 border-amber-700"
                          : "bg-emerald-950/90 text-emerald-300 border-emerald-700"
                      }`}
                    >
                      <span className="font-bold">{result.is_demo ? "[DEMO MODE]" : "[REAL MODEL]"}</span>
                      <span>{result.inference_source}</span>
                    </div>
                  </div>
                )}

                {/* Defects Table */}
                {result.defects.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-100">
                    <p className="text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-2">
                      Detected Anomaly Coordinates
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {result.defects.map((d, i) => (
                        <div
                          key={i}
                          className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/80 text-xs flex items-center justify-between"
                        >
                          <div>
                            <span className="font-bold text-slate-800">{d.defect_name}</span>
                            <span className="text-[10px] text-slate-500 block font-mono">
                              Box: [{d.bbox.map((n) => Math.round(n)).join(", ")}] • Area:{" "}
                              {(d.area_ratio * 100).toFixed(2)}%
                            </span>
                          </div>
                          <div className="text-right">
                            <span className="font-mono text-blue-600 font-bold block text-[11px]">
                              {(d.confidence * 100).toFixed(1)}%
                            </span>
                            <SeverityBadge severity={d.severity_level} size="sm" />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Multimodal GenAI Defect Explanation Card */}
              {result.explanation && (
                <div className="bg-white rounded-xl border border-blue-200/90 p-5 shadow-xs relative overflow-hidden">
                  <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500" />
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-blue-600" />
                      <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                        Multimodal AI Defect Explanation & Recommendations
                      </h4>
                    </div>
                    <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-semibold">
                      {result.explanation.provider_used}
                    </span>
                  </div>

                  <div className="space-y-4 text-xs">
                    <div>
                      <span className="font-bold text-slate-800">Visual Characteristics:</span>
                      <p className="text-slate-600 mt-1 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                        {result.explanation.description} (Location: {result.explanation.location})
                      </p>
                    </div>

                    {result.explanation.possible_causes && result.explanation.possible_causes.length > 0 && (
                      <div>
                        <span className="font-bold text-slate-800">
                          Possible Root Causes (Engineering Hypotheses):
                        </span>
                        <ul className="mt-1 space-y-1 list-disc list-inside text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                          {result.explanation.possible_causes.map((c, i) => (
                            <li key={i}>{c}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {result.explanation.recommended_actions && result.explanation.recommended_actions.length > 0 && (
                      <div>
                        <span className="font-bold text-slate-800">
                          Recommended Corrective & Preventative Actions:
                        </span>
                        <ul className="mt-1 space-y-1 list-disc list-inside text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                          {result.explanation.recommended_actions.map((a, i) => (
                            <li key={i}>{a}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {result.explanation.quality_summary && (
                      <div className="p-3 bg-blue-50/80 rounded-lg border border-blue-200 text-blue-950 font-medium">
                        <strong className="text-blue-900">Engineering Disposition: </strong>
                        {result.explanation.quality_summary}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Webcam Modal */}
      <WebcamCaptureModal
        isOpen={isWebcamOpen}
        onClose={() => setIsWebcamOpen(false)}
        onCapture={handleWebcamCaptured}
      />

      {/* High-Resolution Zoom Modal */}
      {isZoomOpen && result && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4">
          <div className="bg-slate-900 rounded-2xl max-w-4xl w-full p-4 border border-slate-800 shadow-2xl relative flex flex-col">
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800 text-white">
              <div className="flex items-center gap-2">
                <ZoomIn className="w-4 h-4 text-blue-400" />
                <span className="font-bold text-xs font-mono">
                  {result.inspection_code} • High-Resolution Optical Inspection
                </span>
              </div>
              <button
                onClick={() => setIsZoomOpen(false)}
                className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="max-h-[75vh] overflow-auto flex items-center justify-center bg-black/60 rounded-xl p-2 border border-slate-800/80">
              <img
                src={getAssetUrl(
                  imageTab === "original"
                    ? result.original_image_url
                    : (result.annotated_image_url || result.original_image_url)
                )}
                alt="High-Res Inspection"
                className="max-h-[70vh] w-auto object-contain rounded-lg shadow-lg"
              />
            </div>
            <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
              <span>Mode: {result.is_demo ? "Demo Ground Truth" : "Production YOLOv8"}</span>
              <button
                onClick={() => setIsZoomOpen(false)}
                className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold cursor-pointer"
              >
                Close View
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
