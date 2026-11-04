import axios from "axios";
import {
  DashboardSummary,
  Inspection,
  DatasetItem,
  ModelItem,
  TrainingJobStatus,
  SystemSettings,
  ReportItem,
  SampleImage
} from "../types";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

const api = axios.create({
  baseURL: API_BASE_URL ? `${API_BASE_URL}/api` : "/api",
  timeout: 35000,
  headers: {
    "Content-Type": "application/json"
  }
});

export const getAssetUrl = (path: string | undefined): string => {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  return API_BASE_URL ? `${API_BASE_URL}${cleanPath}` : cleanPath;
};

export const ApiService = {
  // Health
  getHealth: async () => {
    const res = await api.get("/health");
    return res.data;
  },

  // Dashboard
  getDashboardSummary: async (): Promise<DashboardSummary> => {
    const res = await api.get<DashboardSummary>("/dashboard/summary");
    return res.data;
  },

  // Samples & Dataset Loading
  getSamples: async (): Promise<SampleImage[]> => {
    const res = await api.get<{ samples: SampleImage[] }>("/inspection/samples");
    return res.data.samples;
  },

  getDatasetImages: async (
    datasetName: string = "neu_det",
    split: string = "all",
    limit: number = 60
  ): Promise<import("../types").LoadedDatasetResponse> => {
    const res = await api.get<import("../types").LoadedDatasetResponse>("/inspection/dataset-images", {
      params: { dataset_name: datasetName, split, limit }
    });
    return res.data;
  },

  // Image Upload
  uploadImage: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await api.post("/inspection/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    return res.data;
  },

  // Analyze Inspection
  analyzeInspection: async (formData: FormData): Promise<Inspection> => {
    const res = await api.post<Inspection>("/inspection/analyze", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    return res.data;
  },

  // History
  getHistory: async (params?: {
    search?: string;
    severity?: string;
    decision?: string;
    limit?: number;
    offset?: number;
  }): Promise<Inspection[]> => {
    const res = await api.get<Inspection[]>("/inspection/history", { params });
    return res.data;
  },

  getInspection: async (id: number): Promise<Inspection> => {
    const res = await api.get<Inspection>(`/inspection/${id}`);
    return res.data;
  },

  deleteInspection: async (id: number) => {
    const res = await api.delete(`/inspection/${id}`);
    return res.data;
  },

  // Datasets
  getDatasets: async (): Promise<DatasetItem[]> => {
    const res = await api.get<DatasetItem[]>("/datasets");
    return res.data;
  },

  getDatasetStatistics: async (name: string) => {
    const res = await api.get(`/datasets/${name}/statistics`);
    return res.data;
  },

  prepareDataset: async (name: string) => {
    const res = await api.post(`/datasets/${name}/prepare`);
    return res.data;
  },

  initDemoDataset: async (name: string) => {
    const res = await api.post(`/datasets/${name}/init-demo`);
    return res.data;
  },

  getDatasetDownloadGuide: async (name: string) => {
    const res = await api.post(`/datasets/${name}/download`);
    return res.data;
  },

  // Models
  getModels: async (): Promise<ModelItem[]> => {
    const res = await api.get<ModelItem[]>("/models");
    return res.data;
  },

  selectActiveModel: async (modelName: string) => {
    const res = await api.post("/models/select-active", null, {
      params: { model_name: modelName }
    });
    return res.data;
  },

  trainModel: async (params: {
    model_name: string;
    dataset_name: string;
    epochs: number;
    batch_size: number;
    img_size: number;
    device: string;
  }): Promise<TrainingJobStatus> => {
    const res = await api.post<TrainingJobStatus>("/models/train", params);
    return res.data;
  },

  getTrainingStatus: async (jobId: string): Promise<TrainingJobStatus> => {
    const res = await api.get<TrainingJobStatus>(`/models/training-status/${jobId}`);
    return res.data;
  },

  // Reports
  createPdfReport: async (inspectionId: number) => {
    const res = await api.post(`/reports/${inspectionId}/pdf`);
    return res.data;
  },

  getReports: async (): Promise<ReportItem[]> => {
    const res = await api.get<ReportItem[]>("/reports");
    return res.data;
  },

  getExportCsvUrl: () => {
    return API_BASE_URL ? `${API_BASE_URL}/api/reports/export-csv` : "/api/reports/export-csv";
  },

  // Analytics
  getDefectAnalytics: async () => {
    const res = await api.get("/analytics/defects");
    return res.data;
  },

  getTrendAnalytics: async (days: number = 14) => {
    const res = await api.get("/analytics/trends", { params: { days } });
    return res.data;
  },

  // Settings
  getSettings: async (): Promise<SystemSettings> => {
    const res = await api.get<SystemSettings>("/settings");
    return res.data;
  },

  updateSettings: async (settings: Partial<SystemSettings>): Promise<SystemSettings> => {
    const res = await api.put<SystemSettings>("/settings", settings);
    return res.data;
  }
};
