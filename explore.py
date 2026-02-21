#!/usr/bin/env python3
"""
SmartThings Food 플러그인 추가 화면 수집 스크립트 v2
- Food 플러그인 내부에서만 탐색
- 탭 좌표: 실제 화면 기준 (1440x3120, 탭바 Y≈3050)
  홈=144, 검색=432, 커뮤니티=720, MY=1008, 바코드=1296
"""

import subprocess
import time
import os
import hashlib
from pathlib import Path

ADB = "/opt/homebrew/bin/adb"
SCREENS_DIR = Path("data/screens")
SCREENS_DIR.mkdir(parents=True, exist_ok=True)

# 기존 파일 수
existing = sorted(SCREENS_DIR.glob("F-S*.png"))
next_id = max([int(f.stem.replace("F-S","")) for f in existing], default=69) + 1

saved_hashes = set()
for f in existing:
    with open(f, "rb") as fp:
        saved_hashes.add(hashlib.md5(fp.read()).hexdigest())

# 탭바 좌표 (실측)
TAB_Y = 3060
TAB_HOME      = (144,  TAB_Y)
TAB_SEARCH    = (432,  TAB_Y)
TAB_COMMUNITY = (720,  TAB_Y)
TAB_MY        = (1008, TAB_Y)
TAB_BARCODE   = (1296, TAB_Y)


def adb(*args):
    return subprocess.run([ADB] + list(args), capture_output=True).stdout

def shell(*args):
    return adb("shell", *args)

def tap(x, y, wait=1.8):
    shell("input", "tap", str(x), str(y))
    time.sleep(wait)

def swipe_up(wait=1.2):
    shell("input", "swipe", "720", "2000", "720", "800", "400")
    time.sleep(wait)

def swipe_down(wait=1.2):
    shell("input", "swipe", "720", "800", "720", "2000", "400")
    time.sleep(wait)

def food_back(wait=1.8):
    """Food 내부 < 버튼 (좌상단 실측 좌표)"""
    shell("input", "tap", "75", "195")
    time.sleep(wait)

def screenshot():
    shell("screencap", "-p", "/sdcard/tmp.png")
    local = "/tmp/food_tmp.png"
    adb("pull", "/sdcard/tmp.png", local)
    with open(local, "rb") as f:
        return f.read()

def save(label=""):
    global next_id
    data = screenshot()
    h = hashlib.md5(data).hexdigest()
    if h in saved_hashes:
        print(f"  [중복 스킵] {label}")
        return False
    saved_hashes.add(h)
    fname = SCREENS_DIR / f"F-S{next_id:02d}.png"
    with open(fname, "wb") as f:
        f.write(data)
    print(f"  [저장] {fname.name}  {label}")
    next_id += 1
    return True

def is_in_food():
    out = adb("shell", "dumpsys", "activity", "activities").decode(errors="ignore")
    return "WebPluginActivity" in out

def goto_home():
    tap(*TAB_HOME)

print(f"시작 ID: F-S{next_id:02d}")
print("=" * 50)

# ─────────────────────────────────────
# MY 탭
# ─────────────────────────────────────
print("\n[MY 탭]")
tap(*TAB_MY)
save("MY 탭 홈")
swipe_up()
save("MY 탭 스크롤")
swipe_down()

# ─────────────────────────────────────
# 검색 탭 → 검색 결과
# ─────────────────────────────────────
print("\n[검색 탭]")
tap(*TAB_SEARCH)
save("검색 홈")

# 검색창 탭 (화면 상단 검색바 위치)
tap(720, 280, wait=1.5)
save("검색창 활성")
shell("input", "text", "pasta")
time.sleep(1)
save("검색어 입력")
shell("input", "keyevent", "66")  # Enter
time.sleep(3)
save("검색 결과 레시피")
swipe_up()
save("검색 결과 스크롤")
swipe_down()

# 검색 결과 첫 레시피 클릭
tap(360, 700, wait=2)
save("검색→레시피 상세 상단")
swipe_up(); save("검색→레시피 상세 중간")
swipe_up(); save("검색→레시피 상세 하단")
swipe_down(); swipe_down()
food_back()

# 커뮤니티 탭으로 전환 (검색 탭 내 상단 탭)
tap(800, 280, wait=1.5)
save("검색 탭 - 커뮤니티 전환")
shell("input", "text", "healthy")
time.sleep(1)
shell("input", "keyevent", "66")
time.sleep(3)
save("커뮤니티 검색 결과")

# 음식 취향 편집 - 검색 홈으로 돌아가서
tap(*TAB_SEARCH)
time.sleep(2)
save("검색 홈 복귀")
# 편집 링크 (검색 홈 내 "내 음식 취향" 섹션 우측)
tap(1330, 700, wait=2)
save("음식 취향 편집")
swipe_up(); save("음식 취향 편집 스크롤")
food_back()

# ─────────────────────────────────────
# 커뮤니티 탭 → 채널 상세
# ─────────────────────────────────────
print("\n[커뮤니티 탭]")
tap(*TAB_COMMUNITY)
save("커뮤니티 홈")
# 첫 번째 채널 클릭
tap(360, 500, wait=2)
save("커뮤니티 채널 상세")
swipe_up(); save("커뮤니티 채널 스크롤")
food_back()

# ─────────────────────────────────────
# 홈 탭 → 레시피 상세 상단 (재료/정보)
# ─────────────────────────────────────
print("\n[홈 → 레시피 상세]")
goto_home()
time.sleep(2)
save("홈 초기")

# 레시피 카드 클릭 (홈 화면 레시피 카드 위치)
tap(360, 1200, wait=2)
save("레시피 상세 상단 (재료/정보)")
swipe_up(); save("레시피 상세 중간")
swipe_up(); save("레시피 상세 하단")

# 단계별 요리하기 버튼 (하단 오렌지 버튼)
tap(720, 2950, wait=2)
save("단계별 요리하기")
swipe_up(); save("단계별 요리하기 스크롤")
food_back()

# 쇼핑리스트로 보내기
tap(360, 1200, wait=2)
swipe_up(); swipe_up()
tap(360, 1400, wait=2)  # 쇼핑리스트 버튼
save("쇼핑리스트")
swipe_up(); save("쇼핑리스트 스크롤")
food_back()

# ─────────────────────────────────────
# 홈 → 내 재료로 요리하기
# ─────────────────────────────────────
print("\n[내 재료로 요리하기]")
goto_home()
time.sleep(2)
# 섹션 > 버튼 (홈 상단 섹션)
tap(1380, 750, wait=2)
save("내 재료로 요리하기 결과")
swipe_up(); save("내 재료로 요리하기 스크롤")
food_back()

# ─────────────────────────────────────
# 홈 → 내 푸드리스트
# ─────────────────────────────────────
print("\n[내 푸드리스트]")
goto_home()
time.sleep(2)
# 내 푸드리스트로 이동 버튼 (홈 최상단 버튼)
tap(720, 300, wait=2)
save("내 푸드리스트")
swipe_up(); save("내 푸드리스트 스크롤")
food_back()

# ─────────────────────────────────────
# 홈 → 내 커뮤니티 채널
# ─────────────────────────────────────
print("\n[내 커뮤니티]")
goto_home()
time.sleep(2)
swipe_up()
# 내 커뮤니티 채널 카드 클릭
tap(200, 1200, wait=2)
save("내 커뮤니티 채널 상세")
food_back()

# ─────────────────────────────────────
# 바코드 탭
# ─────────────────────────────────────
print("\n[바코드 탭]")
tap(*TAB_BARCODE)
save("바코드 스캔")
food_back()

# ─────────────────────────────────────
print("\n" + "=" * 50)
print(f"완료! 총 {len(sorted(SCREENS_DIR.glob('F-S*.png')))}개 화면")
