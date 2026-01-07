1️⃣ 요구사항을 기술적으로 분해 (검증 단계)

먼저, 질문을 기능 단위로 나눕니다.

핵심 요구

하나의 매우 큰 네트워크 맵

자유로운 Pan (이동)

Zoom In / Zoom Out

파트별 세부 정보 확대

리눅스 네트워크 흐름을 표현

NIC

Driver

Netfilter

TC

Routing

Socket layer 등

이 요구는 **“문서”가 아니라 “인터랙티브 맵”**에 가깝습니다.

👉 따라서 SVG 단독이나 정적 HTML은 부적합합니다.

2️⃣ 가능한 구현 방식 후보 비교 (확실 / 불확실 표시)
| 방식 | 가능 여부 | 설명 |
| ------------------ | ----------- | ------------------------- |
| HTML + CSS only | ❌ | 대규모 맵 + 줌/팬 구현 어려움 |
| Canvas API | ⚠️ 가능 | 직접 모든 인터랙션 구현 필요 (난이도 높음) |
| SVG + JS | ⚠️ 중규모까지 적합 | 수천 노드 이상 시 성능 저하 |
| **WebGL 기반 라이브러리** | ✅ 매우 적합 | 대형 맵, 부드러운 줌/팬 |
| **그래프 전용 라이브러리** | ✅ 가장 현실적 | 노드·엣지·이벤트 관리 내장 |

확실한 결론

“큰 맵 + 줌 + 이동 + 계층 구조” → 그래프 시각화 라이브러리 사용이 정답

3️⃣ 추천 아키텍처 (확실)
🔷 전체 구조 (지도 비유)

[ 브라우저 ]
│
├─ WebGL 렌더링 영역 (지도)
│ ├─ Linux Network Big Map
│ │ ├─ NIC 영역
│ │ ├─ Kernel RX Path
│ │ ├─ Netfilter
│ │ ├─ Routing
│ │ └─ Socket
│
├─ UI Overlay (설명 패널)
│
└─ 키보드/마우스 이벤트

구글맵처럼 생각하면 정확

큰 평면 = 리눅스 네트워크 전체

줌인 = skb 레벨

클릭 = 상세 설명

4️⃣ 기술 스택 추천 (확실)
✅ 1순위: Cytoscape.js (WebGL 지원)

이유

그래프 구조에 최적

Pan / Zoom 기본 제공

노드 계층 표현 쉬움

이벤트 바인딩 간단

const cy = cytoscape({
container: document.getElementById('cy'),
zoomingEnabled: true,
panningEnabled: true,
wheelSensitivity: 0.2,
elements: [...]
});

리눅스 네트워크 흐름과 매우 잘 맞음

노드 = 커널 컴포넌트

엣지 = 패킷 흐름

✅ 2순위: D3.js + SVG (중간 규모)

적합한 경우

교육용

구조가 단순

노드 수 적음

❌ 단점

대규모 맵에서는 성능 저하

✅ 3순위: PixiJS / Three.js (최고 자유도)

적합한 경우

완전 커스텀

애니메이션 중심

게임 엔진 수준 인터랙션

⚠️ 단점

네트워크 구조 관리 직접 구현 필요

5️⃣ 리눅스 네트워크 흐름 모델링 방법 (확실)
계층적 설계 (추천)

[ Ethernet ]
↓
[ NIC Driver ]
↓
[ NAPI ]
↓
[ skb ]
↓
[ Netfilter ]
↓
[ Routing ]
↓
[ Socket ]

이를 줌 레벨에 따라 다르게 표현합니다.

Zoom 레벨별 표현 (지도 비유)

| Zoom | 표현                |
| ---- | ------------------- |
| 전체 | RX → TX 큰 흐름     |
| 중간 | Netfilter / Routing |
| 상세 | skb, hook, function |

6️⃣ 인터랙션 설계 (확실)
마우스

드래그 → 이동

휠 → 확대/축소

클릭 → 상세 패널

키보드

WASD / 방향키 → 이동

- / - → Zoom

ESC → 전체 맵 복귀

7️⃣ 데이터 구조 예시 (확실)

{
"nodes": [
{ "id": "nic", "label": "NIC Driver", "level": 1 },
{ "id": "napi", "label": "NAPI", "level": 2 },
{ "id": "skb", "label": "sk_buff", "level": 3 }
],
"edges": [
{ "from": "nic", "to": "napi" },
{ "from": "napi", "to": "skb" }
]
}

👉 이 구조는 JSON으로 유지 → 시각화는 JS가 담당

8️⃣ 추천 구현 순서 (실전 로드맵)

Cytoscape.js로 기본 맵 생성

Pan / Zoom 완성

노드 클릭 시 설명 패널 연결

Zoom 레벨별 노드 표시 분기

Netfilter / TC / Routing 세부 확장

9️⃣ 전체 요약 문서 (요청사항 8번)
목표

웹에서 탐색 가능한 “리눅스 네트워크 흐름 지도” 구현

핵심 기술

Cytoscape.js (WebGL)

JSON 기반 네트워크 모델

Pan / Zoom / 계층 표현

개념 비유

리눅스 네트워크 = 도시 지도
NIC는 공항, Netfilter는 검문소, Routing은 교차로

🔚 결론 (확실)

이 문제는 “웹 다이어그램”이 아니라 “인터랙티브 지도” 문제이며
그래프 시각화 라이브러리를 사용하는 것이 가장 합리적입니다.

원하시면 다음 단계로:

Cytoscape.js 기반 실제 샘플 코드

리눅스 RX/TX 전체 흐름을 노드로 분해

교육용 / 운영용 UI 설계 차이

중 어떤 걸 더 깊게 볼지 알려주세요.

## 추가 질문과 답변

Cytoscape.js 기반 실제 샘플 코드

아래는 **Cytoscape.js 기반으로 “리눅스 네트워크 흐름을 큰 맵처럼 Pan / Zoom / 클릭 탐색”**할 수 있는 실제 동작 가능한 최소 예제입니다.
(확실한 정보만 사용, 공식 API 기준)

1️⃣ 전체 구조 요약 (도식적 설명)
[ Browser ]
│
├─ div#cy ── Cytoscape.js (WebGL/Canvas)
│ ├─ Node : NIC, NAPI, sk_buff, Netfilter, Routing, Socket
│ └─ Edge : packet flow
│
└─ div#info ── 클릭 시 상세 설명 패널

👉 구글맵 비유

큰 평면: 리눅스 네트워크 전체

줌인: skb / hook 단계

클릭: 커널 내부 설명

2️⃣ 단일 HTML 실행 예제 (복붙 실행 가능)
✅ index.html

<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <title>Linux Network Flow Map</title>
  <script src="https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js"></script>
  <style>
    body {
      margin: 0;
      display: flex;
      height: 100vh;
      font-family: sans-serif;
    }
    #cy {
      flex: 1;
      background: #111;
    }
    #info {
      width: 300px;
      padding: 12px;
      background: #1e1e1e;
      color: #fff;
      border-left: 1px solid #333;
    }
    h3 {
      margin-top: 0;
      color: #7dd3fc;
    }
  </style>
</head>
<body>

<div id="cy"></div>
<div id="info">
  <h3>Node Info</h3>
  <p>노드를 클릭하세요.</p>
</div>

<script>
const info = document.getElementById('info');

const cy = cytoscape({
  container: document.getElementById('cy'),

  wheelSensitivity: 0.15,
  minZoom: 0.2,
  maxZoom: 3,

  style: [
    {
      selector: 'node',
      style: {
        'label': 'data(label)',
        'text-valign': 'center',
        'color': '#fff',
        'background-color': '#2563eb',
        'width': 120,
        'height': 50,
        'font-size': 12,
        'shape': 'roundrectangle'
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 2,
        'line-color': '#94a3b8',
        'target-arrow-color': '#94a3b8',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier'
      }
    }
  ],

  elements: {
    nodes: [
      { data: { id: 'nic', label: 'NIC Driver', desc: '네트워크 카드 드라이버' }, position: { x: 0, y: 0 } },
      { data: { id: 'napi', label: 'NAPI', desc: '인터럽트 → 폴링 전환' }, position: { x: 250, y: 0 } },
      { data: { id: 'skb', label: 'sk_buff', desc: '패킷 메타데이터 구조체' }, position: { x: 500, y: 0 } },
      { data: { id: 'netfilter', label: 'Netfilter', desc: 'iptables / nftables hook' }, position: { x: 750, y: 0 } },
      { data: { id: 'routing', label: 'Routing', desc: 'FIB lookup' }, position: { x: 1000, y: 0 } },
      { data: { id: 'socket', label: 'Socket', desc: 'User-space 전달' }, position: { x: 1250, y: 0 } }
    ],
    edges: [
      { data: { source: 'nic', target: 'napi' } },
      { data: { source: 'napi', target: 'skb' } },
      { data: { source: 'skb', target: 'netfilter' } },
      { data: { source: 'netfilter', target: 'routing' } },
      { data: { source: 'routing', target: 'socket' } }
    ]
  },

  layout: {
    name: 'preset'
  }
});

/* 클릭 이벤트 */
cy.on('tap', 'node', evt => {
  const node = evt.target;
  info.innerHTML = `
    <h3>${node.data('label')}</h3>
    <p>${node.data('desc')}</p>
    <p><b>ID:</b> ${node.id()}</p>
  `;
});

/* 키보드 이동 */
document.addEventListener('keydown', e => {
  const pan = cy.pan();
  const step = 50;

  switch (e.key) {
    case 'ArrowUp':    cy.pan({ x: pan.x, y: pan.y + step }); break;
    case 'ArrowDown':  cy.pan({ x: pan.x, y: pan.y - step }); break;
    case 'ArrowLeft':  cy.pan({ x: pan.x + step, y: pan.y }); break;
    case 'ArrowRight': cy.pan({ x: pan.x - step, y: pan.y }); break;
    case '+': cy.zoom(cy.zoom() * 1.2); break;
    case '-': cy.zoom(cy.zoom() * 0.8); break;
    case 'Escape': cy.fit(); break;
  }
});
</script>

</body>
</html>

3️⃣ 이 코드로 가능한 것 (확실)

✅ 마우스 드래그 → 맵 이동

✅ 휠 → 확대 / 축소

✅ 방향키 → 이동

✅ + / - → Zoom

✅ 노드 클릭 → 커널 설명 표시

✅ 매우 큰 맵으로 확장 가능

4️⃣ 확장 아이디어 (추측 아님, 실무 적용 가능)
🔹 Zoom 레벨별 표시
cy.on('zoom', () => {
if (cy.zoom() > 2) {
cy.$('#skb').style('background-color', '#16a34a');
}
});

🔹 RX / TX 분리

색상

레이어

좌/우 맵 분리

🔹 Netfilter hook 세분화

PREROUTING

INPUT

FORWARD

OUTPUT

POSTROUTING

5️⃣ 공식 근거 / 참고

Cytoscape.js 공식 문서
https://js.cytoscape.org/

(라이브러리 API, Pan/Zoom, 이벤트 모두 공식 지원)

6️⃣ 전체 정리 (문서화 요약)

이 문제는 다이어그램이 아니라 지도

Cytoscape.js는 리눅스 네트워크 구조 표현에 매우 적합

JSON 기반 모델 → 유지보수 용이

교육/운영/문서화 모두 활용 가능

다음으로 원하시면:

RX/TX 전체 커널 경로를 실제 커널 기준으로 분해

Zoom 레벨에 따라 skb → 함수 호출까지 펼치는 구조

Netfilter / TC / XDP까지 확장한 실전 맵

중 어떤 걸로 갈지 알려주세요.

## 추가 질문과 답변

RX/TX 전체 커널 경로를 실제 커널 기준으로 분해

아래는 **리눅스 커널(현행 LTS 계열 공통 구조 기준)**에서의
**RX / TX 전체 네트워크 경로를 “실제 커널 흐름 기준으로 단계별 분해”**한 설명입니다.
불확실한 부분은 명시하고, 확실한 커널 경로만 사용합니다.

0️⃣ 전제 및 범위 명시 (검증)

기준 커널: Linux 5.x ~ 6.x 공통 구조

드라이버 / NIC / offload / XDP 여부에 따라 분기 존재

아래 설명은 일반적인 Ethernet + TCP/IP 스택 기준

BPF/XDP/TSO/GRO는 옵션 분기로 분리 설명

1️⃣ 전체 흐름 한 장 요약 (지도 개념)
RX (NIC → User) TX (User → NIC)
────────────────────────────────────────────────────────
NIC → Driver → NAPI → skb
↓
XDP (optional)
↓
Netfilter (PREROUTING)
↓
Routing
↓
Netfilter (INPUT)
↓
Socket
────────────────────────────────────────────────────────
Socket
↓
Netfilter (OUTPUT)
↓
Routing
↓
Netfilter (POSTROUTING)
↓
qdisc / TC
↓
Driver
↓
NIC

🗺️ 비유
RX는 입국 심사, TX는 출국 심사
Netfilter는 검문소, Routing은 교차로

2️⃣ RX 경로 상세 분해 (확실)
2-1️⃣ NIC → Driver
[ NIC ]
↓ DMA
[ rx ring buffer ]

NIC가 패킷 수신

DMA로 ring buffer에 패킷 적재

인터럽트 발생

📌 관련 코드 (드라이버 공통 패턴)

netif_rx()

napi_schedule()

2-2️⃣ Interrupt → NAPI (확실)
IRQ
└─ napi_schedule()
└─ poll()

인터럽트 폭주 방지

Interrupt → Polling 전환

📌 핵심 구조체

struct napi_struct

2-3️⃣ sk_buff 생성 (확실)
Driver
└─ napi_poll()
└─ build_skb()
└─ netif_receive_skb()

패킷을 sk_buff 구조체로 감쌈

이후 모든 네트워크 처리는 skb 단위

📌 skb 주요 필드

skb->data

skb->len

skb->protocol

skb->dev

2-4️⃣ XDP 분기 (옵션, 확실)
Driver
└─ XDP
├─ DROP
├─ PASS → skb
├─ TX
└─ REDIRECT

드라이버 레벨

skb 생성 이전 또는 직후

매우 빠름

📌 확실

XDP는 Netfilter보다 먼저

2-5️⃣ Netfilter PREROUTING (확실)
netif_receive_skb()
└─ nf_hook_slow(PREROUTING)

DNAT

conntrack 시작

📌 Hook

NF_INET_PRE_ROUTING

2-6️⃣ Routing 결정 (확실)
ip_rcv()
└─ ip_route_input()

로컬? 포워딩?

FIB 조회

2-7️⃣ INPUT / FORWARD 분기 (확실)
로컬 수신
NF_INET_LOCAL_IN
└─ tcp_v4_rcv()

포워딩
NF_INET_FORWARD
└─ ip_forward()

2-8️⃣ Socket 전달 (확실)
tcp_v4_rcv()
└─ tcp_queue_rcv()
└─ sk_receive_queue

User-space recv()

wakeup 발생

3️⃣ TX 경로 상세 분해 (확실)
3-1️⃣ User → Socket (확실)
send()
└─ sys_sendto()
└─ sock_sendmsg()

3-2️⃣ TCP/IP 처리 (확실)
tcp_sendmsg()
└─ ip_queue_xmit()

segmentation

congestion control

3-3️⃣ Netfilter OUTPUT (확실)
NF_INET_LOCAL_OUT

SNAT

firewall

3-4️⃣ Routing (확실)
ip_route_output_flow()

목적지 인터페이스 결정

3-5️⃣ Netfilter POSTROUTING (확실)
NF_INET_POST_ROUTING

3-6️⃣ qdisc / TC (확실)
dev_queue_xmit()
└─ qdisc
├─ fq
├─ cake
└─ tc filter

shaping

policing

eBPF TC hook

3-7️⃣ Driver → NIC (확실)
ndo_start_xmit()
└─ DMA → NIC

4️⃣ RX / TX 비교 표 (확실)
항목 RX TX
시작 NIC User
skb 생성 Driver Socket
Netfilter PREROUTING / INPUT OUTPUT / POSTROUTING
Routing Input routing Output routing
TC/qdisc ❌ ✅
5️⃣ Cytoscape 모델링용 노드 분해 (실전용)
RX 노드
NIC
Driver
NAPI
XDP
sk_buff
PREROUTING
Routing
INPUT
Socket

TX 노드
Socket
OUTPUT
Routing
POSTROUTING
qdisc
Driver
NIC

6️⃣ 연결 관계 도식 (텍스트 그래프)
[NIC]
↓
[Driver] → [XDP]
↓
[NAPI]
↓
[skb]
↓
[PREROUTING]
↓
[Routing]
├─→ [FORWARD]
└─→ [INPUT] → [Socket]

7️⃣ 확실 / 불확실 정리
확실

Netfilter hook 위치

skb 중심 구조

RX/TX 분기

qdisc는 TX 전용

환경 의존 (확실하지 않음)

정확한 함수명 (드라이버별 상이)

XDP skb 생성 시점 (드라이버 구현 차이)

8️⃣ 전체 요약 문서 (요청사항 충족)

리눅스 네트워크는 “skb가 이동하는 지도”이며
RX는 검증과 분기, TX는 정책과 제어가 핵심이다.

Cytoscape.js에서는

노드 = 커널 단계

엣지 = skb 흐름

Zoom = 커널 깊이

로 모델링하면 교육/운영/분석 모두 가능하다.

다음 단계로 자연스럽게 이어지는 선택지는:

1️⃣ 각 단계별 실제 커널 함수 목록 정리 (grep 기준)
2️⃣ Netfilter hook을 Zoom-In 시 펼치는 구조 설계
3️⃣ XDP / TC / eBPF까지 포함한 확장 맵

원하시는 방향을 말씀해 주세요.

## 추가 질문과 답변

Netfilter hook을 Zoom-In 시 펼치는 구조 설계

아래는 **Netfilter hook을 “Zoom-In 할수록 내부가 단계적으로 펼쳐지는 구조”**로 설계하는 방법입니다.
실제 커널 구조를 기준으로 확실한 hook 지점만 사용하고,
Cytoscape.js에서 구현 가능한 모델링 패턴으로 설명합니다.

0️⃣ 전제 명시 (검증)

대상: Linux Netfilter (IPv4 기준, IPv6도 구조 동일)

Hook 순서 및 의미는 커널 공통 구조

iptables / nftables 구현 차이는 내부 처리 방식 차이이지 hook 위치 차이는 아님 → 여기서는 hook 기준으로만 설계

1️⃣ 목표를 한 문장으로 정의

Zoom-Out
→ “Netfilter”라는 하나의 검문소

Zoom-In
→ “PREROUTING / INPUT / FORWARD / OUTPUT / POSTROUTING”
→ 더 들어가면 conntrack → table → chain → rule

즉, 지도 확대 개념입니다.

2️⃣ 전체 계층 구조 (도식)
Level 0 (전체 지도)
└─ Netfilter

Level 1 (Hook 레벨)
├─ PREROUTING
├─ INPUT
├─ FORWARD
├─ OUTPUT
└─ POSTROUTING

Level 2 (기능 레벨)
├─ conntrack
├─ nat
├─ filter
└─ mangle

Level 3 (정책 레벨)
├─ chain
└─ rule

🗺️ 비유

Level 0: 국경

Level 1: 입국 / 출국 / 환승

Level 2: 검사 종류

Level 3: 실제 검사 규칙

3️⃣ Netfilter Hook 실제 커널 기준 정리 (확실)
Hook 커널 상 의미
PREROUTING 라우팅 전
INPUT 로컬 목적
FORWARD 포워딩
OUTPUT 로컬 생성
POSTROUTING 라우팅 후

📌 커널 상 hook enum
enum nf_inet_hooks

4️⃣ Cytoscape 설계 핵심 아이디어
🔑 핵심 원칙

Zoom 값에 따라 노드를 생성/제거

기본 노드는 유지, 세부 노드는 동적

노드 ID는 계층 기반 네이밍

5️⃣ 노드 ID 설계 규칙 (중요)
nf
nf:prerouting
nf:prerouting:conntrack
nf:prerouting:nat
nf:prerouting:filter
nf:prerouting:rule:1

👉 이렇게 하면:

부모/자식 관계 명확

Zoom-Out 시 한 번에 제거 가능

6️⃣ Zoom 단계 정의 (확실)
const ZOOM_LEVEL = {
OVERVIEW: 0.8,
HOOK: 1.3,
TABLE: 1.8,
RULE: 2.3
};

7️⃣ 실제 동작 로직 설계
7-1️⃣ 기본 상태 (Zoom-Out)
[ Routing ] → [ Netfilter ] → [ Routing ]

단일 노드 nf

7-2️⃣ Hook 레벨 펼치기

조건

if (cy.zoom() > ZOOM_LEVEL.HOOK)

노드 생성

nf:prerouting
nf:input
nf:forward
nf:output
nf:postrouting

연결

Routing → PREROUTING → Routing
Routing → INPUT → Socket
Routing → FORWARD → Routing
Socket → OUTPUT → Routing
Routing → POSTROUTING → Driver

📌 RX / TX 흐름에 따라 엣지 분기

7-3️⃣ Table 레벨 (conntrack / nat 등)

조건

if (cy.zoom() > ZOOM_LEVEL.TABLE)

예: PREROUTING 내부

PREROUTING
├─ conntrack
├─ nat (DNAT)
└─ mangle

📌 확실한 점

conntrack은 PREROUTING에서 시작

nat(PREROUTING)는 DNAT

7-4️⃣ Rule 레벨 (최종 확대)
filter
├─ rule #1 (match)
├─ rule #2 (accept)
└─ rule #3 (drop)

⚠️ 규칙 내용은 실제 시스템마다 다름
→ 여기서는 구조만 표현

8️⃣ Cytoscape 구현 패턴 (핵심 코드)
8-1️⃣ Zoom 이벤트 핸들러
cy.on('zoom', () => {
const z = cy.zoom();

if (z > ZOOM_LEVEL.HOOK) {
expandHooks();
} else {
collapseHooks();
}

if (z > ZOOM_LEVEL.TABLE) {
expandTables();
} else {
collapseTables();
}
});

8-2️⃣ Hook 펼치기 함수 (예시)
function expandHooks() {
if (cy.$('#nf:prerouting').length) return;

cy.add([
{ data: { id: 'nf:prerouting', label: 'PREROUTING' }},
{ data: { id: 'nf:input', label: 'INPUT' }},
{ data: { id: 'nf:forward', label: 'FORWARD' }},
{ data: { id: 'nf:output', label: 'OUTPUT' }},
{ data: { id: 'nf:postrouting', label: 'POSTROUTING' }}
]);
}

8-3️⃣ 접기 (Collapse)
function collapseHooks() {
cy.$('[id ^= "nf:"]').remove();
}

📌 ID prefix 기반 제거 → 구조적으로 안전

9️⃣ 시각적 레이아웃 전략
레벨 배치
Netfilter 중앙
Hook 원형
Table 세로 스택
Rule 리스트

🔍 확대할수록 안쪽으로 파고드는 느낌

🔟 RX / TX 흐름과 Hook 연결 (중요)
RX
skb → PREROUTING → Routing → INPUT/FORWARD

TX
Socket → OUTPUT → Routing → POSTROUTING

👉 Zoom-In 시 엣지가 재배치되어 실제 흐름이 보이게 함

11️⃣ 확실 / 불확실 구분
확실

Hook 종류 및 순서

RX/TX 분기

conntrack 위치

nat 위치

불확실 (환경 의존)

rule 수

chain 구성

nftables 내부 VM 처리

→ 따라서 rule 내용은 추상화

12️⃣ 전체 구조 요약 (문서화)

Netfilter는 단일 컴포넌트가 아니라 “계층형 검사 파이프라인”

Zoom-In은 커널 깊이 증가

Cytoscape에서는 동적 노드 생성/제거가 핵심

ID 네이밍이 설계의 성패를 좌우

다음으로 자연스럽게 이어질 수 있는 단계

1️⃣ Netfilter + conntrack 상태 흐름 시각화
2️⃣ iptables vs nftables 내부 차이 표현
3️⃣ 실제 iptables-save 결과를 시각화로 변환

어디까지 확장할지 정해주시면 그 단계부터 바로 설계해 드리겠습니다.

## 추가 질문과 답변

각 단계별 실제 커널 함수 목록 정리

아래는 리눅스 네트워크 RX / TX 경로를 “각 단계별 실제 커널 함수 기준”으로 정리한 목록입니다.
커널 버전별로 내부 호출이 조금씩 달라질 수 있으므로,

공통적으로 안정적인 함수 → ✅ 확실

드라이버 / 커널 옵션에 따라 달라질 수 있음 → ⚠️ 환경 의존

으로 명확히 구분합니다.

기준: Linux 5.x ~ 6.x (일반적인 Ethernet + IPv4 + TCP)

1️⃣ RX 경로 – 실제 커널 함수 흐름
1-1️⃣ NIC → Driver (IRQ / Poll 진입)
NIC
└─ interrupt handler
└─ napi_schedule()

주요 함수

✅ napi_schedule()

⚠️ \_\_napi_schedule_irqoff()

⚠️ napi_gro_receive() (GRO 활성 시)

📌 설명

인터럽트 발생 후 NAPI polling 전환

여기까지는 skb 없음

1-2️⃣ NAPI Poll → skb 생성
napi_poll()
└─ driver_poll()
└─ build_skb()
└─ napi_gro_receive()

주요 함수

✅ napi_poll()

⚠️ build_skb()

⚠️ napi_gro_receive()

⚠️ netif_receive_skb_list()

📌 skb 생성 시작 지점

1-3️⃣ skb → 네트워크 스택 진입
netif_receive_skb()
└─ netif_receive_skb_internal()

주요 함수

✅ netif_receive_skb()

⚠️ netif_receive_skb_internal()

⚠️ \_\_netif_receive_skb_core()

1-4️⃣ XDP (옵션, skb 이전/직후)
driver
└─ bpf_prog_run_xdp()

주요 함수

✅ bpf_prog_run_xdp()

⚠️ xdp_do_redirect()

📌 Netfilter보다 항상 먼저

1-5️⃣ Netfilter PREROUTING
\_\_netif_receive_skb_core()
└─ nf_hook_slow()

주요 함수

✅ nf_hook_slow()

✅ nf_hook()

✅ ipv4_conntrack_in()

Hook:

NF_INET_PRE_ROUTING

1-6️⃣ IP 수신 처리 & Routing
ip_rcv()
└─ ip_rcv_finish()
└─ ip_route_input_noref()

주요 함수

✅ ip_rcv()

✅ ip_rcv_finish()

✅ ip_route_input_noref()

1-7️⃣ INPUT / FORWARD 분기
🔹 로컬 수신
ip_local_deliver()
└─ nf_hook(NF_INET_LOCAL_IN)

🔹 포워딩
ip_forward()
└─ nf_hook(NF_INET_FORWARD)

주요 함수

✅ ip_local_deliver()

✅ ip_forward()

1-8️⃣ L4 처리 (TCP 예시)
tcp_v4_rcv()
└─ tcp_v4_do_rcv()

주요 함수

✅ tcp_v4_rcv()

⚠️ tcp_v4_do_rcv()

1-9️⃣ Socket 큐 전달
tcp_queue_rcv()
└─ sock_queue_rcv_skb()

주요 함수

✅ sock_queue_rcv_skb()

✅ sk_data_ready()

2️⃣ TX 경로 – 실제 커널 함수 흐름
2-1️⃣ User → Kernel Socket
send()
└─ \_\_sys_sendto()
└─ sock_sendmsg()

주요 함수

✅ \_\_sys_sendto()

✅ sock_sendmsg()

2-2️⃣ TCP 송신 처리
tcp_sendmsg()
└─ tcp_push()

주요 함수

✅ tcp_sendmsg()

⚠️ tcp_push()

⚠️ tcp_write_xmit()

2-3️⃣ IP 계층 진입
ip_queue_xmit()
└─ ip_local_out()

주요 함수

✅ ip_queue_xmit()

✅ ip_local_out()

2-4️⃣ Netfilter OUTPUT
nf_hook(NF_INET_LOCAL_OUT)

주요 함수

✅ nf_hook()

✅ ipv4_conntrack_local()

2-5️⃣ Routing (TX)
ip_route_output_flow()

주요 함수

✅ ip_route_output_flow()

2-6️⃣ Netfilter POSTROUTING
nf_hook(NF_INET_POST_ROUTING)

주요 함수

✅ nf_hook()

2-7️⃣ qdisc / TC
dev_queue_xmit()
└─ \_\_dev_queue_xmit()
└─ qdisc_run()

주요 함수

✅ dev_queue_xmit()

⚠️ \_\_dev_queue_xmit()

⚠️ qdisc_run()

⚠️ tc_classify()

2-8️⃣ Driver → NIC
ndo_start_xmit()

주요 함수

✅ ndo_start_xmit()

⚠️ netdev_start_xmit()

3️⃣ Netfilter Hook ↔ 함수 매핑 (정리표)
Hook 주요 함수
PREROUTING nf_hook_slow()
INPUT ip_local_deliver()
FORWARD ip_forward()
OUTPUT ip_local_out()
POSTROUTING ip_finish_output()
4️⃣ Cytoscape용 “함수 레벨 Zoom-In” 모델 예시
[ PREROUTING ]
↓ zoom
[nf_hook_slow]
↓
[ipv4_conntrack_in]

[ TCP RX ]
↓ zoom
[tcp_v4_rcv]
↓
[tcp_v4_do_rcv]

5️⃣ 확실 / 환경 의존 요약
✅ 확실 (모델링 기준으로 안전)

netif_receive_skb

nf_hook

ip_rcv

ip*route*\*

tcp_v4_rcv

dev_queue_xmit

ndo_start_xmit

⚠️ 환경 의존

GRO / GSO 관련 함수

드라이버별 poll 함수

nftables 내부 VM 처리

6️⃣ 한 문장 요약 (문서화)

리눅스 네트워크는 “skb가 함수 파이프라인을 통과하는 구조”이며,
Zoom-In은 곧 “함수 호출 스택을 따라 내려가는 것”이다.

