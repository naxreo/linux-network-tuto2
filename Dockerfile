FROM nginx:alpine

# cytoscape.min.js 다운로드 및 저장
# 빌드 시 인터넷 연결이 필요한 경우 이 Dockerfile 사용
# 완전히 오프라인 환경인 경우 Dockerfile.offline 사용
RUN apk add --no-cache curl && \
    mkdir -p /usr/share/nginx/html/js && \
    curl -L https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js -o /usr/share/nginx/html/js/cytoscape.min.js && \
    apk del curl

# HTML 파일들 복사
COPY *.html /usr/share/nginx/html/

# favicon 복사
COPY favicon.svg /usr/share/nginx/html/

# 이미지 파일 복사
COPY img/ /usr/share/nginx/html/img/

# nginx 설정 파일 복사 (다수 요청 처리 최적화)
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

