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

브라우저에서 `http://localhost:8080`으로 접속하세요.

### 중지 및 제거
```bash
docker stop network-map
docker rm network-map
```

## 특징

- **인터랙티브 맵**: 패닝, 줌, 노드 클릭으로 상세 정보 확인
- **RX/TX 경로**: 수신 및 송신 경로를 시각적으로 표현
- **패킷 드롭 및 RST**: 드롭과 RST 발생 지점 표시
- **커널 옵션**: 각 기능과 연관된 커널 옵션 표시
- **상세 설명**: 각 노드의 역할, 동작 방식, sysctl 설정 등 상세 정보 제공

## 오프라인 환경

이 Docker 이미지는 외부 네트워크와 단절된 환경에서도 동작합니다. 모든 JavaScript 라이브러리는 컨테이너 내부에 포함되어 있습니다.

