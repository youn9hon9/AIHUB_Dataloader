# AI-Hub 데이터셋 업로더

## 🛠️사전 준비

1. **rclone 설정**: `rclone config`로 구글 드라이브를 `gdrive` 등 원하는 이름으로 연결해 두세요. 업로드 대상 경로는 아래 **공유 폴더** 안내를 참고해 `GDRIVE_REMOTE`에 맞춥니다.
2. **Git Bash**: 윈도우 파워쉘 대신 **Git Bash**에서 실행해야 합니다.
3. **API 키**: [AI-Hub 마이페이지](https://aihub.or.kr/)에서 발급받은 개인 API 키가 필요합니다.

### 구글 드라이브 공유 폴더에 올릴 때

팀에서 **공유만 받은 폴더**에 그대로 경로를 쓰기 어려운 경우가 많습니다. 웹 구글 드라이브에서 해당 공유 폴더를 연 다음 **「내 드라이브에 바로가기 추가」**(UI 문구는 버전에 따라 다를 수 있음)로 **자신의 드라이브** 쪽에 바로가기를 만들어 두세요. 그다음 `upload_all.sh`의 `GDRIVE_REMOTE`에는 **그 바로가기가 내 드라이브 안에서 차지하는 경로**를 적습니다. 예: `gdrive:상위폴더/…/바로가기폴더명`. rclone `listremotes` / `lsd` 등으로 실제로 보이는 경로와 맞는지 확인하면 안전합니다. **공유 드라이브(팀 드라이브)**만 쓰도록 rclone remote를 따로 만든 경우에는 그 remote 이름과 해당 경로 규칙을 따르면 됩니다.

## 📁 파일 구성

작업 디렉토리(예: `D:/dataset`)에 아래 파일들이 있어야 합니다.

- `aihubshell`: AI-Hub 제공 다운로드 스크립트 (홈페이지에서 다운로드)
- `upload_all.sh`: 자동화 통합 스크립트
- `.env`: API 키 설정
- `rclone`: (시스템 환경변수 `Path`에 등록되어 있어야 함)
- `.gitignore`: API 키 노출 방지

## 🚀 사용 방법

### 1. API 키 설정

프로젝트 루트에서 예시 파일을 복사한 뒤 키를 넣습니다.

```bash
cp .env.example .env
# 에디터로 .env 를 열고 AIHUB_API_KEY= 뒤에 발급받은 키 입력
```

실행 전에 환경 변수를 불러옵니다.

```bash
set -a && source .env && set +a
```

또는 한 세션에서만 쓰려면:

```bash
export AIHUB_API_KEY='발급받은_키'
```

### 2. 구글 드라이브 저장 경로 수정 (`upload_all.sh`)

- `DATASET_KEY`: AI-Hub 데이터셋 번호 (이상행동 CCTV는 `171`)
- `GDRIVE_REMOTE`: 업로드할 **구글 드라이브 쪽 대상 경로**. 공유받은 폴더만 있다면 위 사전 준비처럼 **내 드라이브에 바로가기**를 만든 다음, 그 바로가기가 들어 있는 **내 기준 전체 경로**를 `gdrive:`로 적습니다 (예시는 팀 폴더 구조용).
- `LOCAL_DIR`: AI-Hub가 압축 해제하는 로컬 폴더 이름

```bash
DATASET_KEY="171"
GDRIVE_REMOTE="gdrive:Colab Notebooks/26_Deeplearning/딥러닝 팀플/데이터/dataset/이상행동 CCTV 영상"
LOCAL_DIR="19.이상행동CCTV"
```

### 3. 실행

Git Bash를 열고 해당 폴더로 이동한 뒤, (1)에서 `source .env`까지 한 세션이라면 바로 실행합니다.

```bash
# 1. 실행 권한 부여 (최초 1회)
chmod +x aihubshell upload_all.sh

# 2. 백그라운드 실행 및 로그 기록
./upload_all.sh > upload_log.txt 2>&1 &
```

### 4. 실시간 모니터링

업로드가 잘 되고 있는지 확인하려면 다른 터미널 창에서 아래 명령어를 입력합니다.

```bash
tail -f upload_log.txt
```

## ⚠️ 주의 사항

- **저장 공간**: 파일 하나당 압축 해제 시 약 **60GB**의 여유 공간이 D 드라이브에 있어야 합니다.
- **절전 모드**: 대용량 전송(약 5TB)이므로 컴퓨터가 **절전 모드**로 들어가지 않도록 설정하세요.
- **중단 시**: 컴퓨터가 꺼졌다면 `LOCAL_DIR` 폴더를 지우고, `upload_all.sh`에서 이미 완료된 키(Key) 번호만 삭제한 뒤 다시 실행하면 됩니다.

