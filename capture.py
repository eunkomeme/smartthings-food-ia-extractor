#!/usr/bin/env python3
"""
Food IA 자동 캡처 스크립트
사용법:
  터미널 1: python3 capture.py
  터미널 2: scrcpy --no-audio  (마우스로 폰 직접 조작)

화면이 바뀔 때마다 자동으로 스크린샷 저장
뒤로가기: scrcpy 창에서 왼쪽 엣지를 오른쪽으로 스와이프
"""

import subprocess
import hashlib
import time
import os
import json
import io
from datetime import datetime
from PIL import Image

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "screens")
os.makedirs(OUTDIR, exist_ok=True)

STATUS_BAR_HEIGHT = 80  # 상태바 높이 (시계/배터리 변화 무시)
POLL_INTERVAL = 0.6
STABLE_WAIT = 0.8

def get_screen():
    """adb exec-out으로 직접 파이프 수신 (sdcard 저장 없음, 빠름)"""
    r = subprocess.run("adb exec-out screencap -p", shell=True, capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None, None
    try:
        img = Image.open(io.BytesIO(r.stdout))
        # 상태바 제외하고 해시 계산
        cropped = img.crop((0, STATUS_BAR_HEIGHT, img.width, img.height))
        h = hashlib.md5(cropped.tobytes()).hexdigest()
        return r.stdout, h
    except Exception:
        return None, None

def get_activity():
    r = subprocess.run(
        "adb shell dumpsys activity activities | grep topResumedActivity",
        shell=True, capture_output=True
    )
    line = r.stdout.decode().strip()
    if "/" in line:
        return line.split("/")[-1].split(" ")[0]
    return ""

def save_screen(screen_id, raw_png, activity):
    png_path = os.path.join(OUTDIR, f"{screen_id}.png")
    with open(png_path, "wb") as f:
        f.write(raw_png)

    meta = {
        "id": screen_id,
        "timestamp": datetime.now().isoformat(),
        "activity": activity,
    }
    meta_path = os.path.join(OUTDIR, f"{screen_id}_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"  → {screen_id}.png  [{activity}]")

def main():
    print("=" * 50)
    print("Food IA 자동 캡처")
    print("=" * 50)
    print("scrcpy 창에서 마우스로 폰 조작하세요.")
    print("뒤로가기: 왼쪽 엣지 → 오른쪽 스와이프")
    print("종료: Ctrl+C")
    print("=" * 50)

    existing = [f for f in os.listdir(OUTDIR) if f.endswith('.png')]
    counter = len(existing) + 1
    print(f"\n기존: {len(existing)}개 | 다음: F-S{counter:02d}\n[대기 중...]\n")

    last_hash = None
    last_activity = None

    try:
        while True:
            raw, h = get_screen()
            if not h:
                time.sleep(POLL_INTERVAL)
                continue

            if h != last_hash:
                time.sleep(STABLE_WAIT)
                raw2, h2 = get_screen()
                if h2 == h and raw2:
                    activity = get_activity()
                    screen_id = f"F-S{counter:02d}"
                    ts = datetime.now().strftime("%H:%M:%S")
                    flag = " ★ Activity변경" if activity != last_activity else ""
                    print(f"[{ts}] 변화 감지{flag}")
                    save_screen(screen_id, raw2, activity)
                    counter += 1
                    last_hash = h2
                    last_activity = activity

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        total = counter - len(existing) - 1
        print(f"\n완료! 이번 세션: {total}개 | 저장위치: {OUTDIR}")

if __name__ == "__main__":
    main()
