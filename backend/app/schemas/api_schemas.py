import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# Health & System
class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    device: str
    cuda_available: bool
    gemini_configured: bool
    database_connected: bool
    timestamp: datetime.datetime

# Defect item schema
class DefectItem(BaseModel):
    id: Optional[int] = None
    defect_name: str
    class_id: int = 0
    confidence: float
    bbox: List[float] = Field(..., description="[x1, y1, x2, y2] bounding box coordinates")
    area_pixels: float = 0.0
    area_ratio: float = 0.0
    severity_level: str = "LOW"
    visual_description: Optional[str] = None

# GenAI Structured Explanation Schema
class GenAIExplanation(BaseModel):
    defect_name: str
    description: str
    location: str
    severity: str
    possible_causes: List[str]
    recommended_actions: List[str]
    inspection_decision: str
    quality_summary: Optional[str] = None
    provider_used: str = "Rule-Based Fallback"

# Inspection Create & Response
class InspectionResponse(BaseModel):
    id: int
    inspection_code: str
    timestamp: datetime.datetime
    product_name: str
    product_category: str
    original_image_url: str
    annotated_image_url: Optional[str] = None
    total_defects: int
    max_severity: str
    overall_decision: str
    confidence_avg: float
    inference_time_ms: float
    model_name: str
    is_demo: bool
    inference_source: str
    defects: List[DefectItem] = []
    explanation: Optional[GenAIExplanation] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Inspection History Filter & Pagination
class InspectionFilter(BaseModel):
    search: Optional[str] = None
    severity: Optional[str] = None
    decision: Optional[str] = None
    product_category: Optional[str] = None
    limit: int = 50
    offset: int = 0

# Dashboard Summary
class MetricSummary(BaseModel):
    total_inspections: int
    defective_products: int
    defect_free_products: int
    defect_rate: float
    high_critical_defects: int

class DefectDistributionItem(BaseModel):
    name: str
    count: int
    percentage: float

class TrendItem(BaseModel):
    date: str
    total: int
    defective: int
    defect_free: int

class DashboardSummaryResponse(BaseModel):
    metrics: MetricSummary
    recent_inspections: List[Dict[str, Any]]
    defect_distribution: List[DefectDistributionItem]
    inspection_trends: List[TrendItem]
    active_model: str
    device_info: str
    gemini_status: bool
    dataset_status: Dict[str, Any]

# Dataset Schemas
class DatasetItem(BaseModel):
    id: int
    name: str
    display_name: str
    category: str
    source_url: Optional[str] = None
    description: Optional[str] = None
    is_downloaded: bool
    is_prepared: bool
    total_images: int
    train_count: int
    val_count: int
    test_count: int
    num_classes: int
    classes: List[str]
    disk_size_mb: float
    local_path: Optional[str] = None
    yaml_config_path: Optional[str] = None

class DatasetActionResponse(BaseModel):
    success: bool
    message: str
    dataset_name: str
    data: Optional[Dict[str, Any]] = None

# Model Schemas
class ModelItem(BaseModel):
    id: int
    name: str
    model_type: str
    dataset_name: str
    weights_path: str
    file_exists: bool
    precision: float
    recall: float
    map50: float
    map50_95: float
    device_used: str
    is_active: bool
    created_at: datetime.datetime

class TrainModelRequest(BaseModel):
    model_name: str = "custom_yolov8_defect"
    dataset_name: str = "neu_det"
    epochs: int = 50
    batch_size: int = 16
    img_size: int = 640
    device: str = "cpu"

class TrainingJobStatusResponse(BaseModel):
    job_id: str
    model_name: str
    dataset_name: str
    status: str
    progress: float
    current_epoch: int
    total_epochs: int
    train_loss: float
    val_loss: float
    metrics: Dict[str, Any]
    error_message: Optional[str] = None
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None

# Settings
class SystemSettingsUpdate(BaseModel):
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    confidence_threshold: Optional[float] = None
    iou_threshold: Optional[float] = None
    critical_area_ratio: Optional[float] = None
    high_area_ratio: Optional[float] = None
    medium_area_ratio: Optional[float] = None
    active_model_name: Optional[str] = None

class SystemSettingsResponse(BaseModel):
    gemini_api_key_configured: bool
    gemini_model: str
    confidence_threshold: float
    iou_threshold: float
    critical_area_ratio: float
    high_area_ratio: float
    medium_area_ratio: float
    active_model_name: str
    device_name: str
    cuda_available: bool
    version: str

# Analytics
class DefectAnalyticsResponse(BaseModel):
    by_category: List[Dict[str, Any]]
    by_severity: List[Dict[str, Any]]
    most_frequent: List[Dict[str, Any]]
    defect_rate_overall: float
    total_analyzed: int
