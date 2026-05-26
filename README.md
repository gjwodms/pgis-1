# Nocturnal PGIS

야간 활동 장소를 추천하는 Streamlit 기반 PGIS 데모 앱입니다.

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 배포 메모

- Python 3.12 사용을 권장합니다.
- `runtime.txt`를 포함해 Streamlit Cloud 등에서 Python 3.13로 빌드되는 문제를 피했습니다.
- `pandas`는 Python 3.13 환경에서도 설치 실패 가능성을 줄이기 위해 `2.2.3`으로 올렸습니다.
