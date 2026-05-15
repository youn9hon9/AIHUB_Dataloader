# AI-Hub 데이터셋 업로더

## 🛠️사전 준비

1. **rclone 설정**: `rclone config`로 구글 드라이브를 `gdrive` 등 원하는 이름으로 연결해 두세요.
2. **Git Bash**: 윈도우 파워쉘 대신 **Git Bash**에서 실행해야 합니다.
3. **API 키**: AI-Hub 마이페이지에서 발급받은 개인 API 키가 필요합니다.
4. [(참고) 구글 드라이브 공유 폴더 바로가기 추가하는 방법](https://www.clien.net/service/board/lecture/15976375)

## 🚀 사용 방법

### 1. API 키 설정

프로젝트 루트에서 예시 파일을 복사한 뒤 키를 넣습니다.

```bash
AIHUB_API_KEY='MY_API_KEY' #실제 API 키
```

### 2. 구글 드라이브 저장 경로 수정 (`upload_all.sh`)

- `DATASET_KEY`: AI-Hub 데이터셋 번호 (이상행동 CCTV는 `171`)
- `GDRIVE_REMOTE`: 업로드할 구글 드라이브 쪽 대상 경로.
- `LOCAL_DIR`: AI-Hub가 압축 해제하는 로컬 폴더 이름

```bash
DATASET_KEY="171"
GDRIVE_REMOTE="gdrive:Colab Notebooks/딥러닝 팀플/01_Data/이상행동 CCTV 영상"
LOCAL_DIR="19.이상행동CCTV"
```

### 3. 실행

Git Bash를 열고 `**sctipts/aihub_uploader` 폴더로 이동**한 뒤 실행합니다.

```bash
# 1. 두 방법 중 하나를 통해 aihub_uploader 폴더로 이동
cd sctipts/aihub_uploader

# 2. 실행 권한 부여 (최초 1회)
chmod +x aihubshell upload_all.sh

# 3. 백그라운드 실행 및 로그 기록
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
- **중단 시**: `upload_all.sh`에서 이미 완료된 키(Key) 번호만 삭제한 뒤 다시 실행하면 됩니다.

