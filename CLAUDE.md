# 사생 탄이 사이트 — 진행상황

## 구성
- `index.html`: 모바일용 (기본 도형 탄이, 스크롤 연출). 완성·배포됨.
- `web.html`: **데스크톱용 (배포됨: https://legondmonsterball-byte.github.io/tani-site/web.html, 보강 예정)**. 3D 탄이를 크게 보여주는 페이지.
  - 모델: Sketchfab "Cat v1.0" (rhcreations, CC BY 4.0), 원본은 `web/src/`. 페이지 하단에 출처 표기 필수.
  - `blender/tani_web_rig.py`: 원본에 뼈대를 새로 만들어 자동 가중치로 입히고, 눈을 호박색으로 바꿔 `web/tani.glb`로 내보냄.
    실행: `blender -b -P blender/tani_web_rig.py`
  - 털: Shell 방식 24겹 (`?layers= &len= &den=`로 조절 가능), 몸 재질은 sheen으로 갈색 윤기.
  - 다리: 발 목표 위치로 무릎·팔꿈치를 계산하는 IK(`legIK`). 포즈는 `POSES`.
  - 주의: GLTFLoader가 뼈 이름의 점을 지움 (`thigh.L` → `thighL`). 불러올 때 되돌림.
  - 뼈 회전 방향: +x = 앞으로 숙임/다리를 뒤로, 머리 좌우는 -z가 +X 방향.
- `blender/tani_web_build.py`: 직접 모델링 시도 (안 씀, 형태가 어색해서 실사 모델로 바꿈).

## 화면 확인 방법
- `python3 -m http.server 8765` 후 `web.html?shot=1` (바닥 격자 표시, 캔버스 캡처 가능)
- 헤드리스 렌더는 느려서 `window.__pause`, `window.__dt=1`(포즈 즉시 적용·자동 동작 끔), `__tani.cam=[yaw,pitch,dist]`, `__tani.act('sit')` 사용

## 2026-10-12 현황
- 데스크톱 분위기(B안) 적용: 어두운 배경, 뒤에 큰 TANI 글자, 영어 제목 SASENG Tani(Cormorant Garamond), 앱 카드만 한국어, 스포트라이트+흰 역광으로 털 윤기
- 털: 기본 len 0.065, den 440 (그물 무늬 안 보이게 촘촘히)
- 자세: STAND / SIT / LIE(식빵 대신 엎드리기) / GROOM / STRETCH / MEOW, 쓰다듬기→purr 확인됨
- 화면 확인: `web.html?pose=sit&cam=0.7,0.16,5.2` (자세 즉시 적용). 헤드리스 캡처는 Chrome `--headless=new --use-angle=metal --screenshot` 사용 (playwright 스크린샷은 시간초과)

## 다음 할 일 (2026-10-12 "일단 저장, 나중에 보강"으로 멈춤)
1. 사용자 피드백 반영 — 전체화면으로 다시 띄워 보여준 상태에서 멈춤. 탄이 크기·화면 꽉 채움 여부 의견 받기
   (로컬 전체화면: `python3 -m http.server 8765` 후 `open -na "Google Chrome" --args --user-data-dir=<임시폴더> --start-fullscreen --app=http://localhost:8765/web.html`)
2. 앉은 자세 뒷다리 안쪽에 털 없이 번들거리는 부분 (메시가 접히는 곳)
3. 그루밍 때 앞발이 입까지 안 올라감
4. 데스크톱 접속 시 index.html → web.html 자동 연결할지 정하기 (사용자 답 아직 없음)
