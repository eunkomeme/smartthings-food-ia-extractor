#!/usr/bin/env python3
"""
SmartThings Food 플러그인 추가 화면 수집 스크립트
- 미수집 화면 타겟 탐색
- 화면 변화 감지 후 자동 저장
- 중복 방지 (해시 비교)
"""

import subprocess
import time
import os
import hashlib
from pathlib import Path

ADB = "/opt/homebrew/bin/adb"
SCREENS_DIR = Path("data/screens")
SCREENS_DIR.mkdir(parents=True, exist_ok=True)

# 기존 화면 수
existing = sorted(SCREENS_DIR.glob("F-S*.png"))
next_id = len(existing) + 1 if existing else 70

saved_hashes = set()

# 기존 파일 해시 로드 (중복 방지)
for f in existing:
    with open(f, "rb") as fp:
        saved_hashes.add(hashlib.md5(fp.read()).hexdigest())


def adb(*args):
    result = subprocess.run([ADB] + list(args), capture_output=True)
    return result.stdout


def adb_shell(*args):
    return adb("shell", *args)


def screenshot():
    adb_shell("screencap", "-p", "/sdcard/tmp_cap.png")
    local = Path("/tmp/food_cap.png")
    adb("pull", "/sdcard/tmp_cap.png", str(local))
    if local.exists():
        with open(local, "rb") as f:
            return f.read()
    return None


def save_screen(data, label=""):
    global next_id
    h = hashlib.md5(data).hexdigest()
    if h in saved_hashes:
        print(f"  [중복] 스킵")
        return False
    saved_hashes.add(h)
    fname = SCREENS_DIR / f"F-S{next_id:02d}.png"
    with open(fname, "wb") as f:
        f.write(data)
    print(f"  [저장] {fname.name} {label}")
    next_id += 1
    return True


def tap(x, y):
    adb_shell("input", "tap", str(x), str(y))
    time.sleep(1.5)


def swipe_up():
    adb_shell("input", "swipe", "720", "1800", "720", "900", "400")
    time.sleep(1.0)


def swipe_down():
    adb_shell("input", "swipe", "720", "900", "720", "1800", "400")
    time.sleep(1.0)


def back():
    # Food 플러그인 내 < 버튼 (좌상단)
    adb_shell("input", "tap", "80", "200")
    time.sleep(1.5)


def key_back():
    adb_shell("input", "keyevent", "4")
    time.sleep(1.5)


def capture_and_save(label=""):
    data = screenshot()
    if data:
        save_screen(data, label)
    return data


def get_activity():
    out = adb_shell("dumpsys", "activity", "activities").decode(errors="ignore")
    for line in out.split("\n"):
        if "mResumedActivity" in line or "ResumedActivity" in line:
            return line.strip()
    return ""


def ensure_food_home():
    """Food 홈 탭으로 이동"""
    activity = get_activity()
    if "WebPluginActivity" not in activity:
        print("  [!] Food 플러그인 밖 - 홈 탭으로 이동")
        # SmartThings 라이프 탭 Food 섹션 > 버튼
        tap(1350, 882)  # 라이프 탭 Food > 버튼
        time.sleep(2)

    # 홈 탭 클릭 (탭바 Y=3050, 홈 X=144)
    tap(144, 3050)
    time.sleep(1.5)


# ─────────────────────────────────────
# 탐색 시작
# ─────────────────────────────────────
print("=" * 50)
print("SmartThings Food 추가 화면 수집 시작")
print(f"저장 경로: {SCREENS_DIR}")
print(f"시작 ID: F-S{next_id:02d}")
print("=" * 50)
print()

# 현재 화면 확인
print("[0] 현재 화면 저장")
capture_and_save("현재 상태")
time.sleep(0.5)

# ─────────────────────────────────────
# 1. MY 탭
# ─────────────────────────────────────
print()
print("[1] MY 탭 탐색")
tap(1080, 3050)  # MY 탭
time.sleep(2)
capture_and_save("MY 탭 홈")

# MY 탭 스크롤 다운
swipe_up()
capture_and_save("MY 탭 스크롤 하단")

swipe_down()

# ─────────────────────────────────────
# 2. 검색 탭 → 검색 결과
# ─────────────────────────────────────
print()
print("[2] 검색 탭 → 결과 탐색")
tap(432, 3050)  # 검색 탭
time.sleep(2)
capture_and_save("검색 탭 초기")

# 검색어 입력 (검색 입력창 탭)
tap(720, 300)
time.sleep(1)
capture_and_save("검색 입력 활성")

adb_shell("input", "text", "pasta")
time.sleep(1)
capture_and_save("검색어 입력 후")

# 검색 실행 (키보드 검색/엔터)
adb_shell("input", "keyevent", "66")
time.sleep(3)
capture_and_save("검색 결과 - 레시피")

# 스크롤 다운
swipe_up()
capture_and_save("검색 결과 스크롤")
swipe_down()

# 검색 결과 첫 번째 레시피 클릭
tap(360, 600)
time.sleep(2)
capture_and_save("검색 결과 레시피 상세 상단")
swipe_up()
time.sleep(0.5)
capture_and_save("검색 결과 레시피 상세 중간")
swipe_up()
time.sleep(0.5)
capture_and_save("검색 결과 레시피 상세 하단")
swipe_down(); swipe_down()

# 검색 탭으로 돌아가기
back()
time.sleep(1.5)

# 커뮤니티 검색 탭
tap(600, 160)  # 커뮤니티 탭 전환 (상단 탭)
time.sleep(1.5)
capture_and_save("검색 탭 - 커뮤니티 전환")

adb_shell("input", "text", "healthy")
time.sleep(1)
adb_shell("input", "keyevent", "66")
time.sleep(3)
capture_and_save("커뮤니티 검색 결과")

# ─────────────────────────────────────
# 3. 커뮤니티 탭 → 채널 상세
# ─────────────────────────────────────
print()
print("[3] 커뮤니티 채널 상세 탐색")
tap(720, 3050)  # 커뮤니티 탭
time.sleep(2)
capture_and_save("커뮤니티 탭")

# 첫 번째 채널 클릭
tap(360, 400)
time.sleep(2)
capture_and_save("커뮤니티 채널 상세")
swipe_up()
capture_and_save("커뮤니티 채널 스크롤")
swipe_down()
back()
time.sleep(1.5)

# ─────────────────────────────────────
# 4. 홈 탭 → 내 재료로 요리하기 결과
# ─────────────────────────────────────
print()
print("[4] 홈 → 내 재료로 요리하기 결과")
tap(144, 3050)  # 홈 탭
time.sleep(2)
capture_and_save("홈 탭 초기")

# 내 재료로 요리하기 > 버튼 (우측 > 버튼)
# 홈 화면에서 섹션 우측 > 버튼 위치 추정
tap(1350, 600)
time.sleep(2)
capture_and_save("내 재료로 요리하기 결과")
swipe_up()
capture_and_save("내 재료로 요리하기 결과 스크롤")
swipe_down()
back()
time.sleep(1.5)

# ─────────────────────────────────────
# 5. 홈 → 내 푸드리스트
# ─────────────────────────────────────
print()
print("[5] 내 푸드리스트")
tap(144, 3050)  # 홈 탭
time.sleep(2)

# 홈 스크롤 내려서 푸드리스트 버튼 찾기
swipe_up()
time.sleep(0.5)
capture_and_save("홈 스크롤 - 푸드리스트 버튼 찾기")

# 내 푸드리스트로 이동 버튼 클릭 (대략적 위치)
tap(720, 1600)
time.sleep(2)
capture_and_save("내 푸드리스트")
swipe_up()
capture_and_save("내 푸드리스트 스크롤")
swipe_down()
back()
time.sleep(1.5)

# ─────────────────────────────────────
# 6. 레시피 상세 → 단계별 요리하기
# ─────────────────────────────────────
print()
print("[6] 단계별 요리하기")
tap(144, 3050)  # 홈 탭
time.sleep(2)
swipe_down()

# 레시피 카드 클릭
tap(360, 900)
time.sleep(2)
capture_and_save("레시피 상세 상단")
swipe_up()
time.sleep(0.5)
capture_and_save("레시피 상세 재료 섹션")
swipe_up()
time.sleep(0.5)
capture_and_save("레시피 상세 하단 CTA")

# 단계별 요리하기 버튼 (하단 오렌지 버튼)
tap(720, 2900)
time.sleep(2)
capture_and_save("단계별 요리하기 화면")
swipe_up()
capture_and_save("단계별 요리하기 스크롤")
swipe_down()
back()
time.sleep(1.5)

# ─────────────────────────────────────
# 7. 레시피 상세 → 쇼핑리스트
# ─────────────────────────────────────
print()
print("[7] 쇼핑리스트")
# 레시피 상세로 다시 진입
tap(360, 900)
time.sleep(2)
swipe_up(); swipe_up()

# 쇼핑리스트로 보내기 버튼
tap(360, 1200)
time.sleep(2)
capture_and_save("쇼핑리스트 화면")
swipe_up()
capture_and_save("쇼핑리스트 스크롤")
swipe_down()
back()
time.sleep(1.5)

# ─────────────────────────────────────
# 8. 음식 취향 편집
# ─────────────────────────────────────
print()
print("[8] 음식 취향 편집")
tap(432, 3050)  # 검색 탭
time.sleep(2)

# 편집 링크 클릭
tap(1300, 600)
time.sleep(2)
capture_and_save("음식 취향 편집")
swipe_up()
capture_and_save("음식 취향 편집 스크롤")
swipe_down()
back()
time.sleep(1.5)

# ─────────────────────────────────────
# 9. 바코드 스캔
# ─────────────────────────────────────
print()
print("[9] 바코드 스캔")
tap(1368, 3050)  # 바코드 탭 (5번째)
time.sleep(2)
capture_and_save("바코드 스캔 화면")
back()
time.sleep(1.5)

# ─────────────────────────────────────
# 완료
# ─────────────────────────────────────
print()
print("=" * 50)
print(f"수집 완료! 저장된 화면 확인: {SCREENS_DIR}")
new_files = sorted(SCREENS_DIR.glob("F-S*.png"))
print(f"총 {len(new_files)}개 화면")
print("=" * 50)
