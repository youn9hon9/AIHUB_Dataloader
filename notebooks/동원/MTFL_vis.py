from pathlib import Path
import numpy as np
import cv2
import matplotlib.pyplot as plt

def plot_saved_score(score_path):
    score_path = Path(score_path)
    scores = np.load(score_path)

    gt_path = score_path.with_name(score_path.name.replace("_scores.npy", "_gt.npy"))
    gt = np.load(gt_path) if gt_path.exists() else None

    plt.figure(figsize=(15, 4))
    plt.plot(scores, label="Anomaly score")

    if gt is not None:
        anomaly_idx = np.where(gt == 1)[0]
        if len(anomaly_idx) > 0:
            plt.fill_between(
                np.arange(len(gt)),
                0,
                1,
                where=(gt == 1),
                alpha=0.25,
                label="GT anomaly"
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

    exts = ["*.mp4", "*.avi", "*.mov", "*.mkv"]

    candidates = []
    for ext in exts:
        candidates.extend(video_root.rglob(ext))

    # 1) stem 완전 일치
    for p in candidates:
        if p.stem == video_stem:
            return p

    # 2) 확장자 앞 이름이 조금 다를 때 부분 일치
    for p in candidates:
        if video_stem in p.stem or p.stem in video_stem:
            return p

    return None


def debug_find_video(video_root, video_stem, max_print=30):
    video_root = Path(video_root)

    print("VIDEO_ROOT:", video_root)
    print("exists:", video_root.exists())
    print("target stem:", video_stem)

    videos = []
    for ext in ["*.mp4", "*.avi", "*.mov", "*.mkv"]:
        videos.extend(video_root.rglob(ext))

    print("num videos found:", len(videos))
    print("\nfirst videos:")
    for p in videos[:max_print]:
        print(" -", p.stem, "|", p)

    matched = [p for p in videos if video_stem in p.stem or p.stem in video_stem]
    print("\nmatched candidates:")
    for p in matched[:max_print]:
        print(" -", p)

    return matched


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
        new_h = int(h * scale)
        frame_rgb = cv2.resize(frame_rgb, (resize_width, new_h))

    return frame_rgb


def plot_score_with_selected_frames(score_path, video_root, frame_indices):
    score_path = Path(score_path)
    scores = np.load(score_path)

    gt_path = score_path.with_name(score_path.name.replace("_scores.npy", "_gt.npy"))
    gt = np.load(gt_path) if gt_path.exists() else None

    video_stem = score_path.stem.replace("_scores", "")
    video_path = find_video_by_stem(video_root, video_stem)

    if video_path is None:
        print(f"Video not found for stem: {video_stem}")
        debug_find_video(video_root, video_stem)
        raise FileNotFoundError(f"Video not found for stem: {video_stem}")

    print("video_path:", video_path)

    n_frames_show = len(frame_indices)

    fig = plt.figure(figsize=(16, 6))

    ax_score = plt.subplot2grid((2, n_frames_show), (0, 0), colspan=n_frames_show)
    ax_score.plot(scores, label="Anomaly score")

    if gt is not None and np.any(gt == 1):
        ax_score.fill_between(
            np.arange(len(gt)),
            0,
            1,
            where=(gt == 1),
            alpha=0.25,
            label="GT anomaly"
        )

    for f in frame_indices:
        ax_score.axvline(f, linestyle="--")

    ax_score.set_ylim(0, 1)
    ax_score.set_title(video_stem)
    ax_score.set_xlabel("Frame index")
    ax_score.set_ylabel("Anomaly score")
    ax_score.grid(True)
    ax_score.legend()

    for i, frame_idx in enumerate(frame_indices):
        ax = plt.subplot2grid((2, n_frames_show), (1, i))
        frame = read_frame(video_path, frame_idx)

        ax.imshow(frame)
        ax.axis("off")

        gt_text = ""
        if gt is not None and frame_idx < len(gt):
            gt_text = "GT: anomaly" if gt[frame_idx] == 1 else "GT: normal"

        ax.set_title(
            f"frame {frame_idx}\nscore={scores[frame_idx]:.4f}\n{gt_text}",
            fontsize=10
        )

    plt.tight_layout()
    plt.show()