# 리눅스 네트워크 스택 실습 튜토리얼

이 튜토리얼은 두 대의 리눅스 장비와 nginx를 사용하여 TCP/IP 네트워크 데이터 흐름과 커널의 동작을 단계별로 확인하고 실습할 수 있도록 구성되었습니다.

## 목차

1. [환경 구성](#1-환경-구성)
2. [NIC 및 Driver 레벨 실습](#2-nic-및-driver-레벨-실습)
3. [NAPI 레벨 실습](#3-napi-레벨-실습)
4. [sk_buff 레벨 실습](#4-sk_buff-레벨-실습)
5. [Netfilter Hook 실습](#5-netfilter-hook-실습)
6. [Routing 레벨 실습](#6-routing-레벨-실습)
7. [Socket 레벨 실습](#7-socket-레벨-실습)
8. [TCP 레벨 실습](#8-tcp-레벨-실습)
9. [qdisc/TC 레벨 실습](#9-qdisctc-레벨-실습)
10. [전체 흐름 추적](#10-전체-흐름-추적)

---

## 1. 환경 구성

### 1.1 두 대의 리눅스 장비 준비

**옵션 A: 물리적 장비**
- 두 대의 리눅스 서버 (Ubuntu 20.04 이상 권장)
- 네트워크 케이블로 직접 연결 또는 같은 네트워크에 연결

**옵션 B: 가상 환경 (Docker/Vagrant)**
- Docker Compose를 사용한 가상 환경 구성

**옵션 C: 단일 장비에서 네임스페이스 사용**
- 네트워크 네임스페이스를 사용하여 두 개의 가상 네트워크 인터페이스 생성

### 1.2 네트워크 설정

#### 서버 측 (nginx 서버)
```bash
# IP 주소 설정 (예시)
sudo ip addr add 192.168.100.10/24 dev eth0
sudo ip link set eth0 up

# 호스트명 설정
sudo hostnamectl set-hostname server

# 방화벽 확인 (필요시 포트 80, 443 허용)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

#### 클라이언트 측
```bash
# IP 주소 설정 (예시)
sudo ip addr add 192.168.100.20/24 dev eth0
sudo ip link set eth0 up

# 호스트명 설정
sudo hostnamectl set-hostname client

# 서버로의 연결 테스트
ping -c 3 192.168.100.10
```

### 1.3 nginx 설치 및 설정

#### 서버 측에서 nginx 설치
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y nginx

# CentOS/RHEL
sudo yum install -y nginx
```

#### nginx 기본 설정 확인
```bash
# nginx 상태 확인
sudo systemctl status nginx

# nginx 시작
sudo systemctl start nginx
sudo systemctl enable nginx

# 기본 페이지 생성
echo "Hello from Linux Network Stack Tutorial" | sudo tee /var/www/html/index.html
```

#### nginx 설정 파일 수정 (로깅 강화)
```bash
sudo nano /etc/nginx/nginx.conf
```

다음과 같이 로깅 설정 추가:
```nginx
http {
    log_format detailed '$remote_addr - $remote_user [$time_local] '
                       '"$request" $status $body_bytes_sent '
                       '"$http_referer" "$http_user_agent" '
                       'rt=$request_time uct="$upstream_connect_time" '
                       'uht="$upstream_header_time" urt="$upstream_response_time"';
    
    access_log /var/log/nginx/access.log detailed;
    error_log /var/log/nginx/error.log debug;
    
    # ... 기타 설정
}
```

설정 적용:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 1.4 필수 도구 설치

#### 서버 및 클라이언트 모두에서 설치
```bash
# 네트워크 모니터링 도구
sudo apt install -y tcpdump wireshark-common net-tools iproute2

# 커널 추적 도구
sudo apt install -y linux-tools-common linux-tools-generic
sudo apt install -y trace-cmd

# 기타 유틸리티
sudo apt install -y curl wget htop iotop ethtool

# eBPF 도구 (선택사항)
sudo apt install -y bpfcc-tools
```

---

## 2. NIC 및 Driver 레벨 실습

### 2.1 이론

**NIC (Network Interface Card) 레벨**은 물리적 네트워크 인터페이스에서 패킷을 수신하는 최하위 레벨입니다.

- **RX Ring Buffer**: NIC가 패킷을 수신할 때 DMA를 통해 커널 메모리에 직접 적재하는 링 버퍼
- **인터럽트**: 패킷 수신 시 하드웨어 인터럽트 발생
- **Driver**: NIC 하드웨어와 커널을 연결하는 드라이버

### 2.2 실습: NIC 통계 확인

#### 서버 측에서 실행

```bash
# 네트워크 인터페이스 확인
ip link show

# NIC 통계 확인 (RX/TX 패킷 수, 드롭 등)
cat /proc/net/dev

# 더 자세한 통계 (ethtool 사용)
sudo ethtool -S eth0 | grep -E "rx|tx|drop|error"

# 실시간 통계 모니터링
watch -n 1 'cat /proc/net/dev'
```

**예상 결과:**
```
Inter-|   Receive                                                |  Transmit
 face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
  eth0: 1234567    1234    0    0    0     0          0         0  9876543    987    0    0    0     0       0          0
```

### 2.3 실습: RX Ring Buffer 확인

```bash
# RX Ring Buffer 크기 확인
sudo ethtool -g eth0

# RX Ring Buffer 크기 조정 (예: 4096으로 증가)
sudo ethtool -G eth0 rx 4096

# 변경 확인
sudo ethtool -g eth0
```

**예상 결과:**
```
Ring parameters for eth0:
Pre-set maximums:
RX:     4096
RX Mini:    0
RX Jumbo:  4096
TX:     4096
Current hardware settings:
RX:     4096
RX Mini:    0
RX Jumbo:  4096
TX:     4096
```

### 2.4 실습: 인터럽트 확인

```bash
# 네트워크 인터페이스의 인터럽트 번호 확인
grep eth0 /proc/interrupts

# 실시간 인터럽트 모니터링
watch -n 1 'grep eth0 /proc/interrupts'

# 인터럽트 통계 확인
cat /proc/softirqs | grep NET
```

**예상 결과:**
```
           CPU0       CPU1       CPU2       CPU3
 24:   12345678          0          0          0   PCI-MSI-edge      eth0
```

### 2.5 실습: 패킷 수신 시뮬레이션

#### 클라이언트에서 서버로 패킷 전송
```bash
# 서버로 ping 전송 (ICMP 패킷)
ping -c 100 192.168.100.10

# 서버에서 통계 확인
watch -n 1 'cat /proc/net/dev | grep eth0'
```

#### 서버에서 인터럽트 증가 확인
```bash
# 인터럽트 카운트 확인
watch -n 1 'grep eth0 /proc/interrupts'
```

---

## 3. NAPI 레벨 실습

### 3.1 이론

**NAPI (New API)**는 고속 네트워크 환경에서 인터럽트 폭주를 방지하기 위한 메커니즘입니다.

- **인터럽트 → 폴링 전환**: 초기 인터럽트 후 폴링 모드로 전환
- **NAPI 구조체**: `struct napi_struct`로 관리
- **GRO (Generic Receive Offload)**: 여러 작은 패킷을 하나로 합침

### 3.2 실습: NAPI 통계 확인

```bash
# NAPI 관련 커널 파라미터 확인
sysctl net.core.netdev_max_backlog
sysctl net.core.netdev_budget
sysctl net.core.netdev_budget_usecs

# NAPI 통계 확인 (커널 메시지)
dmesg | grep -i napi

# 실시간 NAPI 통계 (perf 사용)
sudo perf stat -e 'net:*' -a sleep 5
```

### 3.3 실습: GRO 활성화/비활성화

```bash
# GRO 상태 확인
ethtool -k eth0 | grep generic-receive-offload

# GRO 비활성화
sudo ethtool -K eth0 gro off

# GRO 활성화
sudo ethtool -K eth0 gro on

# 변경 확인
ethtool -k eth0 | grep generic-receive-offload
```

### 3.4 실습: netdev_max_backlog 조정

```bash
# 현재 값 확인
sysctl net.core.netdev_max_backlog

# 값 증가 (예: 2000으로)
sudo sysctl -w net.core.netdev_max_backlog=2000

# 영구 적용
echo "net.core.netdev_max_backlog = 2000" | sudo tee -a /etc/sysctl.conf

# 패킷 드롭 모니터링
watch -n 1 'cat /proc/net/dev | grep -E "drop|errs"'
```

### 3.5 실습: 고속 트래픽 생성 및 NAPI 동작 확인

#### 클라이언트에서 고속 트래픽 생성
```bash
# 서버로 대량의 패킷 전송
for i in {1..1000}; do
    curl -s http://192.168.100.10/ > /dev/null
done

# 또는 더 강한 트래픽
ab -n 10000 -c 100 http://192.168.100.10/
```

#### 서버에서 NAPI 동작 확인
```bash
# 인터럽트 vs 폴링 모드 확인
watch -n 1 'cat /proc/interrupts | grep eth0'

# 백로그 상태 확인
watch -n 1 'cat /proc/net/softnet_stat'
```

---

## 4. sk_buff 레벨 실습

### 4.1 이론

**sk_buff (socket buffer)**는 리눅스 커널에서 모든 네트워크 패킷을 표현하는 핵심 데이터 구조입니다.

- **패킷 데이터와 메타데이터**: 프로토콜, 길이, 네트워크 인터페이스, 라우팅 정보 등
- **네트워크 스택 통과**: 각 계층에서 필요한 정보 추가/수정
- **주요 함수**: `build_skb()`, `netif_receive_skb()`

### 4.2 실습: sk_buff 통계 확인

```bash
# 네트워크 스택 통계 확인
cat /proc/net/sockstat

# TCP 소켓 통계
cat /proc/net/sockstat6

# 더 자세한 통계
ss -s
```

**예상 결과:**
```
sockets: used 123
TCP: inuse 10 orphan 0 tw 0 alloc 20 mem 5
UDP: inuse 5
UDPLITE: inuse 0
RAW: inuse 0
FRAG: inuse 0 memory 0
```

### 4.3 실습: 패킷 추적 (tcpdump)

#### 서버에서 패킷 캡처
```bash
# 모든 패킷 캡처
sudo tcpdump -i eth0 -n

# TCP 패킷만 캡처
sudo tcpdump -i eth0 -n tcp

# 특정 포트 (80) 패킷 캡처
sudo tcpdump -i eth0 -n port 80

# 패킷을 파일로 저장
sudo tcpdump -i eth0 -w /tmp/capture.pcap

# 저장된 파일 분석
tcpdump -r /tmp/capture.pcap -n
```

### 4.4 실습: 커널 함수 추적 (ftrace)

```bash
# ftrace 마운트 확인
mount | grep tracefs

# ftrace 활성화
sudo bash -c 'echo 1 > /sys/kernel/debug/tracing/tracing_on'

# netif_receive_skb 함수 추적
sudo bash -c 'echo netif_receive_skb > /sys/kernel/debug/tracing/set_ftrace_filter'
sudo bash -c 'echo function > /sys/kernel/debug/tracing/current_tracer'

# 추적 결과 확인
sudo cat /sys/kernel/debug/tracing/trace

# 추적 비활성화
sudo bash -c 'echo 0 > /sys/kernel/debug/tracing/tracing_on'
```

### 4.5 실습: 패킷 흐름 시각화

#### 클라이언트에서 요청 전송
```bash
curl -v http://192.168.100.10/
```

#### 서버에서 동시에 패킷 캡처
```bash
# tcpdump로 패킷 캐치
sudo tcpdump -i eth0 -n -A 'tcp port 80' &
TCPDUMP_PID=$!

# 요청 처리 후 tcpdump 종료
sleep 5
sudo kill $TCPDUMP_PID
```

---

## 5. Netfilter Hook 실습

### 5.1 이론

**Netfilter**는 리눅스 커널의 패킷 필터링 및 NAT 프레임워크입니다.

**5가지 Hook 지점:**
1. **PREROUTING**: 라우팅 결정 전 (DNAT, conntrack 시작)
2. **INPUT**: 로컬 목적지 패킷 (로컬 수신 필터링)
3. **FORWARD**: 포워딩 패킷 (라우터 역할)
4. **OUTPUT**: 로컬 생성 패킷 (로컬 송신 필터링)
5. **POSTROUTING**: 라우팅 결정 후 (SNAT, 최종 처리)

### 5.2 실습: iptables 규칙 확인

```bash
# 현재 iptables 규칙 확인
sudo iptables -L -n -v

# NAT 테이블 확인
sudo iptables -t nat -L -n -v

# mangle 테이블 확인
sudo iptables -t mangle -L -n -v

# raw 테이블 확인
sudo iptables -t raw -L -n -v
```

### 5.3 실습: PREROUTING Hook 확인

#### PREROUTING에서 패킷 로깅
```bash
# PREROUTING에 로깅 규칙 추가
sudo iptables -t raw -A PREROUTING -p tcp --dport 80 -j TRACE
sudo iptables -t raw -A PREROUTING -p tcp --dport 80 -j LOG --log-prefix "PREROUTING: "

# 로그 확인
sudo tail -f /var/log/kern.log | grep PREROUTING
```

#### 클라이언트에서 요청 전송
```bash
curl http://192.168.100.10/
```

#### 서버에서 로그 확인
```bash
sudo tail -f /var/log/kern.log
```

### 5.4 실습: INPUT Hook 확인

#### INPUT 체인에 규칙 추가
```bash
# INPUT 체인에 로깅 규칙 추가
sudo iptables -A INPUT -p tcp --dport 80 -j LOG --log-prefix "INPUT: "

# INPUT 체인에 허용 규칙 (이미 있을 수 있음)
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# 로그 확인
sudo tail -f /var/log/kern.log | grep INPUT
```

### 5.5 실습: OUTPUT Hook 확인

#### OUTPUT 체인에 규칙 추가
```bash
# OUTPUT 체인에 로깅 규칙 추가
sudo iptables -A OUTPUT -p tcp --sport 80 -j LOG --log-prefix "OUTPUT: "

# 로그 확인
sudo tail -f /var/log/kern.log | grep OUTPUT
```

### 5.6 실습: POSTROUTING Hook 확인

#### POSTROUTING에 규칙 추가
```bash
# POSTROUTING에 로깅 규칙 추가
sudo iptables -t mangle -A POSTROUTING -p tcp --sport 80 -j LOG --log-prefix "POSTROUTING: "

# 로그 확인
sudo tail -f /var/log/kern.log | grep POSTROUTING
```

### 5.7 실습: conntrack (연결 추적) 확인

```bash
# conntrack 모듈 로드 확인
lsmod | grep nf_conntrack

# 연결 추적 테이블 확인
sudo conntrack -L

# 특정 연결 확인
sudo conntrack -L -p tcp --dport 80

# 연결 추적 통계
cat /proc/net/nf_conntrack | head -20

# 실시간 연결 추적
watch -n 1 'sudo conntrack -L | wc -l'
```

### 5.8 실습: NAT 동작 확인

#### SNAT (Source NAT) 설정
```bash
# POSTROUTING에 SNAT 규칙 추가 (예시)
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# NAT 테이블 확인
sudo iptables -t nat -L -n -v
```

#### DNAT (Destination NAT) 설정
```bash
# PREROUTING에 DNAT 규칙 추가 (예시: 포트 포워딩)
sudo iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to-destination 192.168.100.10:80

# NAT 테이블 확인
sudo iptables -t nat -L -n -v
```

### 5.9 실습: 전체 Hook 순서 확인

#### 모든 Hook에 로깅 규칙 추가
```bash
# PREROUTING
sudo iptables -t raw -A PREROUTING -p tcp --dport 80 -j LOG --log-prefix "[PREROUTING] "

# INPUT
sudo iptables -A INPUT -p tcp --dport 80 -j LOG --log-prefix "[INPUT] "

# OUTPUT
sudo iptables -A OUTPUT -p tcp --sport 80 -j LOG --log-prefix "[OUTPUT] "

# POSTROUTING
sudo iptables -t mangle -A POSTROUTING -p tcp --sport 80 -j LOG --log-prefix "[POSTROUTING] "
```

#### 클라이언트에서 요청
```bash
curl http://192.168.100.10/
```

#### 서버에서 로그 확인 (Hook 순서 확인)
```bash
sudo tail -f /var/log/kern.log
```

**예상 결과:** PREROUTING → INPUT → OUTPUT → POSTROUTING 순서로 로그가 나타남

---

## 6. Routing 레벨 실습

### 6.1 이론

**Routing**은 패킷의 목적지가 로컬 시스템인지, 다른 호스트로 포워딩해야 하는지 결정하는 단계입니다.

- **FIB (Forwarding Information Base)**: 라우팅 테이블
- **로컬 수신 (INPUT)**: 목적지가 로컬인 경우
- **포워딩 (FORWARD)**: 다른 호스트로 전달해야 하는 경우

### 6.2 실습: 라우팅 테이블 확인

```bash
# 라우팅 테이블 확인
ip route show

# 더 자세한 정보
ip route show table all

# 특정 목적지에 대한 라우팅 결정 확인
ip route get 192.168.100.20

# 라우팅 캐시 확인
ip route show cache
```

### 6.3 실습: 로컬 수신 경로 확인

#### 서버에서 로컬 IP로의 라우팅 확인
```bash
# 서버의 IP 주소 확인
ip addr show eth0

# 로컬 IP로의 라우팅 결정
ip route get 192.168.100.10

# 로컬 수신 경로 확인
ip route show local
```

### 6.4 실습: 포워딩 활성화/비활성화

```bash
# 현재 포워딩 상태 확인
sysctl net.ipv4.ip_forward

# 포워딩 활성화
sudo sysctl -w net.ipv4.ip_forward=1

# 영구 적용
echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf

# 포워딩 통계 확인
cat /proc/net/snmp | grep -i forward
```

### 6.5 실습: 정적 라우팅 추가

```bash
# 정적 라우트 추가 (예시)
sudo ip route add 192.168.200.0/24 via 192.168.100.1

# 라우팅 테이블 확인
ip route show

# 라우트 삭제
sudo ip route del 192.168.200.0/24
```

### 6.6 실습: 라우팅 결정 추적

```bash
# 라우팅 관련 커널 함수 추적
sudo bash -c 'echo ip_route_input_noref > /sys/kernel/debug/tracing/set_ftrace_filter'
sudo bash -c 'echo function > /sys/kernel/debug/tracing/current_tracer'
sudo bash -c 'echo 1 > /sys/kernel/debug/tracing/tracing_on'

# 클라이언트에서 요청
# (다른 터미널에서)
curl http://192.168.100.10/

# 추적 결과 확인
sudo cat /sys/kernel/debug/tracing/trace | grep ip_route

# 추적 비활성화
sudo bash -c 'echo 0 > /sys/kernel/debug/tracing/tracing_on'
```

---

## 7. Socket 레벨 실습

### 7.1 이론

**Socket**은 커널과 사용자 공간 애플리케이션 사이의 인터페이스입니다.

- **Socket 큐**: 수신 큐 (`sk_receive_queue`), 송신 큐 (`sk_write_queue`)
- **시스템 콜**: `recv()`, `send()`, `read()`, `write()`
- **주요 함수**: `tcp_v4_rcv()`, `sock_queue_rcv_skb()`, `sk_data_ready()`

### 7.2 실습: Socket 상태 확인

```bash
# 모든 소켓 상태 확인
ss -tuln

# TCP 소켓만 확인
ss -tn

# LISTEN 상태 소켓 확인
ss -tln

# ESTABLISHED 연결 확인
ss -tn state established

# 소켓 통계
ss -s
```

### 7.3 실습: nginx 소켓 확인

#### 서버에서 nginx 소켓 확인
```bash
# nginx 프로세스 확인
ps aux | grep nginx

# nginx가 사용하는 소켓 확인
sudo ss -tnp | grep nginx

# nginx의 LISTEN 소켓 확인
sudo ss -tlnp | grep :80
```

**예상 결과:**
```
LISTEN  0  128  0.0.0.0:80  0.0.0.0:*  users:(("nginx",pid=1234,fd=6))
```

### 7.4 실습: Socket 큐 모니터링

```bash
# TCP 소켓의 수신/송신 큐 확인
ss -i

# 더 자세한 정보
ss -i -e

# 특정 연결의 큐 확인
ss -i -n 'dst 192.168.100.10:80'
```

### 7.5 실습: Socket 버퍼 크기 확인

```bash
# 소켓 버퍼 크기 확인
cat /proc/sys/net/core/rmem_default
cat /proc/sys/net/core/wmem_default
cat /proc/sys/net/core/rmem_max
cat /proc/sys/net/core/wmem_max

# TCP 소켓 버퍼 크기 확인
cat /proc/sys/net/ipv4/tcp_rmem
cat /proc/sys/net/ipv4/tcp_wmem
```

### 7.6 실습: 실시간 Socket 모니터링

#### 클라이언트에서 요청 전송
```bash
# 지속적인 요청
while true; do
    curl -s http://192.168.100.10/ > /dev/null
    sleep 1
done
```

#### 서버에서 Socket 모니터링
```bash
# 실시간 소켓 상태 확인
watch -n 1 'ss -tn state established | grep :80'

# 소켓 통계 모니터링
watch -n 1 'ss -s'
```

---

## 8. TCP 레벨 실습

### 8.1 이론

**TCP (Transmission Control Protocol)**는 신뢰성 있는 연결 지향 프로토콜입니다.

- **3-way handshake**: 연결 설정
- **흐름 제어**: 윈도우 크기 조절
- **혼잡 제어**: 네트워크 혼잡에 따른 전송 속도 조절
- **주요 함수**: `tcp_v4_rcv()`, `tcp_sendmsg()`, `tcp_v4_do_rcv()`

### 8.2 실습: TCP 연결 추적

#### 클라이언트에서 연결
```bash
# TCP 연결 생성
curl -v http://192.168.100.10/

# 또는 telnet 사용
telnet 192.168.100.10 80
```

#### 서버에서 연결 확인
```bash
# ESTABLISHED 연결 확인
ss -tn state established

# 연결 상세 정보
ss -i -n 'dst 192.168.100.10:80'
```

### 8.3 실습: TCP 3-way Handshake 확인

#### 서버에서 패킷 캡처
```bash
# SYN, SYN-ACK, ACK 패킷 캡처
sudo tcpdump -i eth0 -n 'tcp port 80 and (tcp[tcpflags] & tcp-syn != 0 or tcp[tcpflags] & tcp-ack != 0)'
```

#### 클라이언트에서 연결 시도
```bash
curl http://192.168.100.10/
```

### 8.4 실습: TCP 윈도우 크기 확인

```bash
# TCP 윈도우 크기 확인
ss -i -n 'dst 192.168.100.10:80' | grep -i cwnd

# TCP 버퍼 크기 확인
cat /proc/sys/net/ipv4/tcp_rmem
cat /proc/sys/net/ipv4/tcp_wmem
```

### 8.5 실습: TCP 혼잡 제어 알고리즘 확인

```bash
# 현재 사용 중인 혼잡 제어 알고리즘 확인
sysctl net.ipv4.tcp_congestion_control

# 사용 가능한 알고리즘 목록
cat /proc/sys/net/ipv4/tcp_available_congestion_control

# 혼잡 제어 알고리즘 변경 (예: BBR)
sudo sysctl -w net.ipv4.tcp_congestion_control=bbr

# 변경 확인
sysctl net.ipv4.tcp_congestion_control
```

### 8.6 실습: TCP 재전송 확인

```bash
# TCP 재전송 통계 확인
ss -i -n 'dst 192.168.100.10:80' | grep -i retrans

# 또는 netstat 사용
netstat -s | grep -i retrans
```

### 8.7 실습: TCP 커널 함수 추적

```bash
# tcp_v4_rcv 함수 추적
sudo bash -c 'echo tcp_v4_rcv > /sys/kernel/debug/tracing/set_ftrace_filter'
sudo bash -c 'echo function > /sys/kernel/debug/tracing/current_tracer'
sudo bash -c 'echo 1 > /sys/kernel/debug/tracing/tracing_on'

# 클라이언트에서 요청
# (다른 터미널에서)
curl http://192.168.100.10/

# 추적 결과 확인
sudo cat /sys/kernel/debug/tracing/trace | grep tcp_v4_rcv

# 추적 비활성화
sudo bash -c 'echo 0 > /sys/kernel/debug/tracing/tracing_on'
```

---

## 9. qdisc/TC 레벨 실습

### 9.1 이론

**qdisc (Queueing Discipline)**와 **TC (Traffic Control)**는 패킷 전송을 제어하는 메커니즘입니다.

- **트래픽 Shaping**: 대역폭 제한
- **트래픽 Policing**: 트래픽 제한
- **스케줄링**: 패킷 전송 순서 제어
- **주요 함수**: `dev_queue_xmit()`, `qdisc_run()`, `tc_classify()`

### 9.2 실습: qdisc 확인

```bash
# 인터페이스의 qdisc 확인
tc qdisc show dev eth0

# 더 자세한 정보
tc -s qdisc show dev eth0

# 기본 qdisc 확인
sysctl net.core.default_qdisc
```

### 9.3 실습: qdisc 통계 확인

```bash
# qdisc 통계 확인
tc -s qdisc show dev eth0

# 클래스별 통계 (있는 경우)
tc -s class show dev eth0
```

### 9.4 실습: 트래픽 Shaping 설정

#### 대역폭 제한 설정 (예: 1Mbps)
```bash
# 기존 qdisc 제거
sudo tc qdisc del dev eth0 root

# HTB (Hierarchical Token Bucket) qdisc 추가
sudo tc qdisc add dev eth0 root handle 1: htb default 30

# 클래스 추가 (1Mbps 제한)
sudo tc class add dev eth0 parent 1: classid 1:1 htb rate 1mbit

# 서브클래스 추가
sudo tc class add dev eth0 parent 1:1 classid 1:10 htb rate 1mbit ceil 1mbit

# 필터 추가
sudo tc filter add dev eth0 protocol ip parent 1:0 prio 1 u32 match ip dst 192.168.100.20/32 flowid 1:10

# 설정 확인
tc -s qdisc show dev eth0
tc -s class show dev eth0
```

#### 클라이언트에서 대역폭 테스트
```bash
# 대역폭 테스트
curl -o /dev/null http://192.168.100.10/large-file
```

### 9.5 실습: qdisc 큐 모니터링

```bash
# qdisc 큐 길이 확인
tc -s qdisc show dev eth0 | grep backlog

# 실시간 모니터링
watch -n 1 'tc -s qdisc show dev eth0'
```

### 9.6 실습: qdisc 제거

```bash
# 모든 qdisc 제거
sudo tc qdisc del dev eth0 root

# 확인
tc qdisc show dev eth0
```

---

## 10. 전체 흐름 추적

### 10.1 이론

전체 네트워크 스택을 통과하는 패킷의 흐름을 추적하여 각 계층에서의 동작을 확인합니다.

### 10.2 실습: 종합 추적 스크립트

#### 서버에서 실행할 추적 스크립트 생성

```bash
cat > /tmp/trace_network.sh << 'EOF'
#!/bin/bash

echo "=== 네트워크 스택 종합 추적 시작 ==="
echo "시간: $(date)"
echo ""

# 1. NIC 통계
echo "--- NIC 통계 ---"
cat /proc/net/dev | grep eth0
echo ""

# 2. 인터럽트 통계
echo "--- 인터럽트 통계 ---"
grep eth0 /proc/interrupts
echo ""

# 3. 소켓 상태
echo "--- 소켓 상태 ---"
ss -tn state established | grep :80 | head -5
echo ""

# 4. Netfilter 규칙
echo "--- Netfilter 규칙 (간략) ---"
sudo iptables -L -n -v | head -10
echo ""

# 5. 라우팅 테이블
echo "--- 라우팅 테이블 ---"
ip route show | head -5
echo ""

# 6. qdisc 상태
echo "--- qdisc 상태 ---"
tc qdisc show dev eth0
echo ""

echo "=== 추적 완료 ==="
EOF

chmod +x /tmp/trace_network.sh
```

#### 실시간 모니터링
```bash
# 실시간 모니터링 (5초마다)
watch -n 5 /tmp/trace_network.sh
```

### 10.3 실습: 패킷 흐름 전체 추적

#### 서버에서 패킷 캡처 시작
```bash
# 패킷을 파일로 저장
sudo tcpdump -i eth0 -w /tmp/full_trace.pcap -n 'tcp port 80' &
TCPDUMP_PID=$!
```

#### 클라이언트에서 요청
```bash
# HTTP 요청 전송
curl -v http://192.168.100.10/
```

#### 서버에서 캡처 종료 및 분석
```bash
# tcpdump 종료
sudo kill $TCPDUMP_PID

# 패킷 분석
tcpdump -r /tmp/full_trace.pcap -n -A
```

### 10.4 실습: 커널 함수 전체 추적

```bash
# 여러 함수 동시 추적
sudo bash -c 'echo "netif_receive_skb
ip_rcv
tcp_v4_rcv
sock_queue_rcv_skb" > /sys/kernel/debug/tracing/set_ftrace_filter'

sudo bash -c 'echo function_graph > /sys/kernel/debug/tracing/current_tracer'
sudo bash -c 'echo 1 > /sys/kernel/debug/tracing/tracing_on'

# 클라이언트에서 요청
# (다른 터미널에서)
curl http://192.168.100.10/

# 추적 결과 확인
sudo cat /sys/kernel/debug/tracing/trace | head -100

# 추적 비활성화
sudo bash -c 'echo 0 > /sys/kernel/debug/tracing/tracing_on'
```

### 10.5 실습: 성능 분석 (perf)

```bash
# perf로 네트워크 관련 함수 프로파일링
sudo perf record -e 'net:*' -a sleep 10

# 결과 확인
sudo perf report

# 특정 함수 프로파일링
sudo perf record -g -e 'net:*' -a sleep 10
sudo perf report -g 'graph,0.5,caller'
```

---

## 부록: 유용한 명령어 모음

### 네트워크 인터페이스
```bash
ip link show                    # 인터페이스 목록
ip addr show                    # IP 주소 확인
ethtool eth0                    # NIC 정보
ethtool -S eth0                # NIC 통계
```

### 패킷 추적
```bash
tcpdump -i eth0 -n             # 패킷 캡처
tcpdump -i eth0 -w file.pcap   # 파일로 저장
wireshark file.pcap            # GUI로 분석
```

### 소켓 및 연결
```bash
ss -tuln                       # 모든 소켓
ss -tn state established       # ESTABLISHED 연결
netstat -tuln                  # 소켓 (구버전)
lsof -i :80                    # 포트 사용 프로세스
```

### 라우팅
```bash
ip route show                  # 라우팅 테이블
ip route get <dest>            # 특정 목적지 라우팅
route -n                       # 라우팅 테이블 (구버전)
```

### Netfilter
```bash
iptables -L -n -v              # 규칙 확인
iptables -t nat -L -n -v        # NAT 테이블
conntrack -L                   # 연결 추적
```

### 커널 추적
```bash
dmesg                          # 커널 메시지
cat /proc/net/sockstat         # 소켓 통계
cat /proc/net/softnet_stat     # NAPI 통계
```

### 성능 모니터링
```bash
iftop                          # 대역폭 모니터링
nethogs                        # 프로세스별 네트워크 사용량
vnstat                         # 네트워크 통계
```

---

## 문제 해결

### 일반적인 문제

1. **권한 오류**: 대부분의 네트워크 모니터링 도구는 root 권한이 필요합니다.
   ```bash
   sudo <command>
   ```

2. **인터페이스 이름이 다름**: `eth0` 대신 `ens33`, `enp0s3` 등일 수 있습니다.
   ```bash
   ip link show
   ```

3. **ftrace가 작동하지 않음**: 커널이 ftrace를 지원하는지 확인
   ```bash
   ls /sys/kernel/debug/tracing
   ```

4. **conntrack이 없음**: 모듈 로드 필요
   ```bash
   sudo modprobe nf_conntrack
   ```

---

## 참고 자료

- [Linux Network Stack Documentation](https://www.kernel.org/doc/html/latest/networking/)
- [Cytoscape.js Network Flow Map](../index.html)
- [PROTO.md](../PROTO.md) - 네트워크 스택 이론 설명
- [iptables Tutorial](https://www.netfilter.org/documentation/)
- [TCP/IP Illustrated](https://en.wikipedia.org/wiki/TCP/IP_Illustrated)

---

## 라이선스

이 튜토리얼은 교육 목적으로 자유롭게 사용할 수 있습니다.

