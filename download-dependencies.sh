#!/bin/bash
# cytoscape.min.js 다운로드 스크립트
# 오프라인 환경에서 사용할 경우, 이 스크립트를 인터넷이 있는 환경에서 실행하여
# js/cytoscape.min.js 파일을 생성한 후 Docker 이미지를 빌드하세요.

mkdir -p js
curl -L https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js -o js/cytoscape.min.js

echo "cytoscape.min.js 다운로드 완료"

