# GameFit Agent

## Windows 실행용 다운로드

**[GameFit-Windows-x64.zip 다운로드](https://github.com/ggach1/gamefit-agent/releases/latest/download/GameFit-Windows-x64.zip)** · [최신 릴리스 및 실행 안내](https://github.com/ggach1/gamefit-agent/releases/latest)

v1.2.0: 공개 이미지 호스트의 안전 검사 및 공고 이미지 여러 장 직접 업로드를 추가했습니다. 기존 배포본 사용자는 새 ZIP을 받아 별도 폴더에 압축 해제하고 실행하세요.

ZIP 전체를 압축 해제하고 `GameFit/GameFit.exe`를 실행하세요. Python·OCR·한국어/영어 모델이 포함되어 별도 설치와 API 키가 필요 없습니다. `_internal` 폴더도 함께 유지하세요. GitHub의 `Code → Download ZIP` 또는 `Source code (zip)`은 소스 코드용이며 위 실행용 배포본과 다릅니다.

게임업계 채용공고와 지원자 경험을 비교해 **적합도, 일치 기술, 부족 기술, 개선 계획**을 알려주는 AI 에이전트 서버입니다. 수행평가 주제표의 9번 “게임업계 채용공고 적합도 분석 봇”을 구현했습니다.

> 이 프로젝트의 “AI 에이전트”는 외부 생성형 AI API가 아닌 설명 가능한 규칙 기반 에이전트입니다. 입력 상태와 중간 결과를 판단해 등록된 도구를 자율적으로 선택·실행합니다. 따라서 API 키나 유료 계정 없이 재현할 수 있습니다.

## 주요 기능

- 채용공고에서 프로그래밍 언어, 엔진, 서버, DB, 협업, 운영 기술 추출
- 지원자 소개에서 보유 기술 추출
- 요구 기술과 보유 기술 비교 및 0~100점 적합도 계산
- 부족한 기술을 기반으로 우선순위별 개선 계획 생성
- 선택한 도구와 선택 이유를 실행 추적(trace)으로 공개
- 웹 UI와 JSON REST API 제공

## 설치 및 실행

### 선생님 PC에서 실행: Windows 배포본

`release/GameFit-Windows-x64.zip` 전체를 압축 해제한 뒤 `GameFit/GameFit.exe`를 더블클릭합니다. Python, OCR 엔진, 한국어·영어 모델이 모두 포함되어 별도 설치나 API 키가 필요 없습니다. Windows 10/11 x64용입니다. `_internal` 폴더를 삭제하거나 EXE만 옮기지 마세요. 콘솔 창을 닫으면 서버가 종료됩니다. 기본 포트가 사용 중이면 다른 빈 포트로 브라우저가 열립니다.

### 소스 실행

텍스트 분석은 **Python 3.10 이상**으로 실행 가능합니다. OCR에는 Pillow와 `vendor/tesseract` 엔진·모델이 추가로 필요합니다. 제공 배포본은 이를 모두 포함합니다.

```bash
git clone https://github.com/ggach1/gamefit-agent.git
cd gamefit-agent
python run.py
```

브라우저에서 `http://127.0.0.1:8000`을 엽니다. Windows에서 `python` 명령이 없다면 `py run.py`를 사용합니다. 두 명령 모두 없다면 [Python 공식 사이트](https://www.python.org/downloads/)에서 Python 3.10 이상을 설치하면서 **Add Python to PATH**를 선택합니다.

## 사용 방법

입력 방식을 **공고 링크 / 이미지 업로드 / 텍스트** 중 선택하고 본인 기술 스택을 입력합니다. 게임잡 또는 잡코리아 HTTPS 상세 URL에서 본문을 가져옵니다. 게임잡 iframe과 잡코리아 JobPosting 구조화 본문의 이미지는 로컬 Tesseract로 읽습니다. 공식 채용 API가 아닌 공개 HTML 읽기이며 로그인·동적 공고·접근 차단은 지원하지 못할 수 있습니다.

이미지 업로드에서는 공고 사진이나 스크린샷을 최대 6장 선택합니다(장당 12MB, 합계 24MB). 화면 목록의 순서로 읽습니다. PNG/JPEG/WebP/GIF/BMP/TIFF를 지원하되 GIF는 첫 프레임, TIFF는 첫 페이지만 처리합니다. OCR은 로컬에서 수행하며 외부 OCR 서비스로 전송하지 않습니다. 흐리거나 작은 글씨는 인식 오류가 날 수 있으므로 추출 본문을 확인하고 수정 후 재분석하세요.

공고의 이미지 주소는 회사별 고정 허용 목록 대신 공개 HTTP/HTTPS 주소인지 검사합니다. DNS 결과와 리디렉션 목적지를 매번 검사하고 사설·루프백·메타데이터 IP를 차단합니다. 검증한 IP로 연결하며 HTTPS 인증서도 확인합니다. 다운로드가 차단되면 공고를 직접 캡처하여 이미지 업로드를 사용하거나 본문을 텍스트로 입력하세요.

게임잡 GI_No=284844의 실제 이미지에서 Unity와 C#을 인식하는 것을 확인했습니다. OCR은 한글·기호를 틀리게 읽을 수 있습니다. 결과의 '가져온 공고 본문 확인'에서 수정 후 재분석할 수 있습니다. 점수는 사전에 등록된 기술의 일치 비율이지 합격 확률이 아닙니다. 공고를 내려받을 때 인터넷이 필요하지만 OCR은 로컬에서 수행하며 이미지는 작업 후 임시 폴더에서 제거됩니다.

### 배포본 재생성

Python 3.12 x64 가상환경에 `requirements-build.txt`를 설치합니다. `prepare_ocr.ps1`은 공식 배포처에서 엔진과 모델을 받아 프로젝트 내부에 추출합니다. 이후 `python build_portable.py`로 ZIP과 SHA256을 만듭니다. `vendor`, 가상환경, 빌드 산출물은 Git에 올리지 않습니다. 배포 ZIP을 별도로 전달하세요.

1. 입력 방식을 선택하여 공고 링크, 이미지 또는 텍스트를 넣습니다.
2. 두 번째 입력란에 자신의 기술과 프로젝트 경험을 적습니다.
3. **에이전트 분석 시작**을 누릅니다.
4. 적합도, 일치/부족 기술, 실행 도구, 개선 계획을 확인합니다.

텍스트 입력 방식을 선택한 뒤 기본 예제 내용으로 분석을 확인할 수 있습니다.

## 도구 등록과 선택 로직

`agent_server/tools.py`의 `@tool` 데코레이터가 함수를 `REGISTRY`에 등록합니다.

| 도구 | 역할 | 선택 조건 |
|---|---|---|
| `extract_requirements` | 공고의 기술과 요구사항 추출 | 채용공고가 있을 때 |
| `extract_candidate_skills` | 지원자 보유 기술 추출 | 지원자 소개가 있을 때 |
| `calculate_fit` | 일치/부족 기술과 점수 계산 | 두 추출 결과가 모두 있을 때 |
| `generate_improvement_plan` | 부족 기술 기반 실행 계획 생성 | 적합도 계산이 끝났을 때 |

선택 흐름은 다음과 같습니다.

```text
입력 검증 → 공고 분석 → 지원자 분석 → 적합도 계산 → 개선 계획 생성 → JSON 응답
```

`GameJobAgent.select_tools()`가 입력에 따라 도구 목록을 선택하고, `_invoke()`가 등록소에서 해당 함수를 찾아 실행합니다. `analyze()`는 각 실행의 이유를 `trace`에 저장합니다.

## API

### 상태 확인

```http
GET /api/health
```

### 등록 도구 목록

```http
GET /api/tools
```

### 적합도 분석

```http
POST /api/analyze
Content-Type: application/json

{
  "job_posting": "C++ TCP Redis 개발자를 모집합니다.",
  "candidate_profile": "C++ TCP 게임 서버 프로젝트 경험이 있습니다."
}
```

응답에는 `selected_tools`, `trace`, `requirements`, `fit`, `improvement_plan`이 포함됩니다.

## 프로젝트 구조

```text
GameFit-Agent/
├─ agent_server/
│  ├─ agent.py        # 도구 선택 및 실행 오케스트레이션
│  ├─ server.py       # HTTP 서버와 API
│  └─ tools.py        # 도구 등록소와 4개 도구
├─ web/
│  ├─ index.html      # 사용자 화면
│  ├─ style.css       # 반응형 디자인
│  └─ app.js          # API 호출 및 결과 표시
├─ tests/test_agent.py
├─ docs/screenshots/   # 실제 실행 화면
├─ DEVELOPMENT_LOG.md
├─ REVIEW.md
└─ run.py
```

## 테스트

```bash
python -m unittest discover -s tests -v
```

테스트는 도구 4개 등록 여부, 입력별 선택 로직, 점수 및 부족 기술 계산, 빈 입력 예외 처리를 검증합니다.

## 한계와 주의점

- 현재는 사전에 정의한 기술 사전을 이용하므로 새 기술명이나 문맥상의 숙련도는 완벽히 이해하지 못합니다.
- 모든 요구 기술을 같은 비중으로 계산합니다.
- 결과는 취업 준비를 위한 참고 자료이며 실제 채용 가능성을 보장하지 않습니다.

## 향후 개선

- 로컬 LLM 또는 선택형 LLM API를 연결해 자유로운 표현과 유사 기술 인식
- 필수/우대 조건에 서로 다른 가중치 적용
- 여러 공고 저장, 비교, 분석 이력 다운로드 기능
- 개인정보 마스킹 및 사용자별 암호화 저장

## 제출 체크리스트

- [x] 에이전트 서버 주요 코드와 도구 등록·선택 로직
- [x] 설치법, 사용법, 코드 설명, 트러블슈팅 문서
- [x] 테스트 코드
- [x] 실사용 후기 초안
- [x] 개발 블로그/SNS 게시글 초안
- [ ] 본인 계정으로 블로그/SNS 게시 후 링크 기입
- [ ] 본인 GitHub 저장소에 업로드 후 링크 기입

## 라이선스

교육용 프로젝트입니다. 자유롭게 수정해 사용할 수 있습니다.
