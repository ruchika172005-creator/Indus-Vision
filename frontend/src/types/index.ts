export type SeverityLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type DecisionType = "PASS" | "FAIL" | "MANUAL_REVIEW";

export interface DefectItem {
  id?: number;
  defect_name: string;
  class_id: number;
  confidence: number;
  bbox: [number, number, number, number]; // [x1, y1, x2, y2]
  area_pixels: number;
  area_ratio: number;
  severity_level: SeverityLevel;
  visual_description?: string;
}

export interface GenAIExplanation {
  defect_name: string;
  description: string;
  location: string;
  severity: SeverityLevel;
  possible_causes: string[];
  recommended_actions: string[];
  inspection_decision: DecisionType;
  quality_summary?: string;
  provider_used: string;
}

export interface Inspection {
  id: number;
  inspection_code: string;
  timestamp: string;
  product_name: string;
  product_category: string;
  original_image_url: string;
  annotated_image_url?: string;
  total_defects: number;
  max_severity: SeverityLevel;
  overall_decision: DecisionType;
  confidence_avg: number;
  inference_time_ms: number;
  model_name: string;
  is_demo: boolean;
  inference_source: string;
  defects: DefectItem[];
  explanation?: GenAIExplanation;
  notes?: string;
}

export interface MetricSummary {
  total_inspections: number;
  defective_products: number;
  defect_free_products: number;
  defect_rate: number;
  high_critical_defects: number;
}

export interface DefectDistributionItem {
  name: string;
  count: number;
  percentage: number;
}

export interface TrendItem {
  date: string;
  total: number;
  defective: number;
  defect_free: number;
}

export interface DashboardSummary {
  metrics: MetricSummary;
  recent_inspections: any[];
  defect_distribution: DefectDistributionItem[];
  inspection_trends: TrendItem[];
  active_model: string;
  device_info: string;
  gemini_status: boolean;
  dataset_status: Record<string, { downloaded: boolean; images: number }>;
}

export interface DatasetItem {
  id: number;
  name: string;
  display_name: string;
  category: string;
  source_url?: string;
  description?: string;
  is_downloaded: boolean;
  is_prepared: boolean;
  total_images: number;
  train_count: number;
  val_count: number;
  test_count: number;
  num_classes: number;
  classes: string[];
  disk_size_mb: number;
  local_path?: string;
  yaml_config_path?: string;
}

export interface ModelItem {
  id: number;
  name: string;
  model_type: string;
  dataset_name: string;
  weights_path: string;
  file_exists: boolean;
  precision: number;
  recall: number;
  map50: number;
  map50_95: number;
  device_used: string;
  is_active: boolean;
  created_at: string;
}

export interface TrainingJobStatus {
  job_id: string;
  model_name: string;
  dataset_name: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";
  progress: number;
  current_epoch: number;
  total_epochs: number;
  train_loss: number;
  val_loss: number;
  metrics: Record<string, any>;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

export interface SystemSettings {
  gemini_api_key_configured: boolean;
  gemini_model: string;
  confidence_threshold: number;
  iou_threshold: number;
  critical_area_ratio: number;
  high_area_ratio: number;
  medium_area_ratio: number;
  active_model_name: string;
  device_name: string;
  cuda_available: boolean;
  version: string;
}

export interface ReportItem {
  id: number;
  inspection_id: number;
  report_type: string;
  filename: string;
  file_size_kb: number;
  download_url: string;
  generated_at: string;
}

export interface SampleImage {
  id: string;
  name: string;
  defect_type: string;
  filename: string;
  category: string;
  url: string;
}

export interface DatasetImageItem {
  id: string;
  filename: string;
  relative_path: string;
  defect_type: string;
  category: string;
  split: string;
  url: string;
  has_annotation: boolean;
}

export interface LoadedDatasetResponse {
  dataset_name: string;
  display_name: string;
  total_images: number;
  classes: string[];
  recommended_model: string;
  images: DatasetImageItem[];
}

export interface ProductionLineConfig {
  id: string;
  code: string;
  name: string;
  plant: string;
  line: string;
  category: string;
  defaultProductName: string;
  stationName: string;
  lineSpeed: string;
  materialGrade: string;
  operatorShift: string;
  operatingTemp: string;
}

export const PRODUCTION_LINES: Record<string, ProductionLineConfig> = {
  line_4: {
    id: "line_4",
    code: "PLANT-A-ML04",
    name: "Plant A • Mill Line 4",
    plant: "Plant A (Cold Rolling Complex)",
    line: "Mill Line 4 - High-Speed Cold Finishing",
    category: "Cold Strip Finishing",
    defaultProductName: "Cold Rolled Steel Coil #842",
    stationName: "Station 04 - Surface Inspection Head",
    lineSpeed: "18.5 m/s",
    materialGrade: "Cold Rolled Carbon Steel (CR4 / SPCC)",
    operatorShift: "Shift Alpha • Calibrated Optical Ring",
    operatingTemp: "Ambient (32°C)"
  },
  line_2: {
    id: "line_2",
    code: "PLANT-A-ML02",
    name: "Plant A • Mill Line 2",
    plant: "Plant A (Primary Mill Complex)",
    line: "Mill Line 2 - Hot Strip Descaling Stand",
    category: "Hot Strip Descaling",
    defaultProductName: "Hot Rolled Steel Strip #305",
    stationName: "Station 02 - Roughing Stand Optical Scanner",
    lineSpeed: "12.0 m/s",
    materialGrade: "Hot Rolled Structural Steel (HR240 / ASTM A36)",
    operatorShift: "Shift Bravo • Pyrometer Synchronized",
    operatingTemp: "Elevated (480°C Surface Temp)"
  },
  line_1: {
    id: "line_1",
    code: "PLANT-B-CL01",
    name: "Plant B • Casting Line 1",
    plant: "Plant B (Continuous Casting Facility)",
    line: "Casting Line 1 - Continuous Slab Casting Stand",
    category: "Continuous Slab Casting",
    defaultProductName: "Continuous Cast Steel Slab #118",
    stationName: "Station 01 - Caster Tundish Exit Optical Head",
    lineSpeed: "2.4 m/s",
    materialGrade: "Cast Heavy Steel Plate (AH36 / Structural)",
    operatorShift: "Shift Charlie • Radiance Filtered",
    operatingTemp: "Thermal Inspected (850°C Surface Radiance)"
  }
};
