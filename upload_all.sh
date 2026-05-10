#!/bin/bash

# 환경 변수 설정
: "${AIHUB_API_KEY:?AIHUB_API_KEY 환경 변수를 설정하세요}"
DATASET_KEY="171"
GDRIVE_REMOTE="gdrive:Colab Notebooks/26_Deeplearning/딥러닝 팀플/데이터/dataset/이상행동 CCTV 영상"
LOCAL_DIR="19.이상행동CCTV"

# 다운로드할 파일 키 리스트

# 폭행
ASSAULT_KEYS=(49825 49826 49827 49828 49829 49830 49831 49832 49833 49834 49841 49842 49843 49844 49845 49846 49847 49848 49849)
# 절도
BURGLARY_KEYS=(49765 49766 49767 49768 49772 49773 49774 49775 49776 49777 49778 49779 49780 49781)
# 실신
SWOON_KEYS=(49792 49793 49794 49795 49796 49797 49798 49803 49804 49805 49806 49696 49697 49698 49699 49700 49701 49702)
# 기물파손
VANDAL_KEYS=(49782 49784 49785 49786 49787 49788 49789 49790 49791)

# 카테고리 배열 정의
CATEGORIES=("Assault" "Burglary" "Swoon" "Vandalism")
declare -n ALL_KEYS
ALL_KEYS_LIST=("ASSAULT_KEYS" "BURGLARY_KEYS" "SWOON_KEYS" "VANDAL_KEYS")

# --- [3] 실행 로직 ---
for i in "${!CATEGORIES[@]}"; do
    CAT_NAME=${CATEGORIES[$i]}
    declare -n CURRENT_KEYS=${ALL_KEYS_LIST[$i]}
    
    echo "**********************************************"
    echo " 현재 카테고리 시작: $CAT_NAME"
    echo "**********************************************"

    for KEY in "${CURRENT_KEYS[@]}"; do
        echo ">>> [Key: $KEY] 다운로드 및 압축해제 시작..."
        
        # 다운로드 실행
        ./aihubshell -mode d -datasetkey "$DATASET_KEY" -filekey "$KEY" -aihubapikey "$AIHUB_API_KEY"

        # 폴더 존재 확인 후 전송
        if [ -d "$LOCAL_DIR" ]; then
            echo ">>> [Key: $KEY] 구글 드라이브로 전송 및 삭제 중..."
            # rclone move는 성공 시 로컬 파일을 자동 삭제함
            rclone move "./$LOCAL_DIR" "$GDRIVE_REMOTE/$CAT_NAME" --progress --transfers=4 --delete-empty-src-dirs
            echo ">>> [Key: $KEY] 처리 완료!"
        else
            echo "!!! [에러] $KEY 다운로드 실패. 네트워크나 용량을 확인하세요."
            exit 1
        fi
    done
done

echo "모든 카테고리(폭행, 절도, 실신, 기물파손) 작업이 완료되었습니다!"