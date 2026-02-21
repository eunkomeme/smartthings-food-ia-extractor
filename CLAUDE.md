# 📌 프로젝트 목적

Google Play 릴리즈 기준 **Samsung SmartThings Android 앱 내 Food 서비스 플러그인의 실제 실행 기준 IA를 추출**하는 것이 목표다.

목표는 단순 스크린샷 수집이 아니라:

1. Food 플러그인의 전체 화면 구조 파악
2. 화면 간 네비게이션 관계 추론
3. Stack depth / Back behavior 분석
4. 주요 CTA → 랜딩 화면 매핑
5. SmartThings 메인 앱 구조와의 연결 지점 파악
6. 이후 신규 Food 관련 기능(혈당 기록 등) PRD 작성 시:
   - 진입 경로 설계
   - 네비게이션 설계
   - 기존 SmartThings 구조 영향도 분석
   - 플러그인 구조 확장 가능성 검토

에 활용하기 위함

---

# 📌 분석 대상

- 앱: Samsung SmartThings (Android, 일반 릴리즈 빌드)
- 영역: Food 서비스 플러그인 (SmartThings 전체 앱 아님)
- 구조 추정: 메인 탭 내 진입 → 플러그인 독립 stack → WebView + Native 혼합 가능성 있음

**접근 불가 항목**: 소스코드, SDK, 내부 문서, Play Console, Food API 문서(불완전)
→ 오직 실행 중인 앱 기반 블랙박스 분석

---

# 📌 실행 환경

- Android 실기기 (루팅 X, USB 디버깅 ON, 로그인 상태 유지)
- adb 사용 가능

---

# 📌 원하는 산출물

**수집 데이터**
- 화면별 스크린샷 (PNG) + UI Hierarchy (XML) 1:1 매칭
- SmartThings 메인 → Food 진입 구간 포함
- 중복 화면 최소화

**분석 결과**
- Screen inventory + 자동 ID 부여 (예: F-S01, F-S02)
- 화면 간 네비게이션 관계 추정
- Back stack / Stack depth 추정
- SmartThings 메인 앱과 플러그인 경계 구분
- 모달 / BottomSheet / Fullscreen / WebView 구분
- Mermaid 다이어그램으로 출력 가능한 형태

---

# 📌 기술적 고려사항

아래는 구현 방법을 지정하는 게 아니라, 분석 시 반드시 고려해야 할 현실적 제약이다. 방법은 상황에 맞게 판단할 것.

**WebView 대응**
Food 플러그인은 WebView 기반일 가능성이 높다. `uiautomator dump`는 WebView 내부를 읽지 못하므로, WebView 감지 시 내부 콘텐츠를 별도로 추출하는 방법을 판단해서 적용할 것.

**화면 전환 감지**
"화면이 바뀌었다"는 시점을 어떻게 감지할지가 수집 품질의 핵심이다. 단순 polling보다 이벤트 기반 감지가 정확하며, 중복 저장 방지 로직이 반드시 필요하다.

**Activity / Fragment 경계**
화면 전환이 Activity 교체인지 Fragment 교체인지에 따라 Back stack 구조가 달라진다. 이를 구분하는 추적 로직이 필요하다.

**Samsung 특이사항**
SmartThings는 Samsung 자체 프레임워크 기반일 수 있다. Knox 보안 정책 등으로 일부 화면에서 dump가 실패할 수 있으며, 이 경우 실패 케이스를 로깅하고 중단 없이 계속 진행해야 한다.

**자동 탐색 (선택)**
가능하면 Food 영역까지 자동 진입 + 버튼 클릭 탐색을 구현하되, 동일 버튼 반복 방지 / depth 제한 / 뒤로가기 로직 포함. 예외 발생 시 중단하지 않고 복구 후 계속 진행.

---

# 📌 이 프로젝트는

❌ 단순 크롤링 아님
❌ SmartThings API 연동 아님
✅ 블랙박스 UI 구조 역설계
✅ 네비게이션 관계 추정이 핵심
✅ PRD 설계 근거 확보가 목적
