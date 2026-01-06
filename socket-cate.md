0️⃣ 전체 강의 철학 (방향성)

소켓은 API가 아니라 “커널 자원 + 큐 + 상태 머신”이다

따라서 강의는 다음 3축을 계속 반복하며 전개됩니다.

[ API 관점 ] ↔ [ 커널 내부 구조 ] ↔ [ 성능 / 장애 / 튜닝 ]

1️⃣ 대주제 구조 제안 (Top-down)
📌 Chapter 1. Socket이란 무엇인가 (개념 재정의)
목적

“파일처럼 보이지만 파일이 아닌 것”이라는 본질 이해

소주제

Socket의 역사 (BSD Socket → Linux)

왜 file descriptor인가?

socket vs file vs pipe vs epoll 대상

프로세스 관점에서 본 socket lifecycle

📌 핵심 메시지

소켓은 통신용 파일이 아니라 커널 상태 머신의 핸들

📌 Chapter 2. Socket API 계층 구조
목적

syscall은 단순 인터페이스일 뿐임을 인식

소주제

socket / bind / listen / accept / connect

send / recv / read / write 차이

blocking vs non-blocking

errno의 진짜 의미

📌 실습 포인트

같은 동작을 read/write vs send/recv로 비교

📌 Chapter 3. Address Family & Socket Type
목적

“왜 이렇게 종류가 많은가?”에 답하기

소주제

AF_INET / AF_INET6 / AF_UNIX / AF_NETLINK

SOCK_STREAM / SOCK_DGRAM / SOCK_RAW

Protocol 필드의 실제 의미

동일한 send()가 내부에서 갈라지는 지점

📌 비유

소켓은 전화기, AF는 국제전화/내선, TYPE은 통화 방식

📌 Chapter 4. Kernel 내부 구조 (핵심 챕터)
목적

이 강의의 차별점

소주제

struct socket vs struct sock

sk_buff의 역할

receive queue / send queue

backlog의 종류

netdev backlog

listen backlog

socket receive buffer

📌 도식

NIC → skb → protocol → sock → recv queue → user

📌 Chapter 5. TCP Socket 심층 분석
목적

TCP를 “프로토콜”이 아니라 “상태 머신”으로 이해

소주제

TCP 3-way handshake (커널 관점)

상태 전이 다이어그램

accept queue / syn backlog

receive window / send window

tcp_rmem / tcp_wmem

📌 장애 사례

SYN flood

accept 지연

zero window

📌 Chapter 6. UDP Socket & 비연결 통신
목적

TCP 기준 사고에서 벗어나기

소주제

UDP socket의 내부 흐름

메시지 단위 수신의 의미

rmem 부족 시 드롭 구조

UDP에서 “성능 문제”가 생기는 지점

📌 실무 연결

DNS, syslog, streaming

📌 Chapter 7. Socket Buffer & Flow Control (성능 핵심)
목적

네트워크 튜닝의 본질 이해

소주제

rmem / wmem 구조

tcp autotuning

netdev_max_backlog vs rmem

socket buffer 고갈 시 현상

📌 도식 비유

고속도로 입구 / 차선 / 물류창고

📌 Chapter 8. Multiplexing & Event Model
목적

“왜 epoll이 필요한가”

소주제

select / poll / epoll 구조 비교

epoll 내부 동작 원리

edge-trigger vs level-trigger

thundering herd 문제

📌 커널 관점 강조

wait queue

wakeup 메커니즘

📌 Chapter 9. Zero-copy & 고성능 I/O
목적

커널-유저 복사의 비용 이해

소주제

copy_from_user / copy_to_user

sendfile

splice / vmsplice

MSG_ZEROCOPY (개념 수준)

📌 실무 예

Nginx

고성능 proxy

📌 Chapter 10. 장애 분석 & 디버깅
목적

“소켓 문제는 증상이 아니라 구조다”

소주제

TIME_WAIT 폭증

CLOSE_WAIT

recv stuck

send block

tcpdump vs ss vs netstat

📌 실습

ss -npi

/proc/net/tcp

📌 Chapter 11. 컨테이너 & 가상화 환경에서의 Socket
목적

현대 환경 대응

소주제

network namespace

veth

loopback

container간 socket 통신

📌 Chapter 12. 정리: Socket을 바라보는 하나의 그림
목적

모든 내용을 하나로 연결

최종 도식
Application
  ↓
Socket API
  ↓
struct socket
  ↓
struct sock
  ↓
Protocol (TCP/UDP)
  ↓
skb queue
  ↓
NIC

2️⃣ 강의 대상별 추천 깊이
대상	강조 챕터
주니어	1~3, 8
서버 개발자	4~7, 8~10
커널/인프라	4~7, 9~11
3️⃣ 강의 자료 구성 팁 (중요)

항상 3단 구성

사용자 API

커널 내부

실제 장애 사례

코드 → 구조 → 현상 순서 유지

4️⃣ 한 문장 핵심 정리

Linux Socket 강의는 “API 설명”이 아니라
“패킷이 커널을 통과하는 여정”을 가르치는 것이어야 깊어진다

원하시면 다음 단계로:

📘 각 챕터별 슬라이드 목차

🧪 실습용 데모 시나리오

🧠 면접/토론 질문 세트

🧩 커널 소스 기반 설명 포인트

중 어떤 방향으로 확장할지 말씀 주세요.