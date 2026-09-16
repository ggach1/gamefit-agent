# OCR 배포본 검증

- Windows x64, Python 3.12 / PyInstaller 6.22.3 / Pillow 12.3.0
- Tesseract 5.5.3.20260724, tessdata_fast kor+eng (배포본 내 포함)
- 단위 테스트 10개 통과: 기존 분석, URL 제한, HTML 제거, OCR 경로, 잘못된 이미지
- GameFit-Windows-x64.zip을 별도 폴더에 압축 해제
- Python 명령 대신 압축 해제한 GameFit.exe --no-browser --port 8765 실행
- GET /api/health 정상
- POST /api/analyze: 실제 게임잡 GI_No=284844 이미지 1개 OCR 후 Unity/C# 추출
- 기술 입력 Unity C# Git → 일치 C#/Unity, 추가 Git
- 점수는 인식된 기술 사전 항목 기준이며 실제 자격요건 전체 충족을 의미하지 않음
- 공고 및 이미지를 내려받을 때만 네트워크 사용; OCR은 번들 엔진으로 로컬 처리
- 별도 물리적 PC 테스트 미실시
- 브라우저 자동화 연결 오류로 클릭/시각적 회귀 검증 미실시

## 전달 방법

release/GameFit-Windows-x64.zip을 통째로 전달한다. 수신자는 압축 해제 후 GameFit/GameFit.exe를 실행한다. _internal 폴더를 함께 유지해야 한다. 배포 파일은 Git에서 제외되어 있으며 기존 GitHub 소스 ZIP에는 자동 포함되지 않는다.
