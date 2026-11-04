import React from "react";
import { DatasetItem } from "../types";
import { X, ExternalLink, Download, FolderTree, Shield, CheckCircle } from "lucide-react";

interface Props {
  dataset: DatasetItem | null;
  onClose: () => void;
  onPrepare: (name: string) => void;
  onInitDemo?: (name: string) => void;
  isPreparing: boolean;
}

export const DatasetGuideModal: React.FC<Props> = ({
  dataset,
  onClose,
  onPrepare,
  onInitDemo,
  isPreparing
}) => {
  if (!dataset) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150">
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold tracking-tight">{dataset.display_name}</h3>
            <p className="text-xs text-slate-400">{dataset.category}</p>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4 max-h-[75vh] overflow-y-auto text-xs text-slate-700">
          <div>
            <h4 className="font-bold text-slate-900 text-sm mb-1">Dataset Overview</h4>
            <p className="text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">
              {dataset.description}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-[11px] font-semibold text-slate-500 uppercase block mb-1">
                Download Status
              </span>
              <span
                className={`font-bold inline-flex items-center gap-1.5 ${
                  dataset.is_downloaded ? "text-emerald-700" : "text-amber-700"
                }`}
              >
                {dataset.is_downloaded ? (
                  <>
                    <CheckCircle className="w-3.5 h-3.5" /> Files Present ({dataset.total_images} images)
                  </>
                ) : (
                  "Not Downloaded / Incomplete"
                )}
              </span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-[11px] font-semibold text-slate-500 uppercase block mb-1">
                YOLO Preparation
              </span>
              <span
                className={`font-bold inline-flex items-center gap-1.5 ${
                  dataset.is_prepared ? "text-emerald-700" : "text-slate-600"
                }`}
              >
                {dataset.is_prepared ? (
                  <>
                    <CheckCircle className="w-3.5 h-3.5" /> Ready for Training
                  </>
                ) : (
                  "Splits Pending"
                )}
              </span>
            </div>
          </div>

          <div>
            <h4 className="font-bold text-slate-900 text-sm mb-1 flex items-center gap-1.5">
              <FolderTree className="w-4 h-4 text-blue-600" />
              Target Folder Structure
            </h4>
            <pre className="bg-slate-900 text-emerald-400 p-3 rounded-lg font-mono text-[11px] overflow-x-auto">
{dataset.name === "neu_det"
  ? `backend/datasets/neu_det/
├── IMAGES/           <- Place original .jpg images (~1,800 images)
├── ANNOTATIONS/      <- Place original .xml Pascal VOC annotations
└── yolo/             <- Auto-generated train/val/test splits`
  : dataset.name === "gc10_det"
  ? `backend/datasets/gc10_det/
├── images/           <- Place original .jpg images (~3,570 images)
├── labelxml/         <- Place original .xml annotation files
└── yolo/             <- Auto-generated train/val/test splits`
  : `backend/datasets/mvtec_ad/
└── <category>/ (e.g., metal_nut)
    ├── train/good/       <- Normal training images
    ├── test/good/        <- Normal test images
    ├── test/<defect>/    <- Defective images
    └── ground_truth/     <- Pixel-level ground-truth masks`}
            </pre>
          </div>

          <div>
            <h4 className="font-bold text-slate-900 text-sm mb-1 flex items-center gap-1.5">
              <ExternalLink className="w-4 h-4 text-blue-600" />
              Official Source & Licensing
            </h4>
            <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg text-blue-900 space-y-1">
              <p>
                <strong>Official Portal: </strong>
                <a
                  href={dataset.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-blue-700 underline font-medium hover:text-blue-900"
                >
                  {dataset.source_url}
                </a>
              </p>
              <p className="text-[11px] text-blue-800">
                Notice: Research and academic usage only. Real annotations and images must be placed in the respective local folder path shown above.
              </p>
            </div>
          </div>
        </div>

        <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-200 text-slate-700 font-semibold text-xs hover:bg-slate-300"
          >
            Close
          </button>
          {dataset.name !== "mvtec_ad" && (
            dataset.is_downloaded ? (
              <button
                onClick={() => {
                  onPrepare(dataset.name);
                  onClose();
                }}
                disabled={isPreparing}
                className="px-4 py-2 rounded-lg bg-blue-600 text-white font-bold text-xs hover:bg-blue-700 transition-colors shadow-xs disabled:opacity-50 flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                {isPreparing ? "Preparing YOLO Splits..." : "Run Split Preparation"}
              </button>
            ) : (
              onInitDemo && (
                <button
                  onClick={() => {
                    onInitDemo(dataset.name);
                    onClose();
                  }}
                  disabled={isPreparing}
                  className="px-4 py-2 rounded-lg bg-indigo-600 text-white font-bold text-xs hover:bg-indigo-700 transition-colors shadow-xs disabled:opacity-50 flex items-center gap-1.5"
                >
                  <FolderTree className="w-3.5 h-3.5" />
                  {isPreparing ? "Initializing..." : "Initialize Demo Samples"}
                </button>
              )
            )
          )}
        </div>
      </div>
    </div>
  );
};
