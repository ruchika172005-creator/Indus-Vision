from typing import List, Dict, Any
from app.datasets.neu_det import neu_det_manager
from app.datasets.gc10_det import gc10_det_manager
from app.datasets.mvtec_ad import mvtec_ad_manager
from app.datasets.download_manager import download_manager

class UnifiedDatasetManager:
    """
    Centralized controller for all industrial defect benchmarks.
    """

    def __init__(self):
        self.managers = {
            "neu_det": neu_det_manager,
            "gc10_det": gc10_det_manager,
            "mvtec_ad": mvtec_ad_manager
        }

    def list_all(self) -> List[Dict[str, Any]]:
        return [mgr.get_statistics() for mgr in self.managers.values()]

    def get_dataset(self, name: str) -> Dict[str, Any]:
        mgr = self.managers.get(name.lower())
        if not mgr:
            raise KeyError(f"Dataset '{name}' is not registered.")
        return mgr.get_statistics()

    def prepare_dataset(self, name: str) -> Dict[str, Any]:
        mgr = self.managers.get(name.lower())
        if not mgr:
            raise KeyError(f"Dataset '{name}' is not registered.")
        if hasattr(mgr, "prepare_yolo_dataset"):
            return mgr.prepare_yolo_dataset()
        return mgr.get_statistics()

    def init_demo_subset(self, name: str) -> Dict[str, Any]:
        mgr = self.managers.get(name.lower())
        if not mgr:
            raise KeyError(f"Dataset '{name}' is not registered.")
        if hasattr(mgr, "initialize_demo_subset"):
            return mgr.initialize_demo_subset()
        raise NotImplementedError(f"Dataset '{name}' does not support demo initialization.")

    def get_download_instructions(self, name: str) -> Dict[str, Any]:
        return download_manager.get_download_guide(name)

dataset_manager = UnifiedDatasetManager()
