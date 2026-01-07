# Linux Network Flow Map

리눅스 네트워크 스택의 패킷 흐름을 시각화하는 인터랙티브 맵입니다.

## Docker로 실행하기

### 방법 1: 빌드 시 다운로드 (인터넷 연결 필요)

빌드 시 cytoscape.min.js를 자동으로 다운로드합니다.

```bash
docker build -t linux-network-map .
docker run -d -p 8080:80 --name network-map linux-network-map
```

### 방법 2: 완전 오프라인 빌드

인터넷이 없는 환경에서 빌드하려면:

1. 인터넷이 있는 환경에서 의존성 다운로드:
```bash
chmod +x download-dependencies.sh
./download-dependencies.sh
```

2. 다운로드된 파일과 함께 Docker 이미지 빌드:
```bash
docker build -f Dockerfile.offline -t linux-network-map .
docker run -d -p 8080:80 --name network-map linux-network-map
```

### 실행

브라우저에서 접속:
- 네트워크 흐름도: `http://localhost:8080/index.html`
- 실습 튜토리얼: `http://localhost:8080/tutorial.html`

두 페이지는 상호 링크로 연결되어 있습니다.

### 중지 및 제거
```bash
docker stop network-map
docker rm network-map
```

## Kubernetes로 배포하기

### 사전 준비

1. Docker 이미지 빌드 및 레지스트리에 푸시:
```bash
# 이미지 빌드
docker build -t linux-network-map:latest .

# 레지스트리에 푸시 (예: Docker Hub)
docker tag linux-network-map:latest your-registry/linux-network-map:latest
docker push your-registry/linux-network-map:latest
```

2. `k8s/deployment.yaml` 파일에서 이미지 경로 수정:
```yaml
image: your-registry/linux-network-map:latest
```

### 배포

```bash
# Namespace 생성 (먼저 실행)
kubectl apply -f k8s/namespace.yaml

# 모든 리소스 배포
kubectl apply -f k8s/

# 또는 개별 배포
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

### 확인

```bash
# Namespace 확인
kubectl get namespace tuto

# Deployment 상태 확인 (namespace 지정)
kubectl get deployment linux-network-map -n tuto

# Pod 상태 확인 (namespace 지정)
kubectl get pods -l app=linux-network-map -n tuto

# Service 확인 (namespace 지정)
kubectl get service linux-network-map -n tuto

# Ingress 확인 (namespace 지정)
kubectl get ingress linux-network-map -n tuto

# 또는 모든 리소스 한번에 확인
kubectl get all -n tuto
```

### 접속

1. **Service를 통한 접속** (클러스터 내부):
```bash
# Port-forward 사용 (namespace 지정)
kubectl port-forward service/linux-network-map 8080:80 -n tuto

# 브라우저에서 접속
# http://localhost:8080/index.html
```

2. **Ingress를 통한 접속** (외부 접근):
   - `k8s/ingress.yaml`의 `host` 값을 실제 도메인으로 수정
   - DNS 설정 또는 `/etc/hosts`에 도메인 추가
   - Ingress Controller가 설치되어 있어야 함

### 삭제

```bash
# 모든 리소스 삭제
kubectl delete -f k8s/

# 또는 개별 삭제
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/ingress.yaml
kubectl delete -f k8s/namespace.yaml

# 또는 Namespace 삭제로 모든 리소스 한번에 삭제
kubectl delete namespace tuto
```

## 특징

- **인터랙티브 맵**: 패닝, 줌, 노드 클릭으로 상세 정보 확인
- **RX/TX 경로**: 수신 및 송신 경로를 시각적으로 표현
- **패킷 드롭 및 RST**: 드롭과 RST 발생 지점 표시
- **커널 옵션**: 각 기능과 연관된 커널 옵션 표시
- **상세 설명**: 각 노드의 역할, 동작 방식, sysctl 설정 등 상세 정보 제공
- **실습 튜토리얼**: 두 대의 리눅스 장비와 nginx를 사용한 단계별 실습 가이드 (`tutorial.html`)

## 마크다운을 HTML로 변환

`md_to_html.py` 스크립트를 사용하여 마크다운 파일을 HTML로 변환할 수 있습니다.

```bash
# 기본 사용법
python3 md_to_html.py TUTORIAL.md tutorial.html

# 옵션 지정 (제목, 네비게이션 링크)
python3 md_to_html.py TUTORIAL.md tutorial.html \
  "리눅스 네트워크 스택 실습 튜토리얼" \
  "index.html" \
  "← 네트워크 흐름도"
```

스크립트는 다음을 지원합니다:
- 제목 (h1-h4)
- 코드 블록 (언어별 하이라이팅)
- 인라인 코드
- 리스트 (순서 있음/없음)
- 링크
- 강조 (볼드)
- 구분선

## 오프라인 환경

이 Docker 이미지는 외부 네트워크와 단절된 환경에서도 동작합니다. 모든 JavaScript 라이브러리는 컨테이너 내부에 포함되어 있습니다.

