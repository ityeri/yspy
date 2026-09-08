# Changelog

All notable changes to yspy are documented here.

## [Unreleased] — 0.2.0 (예정)

### Added
- **Player availability 판정**
  - `data_parsing.player`: `PlayerState` enum + `PlayerAvailability(state, reason)` dataclass.
    `PlayerPage.from_json` → `(PlayerPage | None, PlayerAvailability)` — 페이지 필드는 불변.
  - `api.video`: `Video.get` / `Video.aget` → `(Video | None, VideoState)` — 예외 없이 값으로 판정.
    `VideoState`: `OK` / `MEMBERS_ONLY` / `RECORDING_UNAVAILABLE` / `AGE_RESTRICTED` /
    `BOT_DETECTION` / `LOGIN_REQUIRED` / `REGION_BLOCKED` / `COPYRIGHT_BLOCKED` / `PRIVATE` /
    `REMOVED_BY_UPLOADER` / `ACCOUNT_TERMINATED` / `REMOVED_FOR_TOS` / `UNAVAILABLE`.
  - 페이지가 unavailable일 때 **pot-free 폴백 클라이언트**(VISIONOS/TVHTML5/MWEB/ANDROID_VR)로
    1회 재프로브(영어 로케일)해 정직한 판정을 얻음 — 데이터센터 IP의 player 게이트 우회 실측.
  - 멤버십 전용 영상 등 상태별 실측(두 문구 변형) 커버. `pytest` 53개.
- **채널/플레이리스트 unavailable 처리**
  - `ChannelPage.from_json` / `PlaylistPage.from_json` → `Page | None` (없음 = `None`, 타입 불일치 = 에러).
  - api: `ChannelUnavailableException` / `PlaylistUnavailableException`.
- `WatchRequest` (watch HTML GET), `request/utils` 클라이언트 테이블 (`InnertubeClientData`).

### Changed
- `VideoPage` → `PlayerPage`, `VideoRequest` → `PlayerRequest` (+ next 페이지·요청) — api 레이어 클래스명 불변.
- `yspy.request.constants` 모듈 삭제 → `yspy.request.utils`로 병합.
- `PlayerRequest`에 `client_data` / `visitor_data` / `headers` 옵션 추가.

### Migration (0.1.x → 0.2.0)
```python
# before: video = Video.get(url); print(video.title)  — None이면 예외였음
# after:
video, state = Video.get(url)
if state is VideoState.OK:
    print(video.title)
```

## [0.1.0] — 2026-09-08

### Added
- 뷰 중심 재설계 릴리즈: `api` / `request` / `data_parsing` / `utils` 레이어 구조.
- 검색 (`Search`, 4개 모드 + continuation), `Video`, `Channel`(+`ChannelDetail`),
  `Playlist`(+`PlaylistVideo`, `aget_from_channel`), `Comments`, `Suggestion` — sync/async 트윈 전면.
- `Locale` (frozen dataclass, `NONE_LOCALE`/`ENGLISH_LOCALE`), 영어 카운트 파싱용 eng 2차 요청,
  id 기반 eng 컴포넌트 매칭.
- pytest 스위트(픽스처 ~4MB), PyPI 신뢰 퍼블리싱 workflow.

[Unreleased]: https://github.com/ityeri/yspy/compare/v0.1.0...develop
[0.1.0]: https://github.com/ityeri/yspy/releases/tag/v0.1.0
