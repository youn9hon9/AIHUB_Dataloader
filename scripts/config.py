"""
공통 경로 상수 + clear_gpu().
MTFL / mmaction / VST import 금지 — 01_preprocess에서 안전하게 import 가능.
"""
from __future__ import annotations

import gc
import sys
from pathlib import Path

# --- Google Drive (Colab 기본) ---
DRIVE_ROOT = Path("/content/drive/MyDrive/딥러닝 팀플")
DATA_UCF = DRIVE_ROOT / "01_Data/UCF_Crime"
DATA_AIHUB = DRIVE_ROOT / "01_Data/CCTV 이상행동 데이터"
WEIGHTS = DRIVE_ROOT / "02_Weights"
RESULTS = DRIVE_ROOT / "03_Result"

PRETRAINED_SWIN = WEIGHTS / "pretrained/swin_base_patch244_window877_kinetics400_22k.pth"
PRETRAINED_MTFL = WEIGHTS / "pretrained/MTFL-1280_original.pkl"
CHECKPOINTS_DIR = WEIGHTS / "checkpoints"

RESULTS_EVAL = RESULTS / "results_eval"
GRADCAM_OUTPUTS = RESULTS / "gradcam_outputs"
INFERENCE_CACHE = RESULTS / "inference_cache"

# MTFL feature extractor 최소 프레임 (01_preprocess 필터)
MIN_FRAMES_L32 = 32
MIN_FRAMES_L64 = 64

# UCF 기본 입력 (노트북에서 덮어쓰기 가능)
UCF_FRAME_ROOT = DATA_UCF / "UCF_Crime_frames"
UCF_ANNOTATION_TXT = DATA_UCF / "UCF-Crime-Annotations/Temporal_Anomaly_Annotation.txt"


def resolve_workspace(explicit: Path | None = None) -> Path:
    """Colab Drive clone 경로 또는 레포 루트."""
    if explicit is not None:
        return Path(explicit)
    drive_ws = DRIVE_ROOT / "04_Workspace"
    if drive_ws.exists():
        return drive_ws
    here = Path(__file__).resolve().parent.parent
    if (here / "models" / "MTFL").exists():
        return here
    return Path.cwd()


WORKSPACE = resolve_workspace()
MTFL_ROOT = WORKSPACE / "models" / "MTFL"
SCRIPTS = WORKSPACE / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def clear_gpu():
    """CUDA 캐시 해제 (torch lazy import)."""
    gc.collect()
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            if hasattr(torch.cuda, "ipc_collect"):
                torch.cuda.ipc_collect()
    except ImportError:
        pass
