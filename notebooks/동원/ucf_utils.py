import cv2
import numpy as np
from pathlib import Path
from collections import defaultdict


def imread_unicode(path):
    """
    한글/특수문자 경로에서도 이미지 읽기
    """
    data = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img


def parse_image_name(img_path: Path):
    """
    Abuse030_x264_1410.png -> ("Abuse030_x264", 1410)
    """
    stem = img_path.stem
    base, frame_str = stem.rsplit("_", 1)
    return base, int(frame_str)


def collect_frames_by_video(category_dir: Path):
    """
    category 폴더 안의 이미지들을 video_id별로 묶음
    """
    image_paths = []
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        image_paths.extend(category_dir.glob(ext))

    grouped = defaultdict(list)

    for img_path in image_paths:
        try:
            video_id, frame_no = parse_image_name(img_path)
            grouped[video_id].append((frame_no, img_path))
        except Exception as e:
            print("skip:", img_path, e)

    for video_id in grouped:
        grouped[video_id] = sorted(grouped[video_id], key=lambda x: x[0])

    return grouped


def merge_intervals(intervals):
    """
    겹치는 anomaly interval 병합
    """
    if not intervals:
        return []

    intervals = sorted(intervals, key=lambda x: x[0])
    merged = [intervals[0]]

    for s, e in intervals[1:]:
        last_s, last_e = merged[-1]

        if s <= last_e:
            merged[-1] = [last_s, max(last_e, e)]
        else:
            merged.append([s, e])

    return merged


def timestamps_to_output_frame_intervals(timestamps, output_fps, total_output_frames):
    """
    json timestamps: 초 단위
    변환된 mp4 frame index로 변환
    """
    intervals = []

    for start_sec, end_sec in timestamps:
        start_frame = int(round(float(start_sec) * output_fps))
        end_frame = int(round(float(end_sec) * output_fps))

        start_frame = max(0, min(start_frame, total_output_frames - 1))
        end_frame = max(0, min(end_frame, total_output_frames - 1))

        if end_frame >= start_frame:
            intervals.append([start_frame, end_frame])

    return merge_intervals(intervals)

def imread_unicode(path):
    data = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img

def frames_to_video(frame_items, out_video_path: Path, fps):
    """
    이미지 프레임 리스트를 mp4로 저장
    frame_items: [(frame_no, img_path), ...]
    """
    out_video_path.parent.mkdir(parents=True, exist_ok=True)

    first_img = imread_unicode(frame_items[0][1])
    if first_img is None:
        raise ValueError(f"Cannot read image: {frame_items[0][1]}")

    height, width = first_img.shape[:2]

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_video_path), fourcc, fps, (width, height))

    for _, img_path in frame_items:
        img = imread_unicode(img_path)

        if img is None:
            print("warning: cannot read", img_path)
            continue

        if img.shape[:2] != (height, width):
            img = cv2.resize(img, (width, height))

        writer.write(img)

    writer.release()