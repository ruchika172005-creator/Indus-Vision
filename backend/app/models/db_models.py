import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database.connection import Base

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inspection_code = Column(String(64), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=utc_now, index=True, nullable=False)
    product_name = Column(String(128), default="Steel Component", nullable=False)
    product_category = Column(String(64), default="Steel Plate", nullable=False)
    
    # Image file paths
    original_image_path = Column(String(256), nullable=False)
    annotated_image_path = Column(String(256), nullable=True)
    
    # Overall summary metrics
    total_defects = Column(Integer, default=0, nullable=False)
    max_severity = Column(String(32), default="LOW", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    overall_decision = Column(String(32), default="PASS", nullable=False) # PASS, FAIL, MANUAL_REVIEW
    confidence_avg = Column(Float, default=0.0)
    inference_time_ms = Column(Float, default=0.0)
    
    # Model & Mode info
    model_name = Column(String(128), default="YOLOv8n-NEU-DET", nullable=False)
    is_demo = Column(Boolean, default=False, nullable=False)
    inference_source = Column(String(64), default="real_model") # real_model, demo_precomputed, synthetic_rule
    
    # Multimodal GenAI response (Structured JSON)
    genai_defect_name = Column(String(128), nullable=True)
    genai_description = Column(Text, nullable=True)
    genai_location = Column(String(128), nullable=True)
    genai_severity = Column(String(32), nullable=True)
    genai_possible_causes = Column(Text, nullable=True) # JSON serialized list
    genai_recommended_actions = Column(Text, nullable=True) # JSON serialized list
    genai_quality_summary = Column(Text, nullable=True)
    genai_provider_used = Column(String(64), default="Rule-Based Fallback") # Google Gemini or Rule-Based Fallback
    
    notes = Column(Text, nullable=True)

    # Relationships
    defects = relationship("DetectedDefect", back_populates="inspection", cascade="all, delete-orphan")
    reports = relationship("GeneratedReport", back_populates="inspection", cascade="all, delete-orphan")


class DetectedDefect(Base):
    __tablename__ = "detected_defects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False, index=True)
    defect_name = Column(String(128), nullable=False)
    class_id = Column(Integer, default=0)
    confidence = Column(Float, nullable=False)
    
    # Coordinates in normalized or absolute pixels
    bbox_x1 = Column(Float, nullable=False)
    bbox_y1 = Column(Float, nullable=False)
    bbox_x2 = Column(Float, nullable=False)
    bbox_y2 = Column(Float, nullable=False)
    
    area_pixels = Column(Float, default=0.0)
    area_ratio = Column(Float, default=0.0) # Defect area / total product area
    severity_level = Column(String(32), default="LOW", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    visual_description = Column(String(256), nullable=True)

    inspection = relationship("Inspection", back_populates="defects")


class DatasetRecord(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(64), unique=True, index=True, nullable=False) # neu_det, gc10_det, mvtec_ad
    display_name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False) # Surface Defect, Anomaly Detection
    source_url = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    
    is_downloaded = Column(Boolean, default=False, nullable=False)
    is_prepared = Column(Boolean, default=False, nullable=False)
    
    total_images = Column(Integer, default=0)
    train_count = Column(Integer, default=0)
    val_count = Column(Integer, default=0)
    test_count = Column(Integer, default=0)
    num_classes = Column(Integer, default=0)
    classes_json = Column(Text, default="[]") # JSON list of class names
    disk_size_mb = Column(Float, default=0.0)
    local_path = Column(String(256), nullable=True)
    yaml_config_path = Column(String(256), nullable=True)
    
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class TrainedModel(Base):
    __tablename__ = "trained_models"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(128), unique=True, index=True, nullable=False)
    model_type = Column(String(64), default="YOLOv8n", nullable=False)
    dataset_name = Column(String(64), nullable=False)
    weights_path = Column(String(256), nullable=False)
    file_exists = Column(Boolean, default=False)
    
    # Benchmark Metrics (verified or real evaluation results)
    precision = Column(Float, default=0.0)
    recall = Column(Float, default=0.0)
    map50 = Column(Float, default=0.0)
    map50_95 = Column(Float, default=0.0)
    
    device_used = Column(String(32), default="cpu")
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)


class TrainingJob(Base):
    __tablename__ = "training_jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(String(64), unique=True, index=True, nullable=False)
    model_name = Column(String(128), nullable=False)
    dataset_name = Column(String(64), nullable=False)
    epochs = Column(Integer, default=50)
    batch_size = Column(Integer, default=16)
    img_size = Column(Integer, default=640)
    device = Column(String(32), default="cpu")
    
    status = Column(String(32), default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED
    progress = Column(Float, default=0.0) # 0.0 to 100.0 %
    current_epoch = Column(Integer, default=0)
    train_loss = Column(Float, default=0.0)
    val_loss = Column(Float, default=0.0)
    metrics_json = Column(Text, default="{}")
    log_output = Column(Text, default="")
    error_message = Column(Text, nullable=True)
    
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False, index=True)
    report_type = Column(String(16), default="PDF") # PDF or CSV
    filename = Column(String(128), nullable=False)
    file_path = Column(String(256), nullable=False)
    file_size_kb = Column(Float, default=0.0)
    generated_at = Column(DateTime, default=utc_now)

    inspection = relationship("Inspection", back_populates="reports")


class ApplicationSetting(Base):
    __tablename__ = "application_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(64), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(256), nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
