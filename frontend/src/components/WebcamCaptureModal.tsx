import React, { useRef, useEffect, useState } from "react";
import { Camera, X, RefreshCw } from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onCapture: (capturedFile: File) => void;
}

export const WebcamCaptureModal: React.FC<Props> = ({ isOpen, onClose, onCapture }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cameras, setCameras] = useState<MediaDeviceInfo[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<string>("");

  useEffect(() => {
    if (!isOpen) {
      stopCamera();
      return;
    }
    startCamera();

    return () => {
      stopCamera();
    };
  }, [isOpen, selectedCamera]);

  const startCamera = async () => {
    setError(null);
    try {
      stopCamera();
      const constraints: MediaStreamConstraints = {
        video: selectedCamera ? { deviceId: { exact: selectedCamera } } : { facingMode: "environment" }
      };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      // Enumerate cameras
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter((d) => d.kind === "videoinput");
      setCameras(videoDevices);
      if (!selectedCamera && videoDevices.length > 0) {
        setSelectedCamera(videoDevices[0].deviceId);
      }
    } catch (err: any) {
      console.error("Camera access error:", err);
      setError("Unable to access webcam. Please check browser camera permissions or hardware connection.");
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  };

  const handleCapture = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 640;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `webcam_snap_${Date.now()}.jpg`, { type: "image/jpeg" });
        onCapture(file);
        stopCamera();
        onClose();
      }
    }, "image/jpeg", 0.95);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-xl overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150">
        <div className="px-5 py-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Camera className="w-5 h-5 text-blue-400" />
            <h3 className="text-sm font-bold tracking-tight">Optical Inspection Live Webcam Feed</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 bg-slate-900 relative flex items-center justify-center min-h-[360px]">
          {error ? (
            <div className="text-center p-6 bg-slate-800 rounded-xl text-slate-300 max-w-md">
              <Camera className="w-12 h-12 text-slate-500 mx-auto mb-3" />
              <p className="text-sm font-semibold text-rose-400 mb-1">Webcam Stream Unavailable</p>
              <p className="text-xs text-slate-400 mb-4">{error}</p>
              <button
                onClick={startCamera}
                className="px-3.5 py-1.5 rounded-lg bg-blue-600 text-white text-xs font-semibold hover:bg-blue-700"
              >
                Retry Camera
              </button>
            </div>
          ) : (
            <div className="relative w-full aspect-4/3 max-h-[380px] bg-black rounded-xl overflow-hidden border border-slate-800">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />

              {/* Optical Crosshair Viewfinder */}
              <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                <div className="w-48 h-48 border border-white/40 rounded-lg relative">
                  <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-blue-400" />
                  <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-blue-400" />
                  <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-blue-400" />
                  <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-blue-400" />
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 border border-red-500 rounded-full" />
                </div>
              </div>

              <div className="absolute top-3 left-3 bg-red-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-sm flex items-center gap-1.5 uppercase tracking-wider">
                <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
                Live Feed
              </div>
            </div>
          )}
        </div>

        <div className="px-5 py-3.5 bg-white border-t border-slate-200 flex items-center justify-between">
          {cameras.length > 1 ? (
            <select
              value={selectedCamera}
              onChange={(e) => setSelectedCamera(e.target.value)}
              className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 font-medium text-slate-700"
            >
              {cameras.map((c) => (
                <option key={c.deviceId} value={c.deviceId}>
                  {c.label || `Camera ${c.deviceId.slice(0, 5)}`}
                </option>
              ))}
            </select>
          ) : (
            <span className="text-xs text-slate-500">Position part in crosshair</span>
          )}

          <div className="flex items-center gap-2.5">
            <button
              onClick={onClose}
              className="px-3.5 py-2 rounded-lg bg-slate-100 text-slate-700 text-xs font-semibold hover:bg-slate-200"
            >
              Cancel
            </button>
            <button
              onClick={handleCapture}
              disabled={Boolean(error)}
              className="px-4 py-2 rounded-lg bg-blue-600 text-white text-xs font-bold hover:bg-blue-700 flex items-center gap-2 shadow-xs disabled:opacity-50"
            >
              <Camera className="w-4 h-4" />
              Capture Component Frame
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
