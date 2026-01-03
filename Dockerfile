FROM nginx:alpine

# cytoscape.min.js 다운로드 및 저장
# 빌드 시 인터넷 연결이 필요한 경우 이 Dockerfile 사용
# 완전히 오프라인 환경인 경우 Dockerfile.offline 사용
RUN apk add --no-cache curl && \
    mkdir -p /usr/share/nginx/html/js && \
    curl -L https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js -o /usr/share/nginx/html/js/cytoscape.min.js && \
    apk del curl

# HTML 파일들 복사
COPY index.html /usr/share/nginx/html/
COPY tutorial.html /usr/share/nginx/html/

# nginx 설정 (기본 설정 사용)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

