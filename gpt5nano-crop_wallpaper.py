#!/usr/bin/env python3
import argparse
import os
import shutil
from pathlib import Path

import cv2
import numpy as np

# Simple orientation constants (simplified rule: height > width => vertical)
VERT_AR = 9.0 / 16.0      # vertical: 9:16
HORZ_AR = 16.0 / 10.0     # horizontal: 16:10

def load_image(path):
    path = os.path.normpath(str(path))
    try:
        with open(path, 'rb') as f:
            data = f.read()
        nparr = np.asarray(bytearray(data), dtype=np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is not None:
            return img
    except Exception:
        pass
    return None

def save_image_buffer(path, img):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    ext = p.suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
        ext = ".png"

    success, buf = cv2.imencode(ext, img)
    if not success:
        return False

    with open(str(p), "wb") as f:
        buf.tofile(f)
    return True

def save_image(path, img):
    if save_image_buffer(path, img):
        return True
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return cv2.imwrite(str(path), img)

def compute_saliency_map(img_gray):
    saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
    (success, sal_map) = saliency.computeSaliency(img_gray)
    if not success or sal_map is None:
        return None
    sal_map = (sal_map * 255).astype('uint8')
    return sal_map

def window_sum(ii, x, y, cw, ch):
    x2 = x + cw
    y2 = y + ch
    return float(ii[y2, x2] - ii[y, x2] - ii[y2, x] + ii[y, x])

def best_crop_coords(W, H, cw, ch, sal_map_uint8):
    if sal_map_uint8 is None:
        return max(0, (W - cw) // 2), max(0, (H - ch) // 2)

    sal_f = sal_map_uint8.astype(np.float32) / 255.0
    thresh = max(0.01, float(sal_f.mean()))
    ys, xs = np.where(sal_f > thresh)
    if xs.size > 0:
        cx = xs.mean()
        cy = ys.mean()
    else:
        cx, cy = W / 2.0, H / 2.0

    ii = cv2.integral(sal_map_uint8.astype(np.float32))

    best_score = -1e30
    best_x, best_y = max(0, (W - cw) // 2), max(0, (H - ch) // 2)

    max_x = W - cw
    max_y = H - ch
    step_x = max(1, (W - cw) // 10)
    step_y = max(1, (H - ch) // 10)
    m = max(W, H) * 0.0008

    for y in range(0, max_y + 1, step_y):
        for x in range(0, max_x + 1, step_x):
            s = window_sum(ii, x, y, cw, ch)
            cx_win = x + cw / 2.0
            cy_win = y + ch / 2.0
            dist = ((cx_win - cx) ** 2 + (cy_win - cy) ** 2) ** 0.5
            score = s - dist * m
            if score > best_score:
                best_score = score
                best_x, best_y = int(x), int(y)

    return best_x, best_y

def orientation_for_dims(cw, ch):
    ratio = cw / ch if ch else 0
    vert_diff = abs(ratio - VERT_AR)
    horz_diff = abs(ratio - HORZ_AR)
    return "vertical" if vert_diff <= horz_diff else "horizontal"

def process_image(img_path, out_path, target_w, target_h, exact, downscale_max=1200, sort_output=True, auto_orient=False, input_root=None):
    img = load_image(img_path)
    if img is None:
        return False, None

    H, W = img.shape[:2]

    # Decide ar based on simple rule if auto_orient is on
    ar = None
    if auto_orient:
        orient = "vertical" if H > W else "horizontal"
        ar = VERT_AR if orient == "vertical" else HORZ_AR
    else:
        ar = float(target_w) / float(target_h) if target_h != 0 else 1.0

    # Downscale for saliency
    scale = 1.0
    max_dim = max(W, H)
    if max_dim > downscale_max:
        scale = downscale_max / float(max_dim)
        W_s = int(round(W * scale))
        H_s = int(round(H * scale))
        img_for_sal = cv2.resize(img, (W_s, H_s), interpolation=cv2.INTER_AREA)
    else:
        img_for_sal = img.copy()
        W_s, H_s = W, H

    if exact and (target_w <= W and target_h <= H):
        cw_s, ch_s = int(round(target_w * scale)), int(round(target_h * scale))
    else:
        if W_s / H_s >= ar:
            ch_s = min(H_s, int(round(W_s / ar)))
            cw_s = int(round(ar * ch_s))
        else:
            cw_s = min(W_s, int(round(H_s * ar)))
            ch_s = int(round(cw_s / ar)) if ar != 0 else H_s

        cw_s = max(1, cw_s)
        ch_s = max(1, ch_s)
        cw_s = min(cw_s, W_s)
        ch_s = min(ch_s, H_s)

    sal_map = compute_saliency_map(cv2.cvtColor(img_for_sal, cv2.COLOR_BGR2GRAY))
    x_s, y_s = best_crop_coords(W_s, H_s, cw_s, ch_s, sal_map)

    if scale < 1.0:
        inv = 1.0 / scale
        x = int(round(x_s * inv))
        y = int(round(y_s * inv))
        cw = int(round(cw_s * inv))
        ch = int(round(ch_s * inv))
    else:
        x, y, cw, ch = x_s, y_s, cw_s, ch_s

    x = max(0, min(x, max(0, W - cw)))
    y = max(0, min(y, max(0, H - ch)))
    cw = min(cw, W - x)
    ch = min(ch, H - y)

    crop = img[y:y+ch, x:x+cw]

    ok = save_image(out_path, crop)
    if not ok:
        return False, None

    final_path = str(out_path)
    if sort_output:
        orientation = orientation_for_dims(cw, ch)
        dest_dir = Path(out_path).parent / orientation
        dest_dir.mkdir(parents=True, exist_ok=True)

        if input_root is not None:
            try:
                rel = Path(img_path).relative_to(input_root)
                rel_str = rel.as_posix()  # uses forward slashes
                rel_str = rel_str.replace('/', ' ').replace('\\', ' ')
                ext = Path(out_path).suffix
                base_no_ext = (rel_str[:-len(ext)] if rel_str.endswith(ext) else rel_str)
                if base_no_ext.endswith("_crop"):
                    base_no_ext = base_no_ext[:-5]
                final_name = base_no_ext + ext
            except Exception:
                final_name = Path(out_path).name
        else:
            final_name = Path(out_path).name

        dest_path = dest_dir / final_name
        try:
            os.replace(str(out_path), str(dest_path))
        except Exception:
            shutil.move(str(out_path), str(dest_path))
        final_path = str(dest_path)
    return True, final_path

def collect_image_paths(input_path, recursive=True):
    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    p = Path(input_path)
    if p.is_dir():
        if recursive:
            paths = [f for f in p.rglob("*") if f.suffix.lower() in image_exts]
        else:
            paths = [f for f in p.glob("*") if f.suffix.lower() in image_exts]
    elif p.is_file():
        paths = [p] if p.suffix.lower() in image_exts else []
    else:
        paths = []
    return sorted([str(p) for p in paths])

def main():
    parser = argparse.ArgumentParser(
        description="Crop images to a desktop-wallpaper aspect while preserving focus (no upscaling)."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--input", "-i", type=str, help="Input image file path.")
    group.add_argument("--input_dir", "--indir", type=str, help="Input directory of images.")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output image file path (for single image).")
    parser.add_argument("--output_dir", "--outdir", type=str, default=None, help="Output directory (for batch).")
    parser.add_argument("--target_w", type=int, default=None, help="Target wallpaper width in pixels.")
    parser.add_argument("--target_h", type=int, default=None, help="Target wallpaper height in pixels.")
    parser.add_argument("--exact", action="store_true", help="Crop exactly to target_w x target_h when possible.")
    parser.add_argument("--detect_display", action="store_true", help="Auto-detect display resolution and use as target.")
    parser.add_argument("--downscale_max", type=int, default=1200, help="Maximum dimension for internal saliency pass (faster).")
    parser.add_argument("--recursive", action="store_true", help="When input is a directory, process subfolders as well.")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging.")
    parser.add_argument("--auto_orient", action="store_true", help="Auto detect vertical/horizontal focus before cropping (simple heuristic).")
    parser.add_argument("--no_sort", action="store_true", help="Do not sort output into vertical/horizontal folders.")
    args = parser.parse_args()

    if args.detect_display:
        dw, dh = detect_display_resolution()
        if args.target_w is None:
            args.target_w = dw
        if args.target_h is None:
            args.target_h = dh

    if args.input and not args.input_dir:
        in_paths = [args.input]
        single = True
    elif args.input_dir and not args.input:
        in_paths = collect_image_paths(args.input_dir, recursive=args.recursive)
        single = False
    else:
        print("Specify either --input (single image) or --input_dir (batch).")
        return

    sort_output = not args.no_sort

    if single:
        if not args.output:
            p = Path(args.input)
            out_path = str(p.with_name(p.stem + p.suffix))
        else:
            out_path = args.output
        ok, final_out_path = process_image(
            in_paths[0], out_path,
            target_w=args.target_w or 1920,
            target_h=args.target_h or 1080,
            exact=args.exact,
            downscale_max=args.downscale_max,
            sort_output=sort_output,
            auto_orient=args.auto_orient
        )
        print(f"Processed: {in_paths[0]} -> {final_out_path} ({'OK' if ok else 'FAILED'})")
    else:
        if not args.output_dir:
            out_dir = Path(args.input_dir) / "crops"
        else:
            out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        t_w = args.target_w or 1920
        t_h = args.target_h or 1080

        for pth in in_paths:
            p = Path(pth)
            out_path = out_dir / (p.stem + p.suffix)
            ok, final_out_path = process_image(
                pth, str(out_path),
                target_w=t_w,
                target_h=t_h,
                exact=args.exact,
                downscale_max=args.downscale_max,
                sort_output=sort_output,
                auto_orient=args.auto_orient,
                input_root=args.input_dir if args.input_dir else None
            )
            if args.verbose:
                print(f"Processed: {pth} -> {final_out_path} ({'OK' if ok else 'FAILED'})")

if __name__ == "__main__":
    main()