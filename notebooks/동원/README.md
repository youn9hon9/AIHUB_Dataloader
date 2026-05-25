# Deprecated — 레거시 노트북

이 폴더의 노트북·유틸은 **참고용**입니다. 새 파이프라인은 상위 [`../`](../) 를 사용하세요.

| 레거시 | 대체 |
|--------|------|
| `ucf_crime_train.ipynb` | `01_preprocess.ipynb` + `02_MTFL_train.ipynb` |
| `baseline.ipynb`, `gradcam_test.ipynb` | `03_MTFL_inference.ipynb` |
| `aihub_mtfl_prepare_utils.py`, `ucf_utils.py` | `01_preprocess.ipynb` 셀 내 인라인 |
| `MTFL_vis.py` | `scripts/viz.py` |

MTFL 클론 경로: 레포의 [`models/MTFL`](../../models/MTFL/) (루트 `MTFL/` 폴더는 사용하지 않음).
