"""점수·프레임 시각화 (02·03 노트북 공용)."""
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np


def plot_saved_score(score_path):
    score_path = Path(score_path)
    scores = np.load(score_path)

    gt_path = score_path.with_name(score_path.name.replace("_scores.npy", "_gt.npy"))
    gt = np.load(gt_path) if gt_path.exists() else None

    plt.figure(figsize=(15, 4))
    plt.plot(scores, label="Anomaly score")

    if gt is not None:
        if np.any(gt == 1):
            plt.fill_between(
                np.arange(len(gt)),
                0,
                1,
                where=(gt == 1),
                alpha=0.25,
                label="GT anomaly",
            )

    plt.ylim(0, 1)
    plt.title(score_path.stem.replace("_scores", ""))
    plt.xlabel("Frame index")
    plt.ylabel("Anomaly score")
    plt.grid(True)
    plt.legend()
    plt.show()


def find_video_by_stem(video_root, video_stem):
    video_root = Path(video_root)
    candidates = []
    for ext in ["*.mp4", "*.avi", "*.mov", "*.mkv"]:
        candidates.extend(video_root.rglob(ext))

    for p in candidates:
        if p.stem == video_stem:
            return p
    for p in candidates:
        if video_stem in p.stem or p.stem in video_stem:
            return p
    return None


def read_frame(video_path, frame_idx, resize_width=None):
    video_path = Path(video_path)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_idx = int(max(0, min(frame_idx, total_frames - 1)))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame_bgr = cap.read()
    cap.release()

    if not ret:
        raise ValueError(f"Cannot read frame {frame_idx} from {video_path}")

    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    if resize_width is not None:
        h, w = frame_rgb.shape[:2]
        scale = resize_width / w
        frame_rgb = cv2.resize(frame_rgb, (resize_width, int(h * scale)))
    return frame_rgb


def plot_score_with_selected_frames(score_path, video_root, frame_indices):
    score_path = Path(score_path)
    scores = np.load(score_path)
    gt_path = score_path.with_name(score_path.name.replace("_scores.npy", "_gt.npy"))
    gt = np.load(gt_path) if gt_path.exists() else None

    video_stem = score_path.stem.replace("_scores", "")
    video_path = find_video_by_stem(video_root, video_stem)
    if video_path is None:
        raise FileNotFoundError(f"Video not found for stem: {video_stem}")

    n_frames_show = len(frame_indices)
    fig = plt.figure(figsize=(16, 6))
    ax_score = plt.subplot2grid((2, n_frames_show), (0, 0), colspan=n_frames_show)
    ax_score.plot(scores, label="Anomaly score")

    if gt is not None and np.any(gt == 1):
        ax_score.fill_between(
            np.arange(len(gt)), 0, 1, where=(gt == 1), alpha=0.25, label="GT anomaly"
        )
    for f in frame_indices:
        ax_score.axvline(f, linestyle="--")

    ax_score.set_ylim(0, 1)
    ax_score.set_title(video_stem)
    ax_score.grid(True)
    ax_score.legend()

    for i, frame_idx in enumerate(frame_indices):
        ax = plt.subplot2grid((2, n_frames_show), (1, i))
        ax.imshow(read_frame(video_path, frame_idx))
        ax.axis("off")
        gt_text = ""
        if gt is not None and frame_idx < len(gt):
            gt_text = "GT: anomaly" if gt[frame_idx] == 1 else "GT: normal"
        ax.set_title(
            f"frame {frame_idx}\nscore={scores[frame_idx]:.4f}\n{gt_text}",
            fontsize=10,
        )

    plt.tight_layout()
    plt.show()
