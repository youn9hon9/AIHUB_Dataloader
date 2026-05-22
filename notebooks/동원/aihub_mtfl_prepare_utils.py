from pathlib import Path
import xml.etree.ElementTree as ET
import shutil
import random
import csv
from collections import defaultdict


VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}


def time_to_seconds(t):
    """
    00:00:52.9 -> 52.9
    """
    if t is None:
        return None

    parts = t.strip().split(":")
    if len(parts) == 3:
        h = int(parts[0])
        m = int(parts[1])
        s = float(parts[2])
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:
        m = int(parts[0])
        s = float(parts[1])
        return m * 60 + s
    else:
        return float(parts[0])


def safe_class_name(name):
    """
    폴더명으로 쓰기 좋게 정리.
    """
    if name is None:
        return "unknown"

    return (
        name.strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )


def parse_aihub_xml(xml_path):
    """
    AIHub XML에서 MTFL annotation 생성에 필요한 정보 추출.

    반환:
    {
        filename,
        folder,
        event_name,
        label,
        fps,
        num_frames,
        anomaly_start,
        anomaly_end
    }
    """
    xml_path = Path(xml_path)
    root = ET.parse(xml_path).getroot()

    filename = root.findtext("filename")
    folder = root.findtext("folder")

    fps_text = root.findtext("header/fps")
    frames_text = root.findtext("header/frames")

    fps = float(fps_text) if fps_text is not None else None
    num_frames = int(frames_text) if frames_text is not None else None

    event_node = root.find("event")

    if event_node is None:
        event_name = "normal"
        label = 0
        anomaly_start = -1
        anomaly_end = -1
    else:
        event_name = event_node.findtext("eventname")
        starttime = event_node.findtext("starttime")
        duration = event_node.findtext("duration")

        start_sec = time_to_seconds(starttime)
        duration_sec = time_to_seconds(duration)

        label = 1

        if fps is not None and start_sec is not None and duration_sec is not None:
            anomaly_start = int(round(start_sec * fps))
            anomaly_end = int(round((start_sec + duration_sec) * fps))
        else:
            anomaly_start = -1
            anomaly_end = -1

        if num_frames is not None and anomaly_end > num_frames:
            anomaly_end = num_frames

    if event_name is None:
        event_name = folder if folder is not None else "unknown"

    return {
        "xml_path": xml_path,
        "filename": filename,
        "folder": folder,
        "event_name": event_name,
        "label": label,
        "fps": fps,
        "num_frames": num_frames,
        "anomaly_start": anomaly_start,
        "anomaly_end": anomaly_end,
    }


def find_video_for_xml(xml_path, filename=None):
    """
    XML과 같은 폴더에서 연결되는 영상 파일 찾기.
    """
    xml_path = Path(xml_path)

    if filename:
        candidate = xml_path.parent / filename
        if candidate.exists():
            return candidate

    stem = xml_path.stem
    for ext in VIDEO_EXTS:
        candidate = xml_path.parent / f"{stem}{ext}"
        if candidate.exists():
            return candidate

    for p in xml_path.parent.iterdir():
        if p.is_file() and p.suffix.lower() in VIDEO_EXTS and p.stem == stem:
            return p

    return None


def collect_aihub_items(aihub_raw_root):
    """
    AIHub_raw 하위의 모든 XML을 읽고, 연결 영상과 annotation 정보를 수집.
    """
    aihub_raw_root = Path(aihub_raw_root)

    xml_files = sorted(aihub_raw_root.rglob("*.xml"))

    items = []
    skipped = []

    for xml_path in xml_files:
        try:
            info = parse_aihub_xml(xml_path)
            video_path = find_video_for_xml(xml_path, info["filename"])

            if video_path is None:
                skipped.append({
                    "xml_path": str(xml_path),
                    "reason": "video_not_found",
                })
                continue

            class_name = safe_class_name(info["event_name"])

            item = {
                "src_xml": str(xml_path),
                "src_video": str(video_path),
                "src_parent_folder": xml_path.parent.name,
                "filename": video_path.name,
                "class_name": class_name,
                "label": info["label"],
                "fps": info["fps"],
                "num_frames": info["num_frames"],
                "anomaly_start": info["anomaly_start"],
                "anomaly_end": info["anomaly_end"],
                "event_name": info["event_name"],
            }

            items.append(item)

        except Exception as e:
            skipped.append({
                "xml_path": str(xml_path),
                "reason": f"parse_error: {repr(e)}",
            })

    return items, skipped


def split_items_by_class(items, train_ratio=0.8, seed=42):
    """
    class_name 기준으로 train/test split.
    클래스별 비율 유지.
    """
    random.seed(seed)

    by_class = defaultdict(list)
    for item in items:
        by_class[item["class_name"]].append(item)

    train_items = []
    test_items = []

    for cls, cls_items in by_class.items():
        cls_items = cls_items.copy()
        random.shuffle(cls_items)

        n = len(cls_items)
        n_train = int(n * train_ratio)

        if n >= 2:
            n_train = min(max(n_train, 1), n - 1)

        train_items.extend(cls_items[:n_train])
        test_items.extend(cls_items[n_train:])

    random.shuffle(train_items)
    random.shuffle(test_items)

    return train_items, test_items


def copy_videos_to_mtfl_structure(items, video_out_root, copy_xml=False):
    """
    MTFL용 videos/class_name/video.mp4 구조로 영상 복사.

    반환 items에는 rel_video, dst_video가 추가됨.
    """
    video_out_root = Path(video_out_root)
    video_out_root.mkdir(parents=True, exist_ok=True)

    new_items = []

    for item in items:
        src_video = Path(item["src_video"])
        class_name = item["class_name"]

        dst_video = video_out_root / class_name / src_video.name
        dst_video.parent.mkdir(parents=True, exist_ok=True)

        if not dst_video.exists():
            shutil.copy2(src_video, dst_video)

        new_item = item.copy()
        new_item["dst_video"] = str(dst_video)
        new_item["rel_video"] = dst_video.relative_to(video_out_root).as_posix()

        if copy_xml:
            src_xml = Path(item["src_xml"])
            dst_xml = dst_video.with_suffix(".xml")
            if not dst_xml.exists():
                shutil.copy2(src_xml, dst_xml)
            new_item["dst_xml"] = str(dst_xml)

        new_items.append(new_item)

    return new_items


def make_mtfl_anno_line(item, mode="full"):
    """
    MTFL annotation line 생성.

    mode="full":
        rel_video label num_frames start end

    mode="common":
        rel_video label num_frames start end

    현재 둘은 동일하게 둠.
    필요한 경우 여기만 바꾸면 됨.
    """
    rel_video = item["rel_video"]
    label = int(item["label"])

    num_frames = item["num_frames"]
    if num_frames is None:
        raise ValueError(f"num_frames is None: {rel_video}")

    if label == 0:
        start = -1
        end = -1
    else:
        start = int(item["anomaly_start"])
        end = int(item["anomaly_end"])

    return f"{rel_video} {label} {int(num_frames)} {start} {end}"


def write_annotation(items, out_path, mode="full"):
    """
    annotation txt 저장.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(make_mtfl_anno_line(item, mode=mode) + "\n")

    return out_path


def write_items_csv(items, out_path, split_name=None):
    """
    item 목록 csv 저장.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "split",
        "rel_video",
        "class_name",
        "label",
        "event_name",
        "num_frames",
        "fps",
        "anomaly_start",
        "anomaly_end",
        "src_parent_folder",
        "filename",
        "src_video",
        "src_xml",
        "dst_video",
    ]

    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in items:
            row = {k: item.get(k) for k in fieldnames}
            row["split"] = split_name if split_name is not None else item.get("split")
            writer.writerow(row)

    return out_path


def write_split_summary(train_items, test_items, out_path):
    """
    train/test 전체 summary csv 저장.
    """
    rows = []

    for item in train_items:
        row = item.copy()
        row["split"] = "train"
        rows.append(row)

    for item in test_items:
        row = item.copy()
        row["split"] = "test"
        rows.append(row)

    return write_items_csv(rows, out_path, split_name=None)


def prepare_aihub_for_mtfl(
    aihub_raw_root,
    mtfl_custom_root,
    train_ratio=0.8,
    seed=42,
    copy_xml=False,
    annotation_mode="full",
):
    """
    전체 실행 함수.

    입력:
        AIHub_raw/
          10-1/
            xxx.mp4
            xxx.xml
          10-2/
            ...

    출력:
        MTFL_custom/
          videos/
            assault/
              xxx.mp4
          annotations/
            train_anno.txt
            test_anno.txt
            split_summary.csv
            skipped.csv
    """
    aihub_raw_root = Path(aihub_raw_root)
    mtfl_custom_root = Path(mtfl_custom_root)

    video_out_root = mtfl_custom_root / "videos"
    anno_out_root = mtfl_custom_root / "annotations"

    video_out_root.mkdir(parents=True, exist_ok=True)
    anno_out_root.mkdir(parents=True, exist_ok=True)

    items, skipped = collect_aihub_items(aihub_raw_root)

    copied_items = copy_videos_to_mtfl_structure(
        items=items,
        video_out_root=video_out_root,
        copy_xml=copy_xml,
    )

    train_items, test_items = split_items_by_class(
        copied_items,
        train_ratio=train_ratio,
        seed=seed,
    )

    train_anno_path = write_annotation(
        train_items,
        anno_out_root / "train_anno.txt",
        mode=annotation_mode,
    )

    test_anno_path = write_annotation(
        test_items,
        anno_out_root / "test_anno.txt",
        mode=annotation_mode,
    )

    summary_path = write_split_summary(
        train_items,
        test_items,
        anno_out_root / "split_summary.csv",
    )

    skipped_path = anno_out_root / "skipped.csv"
    with open(skipped_path, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["xml_path", "reason"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(skipped)

    result = {
        "num_xml": len(list(aihub_raw_root.rglob("*.xml"))),
        "num_items": len(items),
        "num_skipped": len(skipped),
        "num_train": len(train_items),
        "num_test": len(test_items),
        "video_out_root": str(video_out_root),
        "train_anno_path": str(train_anno_path),
        "test_anno_path": str(test_anno_path),
        "summary_path": str(summary_path),
        "skipped_path": str(skipped_path),
    }

    return result, train_items, test_items, skipped


def print_prepare_result(result):
    """
    prepare 결과 보기 좋게 출력.
    """
    print("=" * 70)
    print("AIHub -> MTFL prepare result")
    print("=" * 70)
    print("XML files      :", result["num_xml"])
    print("Usable videos  :", result["num_items"])
    print("Skipped        :", result["num_skipped"])
    print("Train          :", result["num_train"])
    print("Test           :", result["num_test"])
    print("Video out root :", result["video_out_root"])
    print("Train anno     :", result["train_anno_path"])
    print("Test anno      :", result["test_anno_path"])
    print("Summary csv    :", result["summary_path"])
    print("Skipped csv    :", result["skipped_path"])
    print("=" * 70)