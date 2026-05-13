# DataFlow — 可视化数据批处理系统 开发计划

## Context

DataFlow 是一个以节点拖拽方式构建数据处理流水线的系统，支持结构化数据、非结构化文本、图片、影像、视频等多类型数据的批量处理。用户通过可视化画布连接处理节点（读取 → 转换 → 输出），系统将流水线翻译为分布式任务并异步执行。

现有基础：
- `backend/`：Spring Boot 4.0.6 + Java 21，已配置 WebFlux（响应式）、R2DBC + MySQL、MongoDB Reactive、Redis Reactive、Kafka、Security、Lombok
- `backend/compose.yaml`：已含 MySQL、MongoDB、Redis 容器
- `tailwindui_template/`：TailwindUI Vue 组件库（Composition API + `<script setup>` + @headlessui/vue + @heroicons/vue），涵盖 hero、feature、navigation、forms、tables、modals 等分类

---

## 系统架构分析与改进

### 已有技术栈评估

| 层 | 选型 | 评价 |
|---|---|---|
| Spring Boot 4 + WebFlux | 响应式非阻塞 | ✅ 适合高并发任务轮询与 SSE 推送 |
| R2DBC + MySQL | 异步关系型 | ✅ 存储任务元数据、用户信息、流水线定义 |
| MongoDB Reactive | 文档型 | ✅ 存储节点配置 JSON（schema 灵活） |
| Redis Reactive | 缓存/发布订阅 | ✅ 任务状态缓存、WebSocket session 管理 |
| Kafka | 消息队列 | ✅ 解耦 Spring Boot 与 Python Worker |
| VueFlow | 节点画布 | ✅ 专为流程图设计，拖拽成熟 |

### 架构改进建议（已融入 Plan）

1. **去掉 Celery，保留 Ray**：Celery 与 Ray 职责重叠。Ray 原生支持分布式并发、Actor 模型、数据并行，是更现代的选择；Celery 在 Python 侧仅增加复杂度。
2. **MySQL 改存核心业务数据，MongoDB 改存节点图快照**：两者互补，避免全部放 MySQL 导致 JSON 字段滥用。
3. **MinIO 统一作为对象存储**：输入文件上传、中间结果、输出产物均走 MinIO，Spring Boot 和 Python Worker 均通过 MinIO SDK 访问，避免文件路径共享问题。
4. **WebFlux SSE 替代 WebSocket 做任务进度推送**：任务进度是单向推送，SSE 更简单且天然适配 WebFlux，不需要维护双向连接。
5. **Spring Boot 作为 API Gateway + Orchestrator**：不直接执行计算，只负责接受请求→发 Kafka→响应前端。
6. **Python Ray Worker 集群独立部署**：与 Spring Boot 通过 Kafka Topic 解耦，消费任务消息、执行节点算子、回写结果。

---

## 最终系统架构

```
┌─────────────────────────────────────────────────────┐
│                      前端 (Vue 3)                     │
│  VueFlow画布  │  任务列表  │  数据预览  │  监控面板   │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP + SSE (Axios)
┌──────────────────────▼──────────────────────────────┐
│              Spring Boot 4 (WebFlux)                  │
│  AuthFilter │ PipelineController │ TaskController     │
│  FileController │ SSE Progress Emitter                 │
│     MySQL(R2DBC)  │  MongoDB  │  Redis               │
└──────┬─────────────────────────────┬────────────────┘
       │ Kafka Producer               │ MinIO (文件读写)
┌──────▼──────────────────────┐      │
│        Kafka Broker          │      │
│  topic: task.dispatch        │      │
│  topic: task.progress        │      │
└──────┬──────────────────────┘      │
       │ Kafka Consumer               │
┌──────▼──────────────────────────────▼──────────────┐
│              Python Ray Worker 集群                   │
│  ray_worker/                                          │
│    dispatcher.py   ← Kafka consumer, 分发 Ray tasks  │
│    nodes/          ← 各类节点算子实现                 │
│      csv_reader.py │ image_resize.py │ ffmpeg_node.py│
│      text_ocr.py   │ json_transform.py │ ...          │
│    reporter.py     ← 写进度到 Kafka task.progress     │
└────────────────────────────────────────────────────┘
                       │
              MinIO Object Storage
         (input/ │ temp/ │ output/ │ preview/)
```

---

## 目录结构规划

```
DataFlow/
├── backend/                          # Spring Boot 4 (已存在)
│   ├── build.gradle                  # 需补充 MinIO、JWT、MapStruct 依赖
│   ├── compose.yaml                  # 需补充 Kafka、MinIO、Zookeeper
│   └── src/main/java/com/hades/dataflow/
│       ├── config/
│       │   ├── SecurityConfig.java
│       │   ├── KafkaConfig.java
│       │   ├── MinioConfig.java
│       │   └── RedisConfig.java
│       ├── domain/
│       │   ├── entity/               # R2DBC 实体（MySQL）
│       │   │   ├── User.java
│       │   │   ├── Pipeline.java
│       │   │   └── Task.java
│       │   ├── document/             # MongoDB 文档
│       │   │   └── PipelineGraph.java
│       │   └── dto/
│       │       ├── PipelineCreateDTO.java
│       │       ├── TaskSubmitDTO.java
│       │       └── TaskProgressDTO.java
│       ├── repository/
│       │   ├── UserRepository.java   # R2DBC
│       │   ├── PipelineRepository.java
│       │   ├── TaskRepository.java
│       │   └── PipelineGraphRepository.java  # MongoDB
│       ├── service/
│       │   ├── AuthService.java
│       │   ├── PipelineService.java
│       │   ├── TaskService.java
│       │   └── MinioService.java
│       ├── controller/
│       │   ├── AuthController.java
│       │   ├── PipelineController.java
│       │   ├── TaskController.java    # 含 SSE /tasks/{id}/progress
│       │   └── FileController.java   # 预签名上传/下载 URL
│       ├── kafka/
│       │   ├── TaskProducer.java
│       │   └── ProgressConsumer.java # 消费 task.progress → 推 SSE
│       └── security/
│           ├── JwtFilter.java
│           └── JwtUtil.java
│
├── worker/                           # Python Ray Worker (新建)
│   ├── requirements.txt
│   ├── dispatcher.py                 # Kafka consumer 入口
│   ├── reporter.py                   # 进度回写 Kafka
│   ├── executor.py                   # Ray remote 任务执行器
│   └── nodes/                        # 节点算子注册表
│       ├── __init__.py               # NODE_REGISTRY dict
│       ├── base.py                   # BaseNode 抽象类
│       ├── readers/
│       │   ├── csv_reader.py
│       │   ├── json_reader.py
│       │   └── minio_reader.py
│       ├── transforms/
│       │   ├── filter_node.py
│       │   ├── map_node.py
│       │   ├── aggregate_node.py
│       │   └── json_transform.py
│       ├── media/
│       │   ├── image_resize.py
│       │   ├── image_ocr.py          # Tesseract/EasyOCR
│       │   ├── video_extract.py      # FFmpeg 抽帧
│       │   └── video_transcode.py
│       └── writers/
│           ├── minio_writer.py
│           └── csv_writer.py
│
└── frontend/                         # Vue 3 (新建)
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.ts
    └── src/
        ├── main.ts
        ├── App.vue
        ├── router/
        │   └── index.ts
        ├── stores/                   # Pinia
        │   ├── auth.ts
        │   ├── pipeline.ts
        │   └── task.ts
        ├── api/                      # Axios 封装
        │   ├── http.ts               # 拦截器、JWT header
        │   ├── pipeline.ts
        │   ├── task.ts
        │   └── file.ts
        ├── views/
        │   ├── Login.vue
        │   ├── Dashboard.vue
        │   ├── FlowEditor.vue        # 核心画布页
        │   ├── TaskMonitor.vue
        │   └── DataPreview.vue
        └── components/
            ├── flow/
            │   ├── FlowCanvas.vue    # VueFlow 主画布
            │   ├── NodePanel.vue     # 左侧节点选择面板
            │   ├── NodeConfig.vue    # 右侧节点配置抽屉
            │   └── nodes/           # 自定义节点组件
            │       ├── CsvReaderNode.vue
            │       ├── ImageNode.vue
            │       ├── TransformNode.vue
            │       └── OutputNode.vue
            ├── task/
            │   ├── TaskList.vue
            │   ├── TaskProgress.vue  # SSE 进度条
            │   └── ResultPreview.vue
            └── ui/                  # 从 tailwindui_template 复用
                ├── Navbar.vue       # 改自 navigation 模板
                ├── Modal.vue        # 改自 application-ui/modals
                └── Table.vue        # 改自 application-ui/tables
```

---

## 分阶段开发计划

### Phase 1 — 基础设施与项目初始化（第 1-2 周）

**1.1 backend 补全依赖与配置**

在 `backend/build.gradle` 补充：
```groovy
// 需新增
implementation 'io.minio:minio:8.5.17'
implementation 'io.jsonwebtoken:jjwt-api:0.12.6'
runtimeOnly 'io.jsonwebtoken:jjwt-impl:0.12.6'
runtimeOnly 'io.jsonwebtoken:jjwt-jackson:0.12.6'
implementation 'org.mapstruct:mapstruct:1.6.3'
annotationProcessor 'org.mapstruct:mapstruct-processor:1.6.3'
```

在 `backend/compose.yaml` 补充：
```yaml
services:
  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      KAFKA_KRAFT_MODE: "true"
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_NODE_ID: 1
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@localhost:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports:
      - '9092:9092'

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: dataflow
      MINIO_ROOT_PASSWORD: dataflow123
    ports:
      - '9000:9000'
      - '9001:9001'
    volumes:
      - minio_data:/data
```

**1.2 前端项目初始化**

```bash
cd DataFlow
npm create vue@latest frontend -- --ts --router --pinia
cd frontend
npm install @vue-flow/core @vue-flow/background @vue-flow/controls @vue-flow/minimap
npm install @headlessui/vue @heroicons/vue
npm install axios
npm install tailwindcss @tailwindcss/vite
```

**1.3 Python Worker 初始化**

```bash
mkdir worker && cd worker
python -m venv .venv
pip install ray kafka-python minio pillow opencv-python pytesseract ffmpeg-python pandas
```

**1.4 数据库 Schema（MySQL，R2DBC）**

```sql
CREATE TABLE users (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(64) UNIQUE NOT NULL,
  password_hash VARCHAR(256) NOT NULL,
  created_at DATETIME DEFAULT NOW()
);

CREATE TABLE pipelines (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  name VARCHAR(128) NOT NULL,
  description TEXT,
  graph_id VARCHAR(36) NOT NULL,   -- MongoDB document id
  created_at DATETIME DEFAULT NOW(),
  updated_at DATETIME DEFAULT NOW() ON UPDATE NOW()
);

CREATE TABLE tasks (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  pipeline_id BIGINT NOT NULL,
  user_id BIGINT NOT NULL,
  status ENUM('PENDING','RUNNING','SUCCESS','FAILED') DEFAULT 'PENDING',
  progress INT DEFAULT 0,
  input_path VARCHAR(512),         -- MinIO object key
  output_path VARCHAR(512),
  error_msg TEXT,
  created_at DATETIME DEFAULT NOW(),
  finished_at DATETIME
);
```

MongoDB `pipeline_graphs` collection schema（JSON）：
```json
{
  "_id": "uuid",
  "pipeline_id": 1,
  "nodes": [{"id":"n1","type":"csv_reader","position":{},"data":{"path":"..."}}],
  "edges": [{"id":"e1","source":"n1","target":"n2"}],
  "version": 1
}
```

---

### Phase 2 — 后端核心 API（第 2-4 周）

**2.1 认证模块**

- `POST /api/auth/register` → 注册，bcrypt 加密密码
- `POST /api/auth/login` → 返回 JWT（有效期 24h）
- `JwtFilter` → WebFlux ServerWebExchange 过滤，写入 ReactiveSecurityContext

**2.2 流水线 CRUD**

- `GET    /api/pipelines` → 当前用户的流水线列表
- `POST   /api/pipelines` → 创建（同时在 MongoDB 存图结构）
- `GET    /api/pipelines/{id}` → 获取含节点图
- `PUT    /api/pipelines/{id}` → 更新图（节点/边变更）
- `DELETE /api/pipelines/{id}` → 删除

**2.3 文件上传（MinIO 预签名）**

- `POST /api/files/presign-upload` → 返回 MinIO presigned PUT URL（有效 15min）
- `GET  /api/files/presign-download?key=xxx` → 返回 presigned GET URL
- 前端直接 PUT 到 MinIO，不经过 Spring Boot，避免大文件撑爆内存

**2.4 任务提交与进度 SSE**

- `POST /api/tasks` → 提交任务：
  1. 创建 Task 记录（status=PENDING）
  2. 序列化流水线图 + 输入文件 key → JSON
  3. 发 Kafka topic `task.dispatch`
  4. 返回 taskId
- `GET /api/tasks/{id}/progress` → **SSE**（`text/event-stream`）：
  - Spring WebFlux `Flux<ServerSentEvent>` 
  - 从 Redis pub/sub 订阅该 taskId 的进度频道
  - 收到消息即推送给客户端
- `GET /api/tasks` → 任务列表（分页）
- `GET /api/tasks/{id}` → 任务详情 + 结果文件 key

**2.5 ProgressConsumer（Kafka → Redis → SSE）**

```
Kafka topic: task.progress
  消息格式: { taskId, nodeId, progress(0-100), status, message }

ProgressConsumer:
  1. 更新 MySQL task.progress, task.status
  2. PUBLISH 到 Redis channel "progress:{taskId}"

SSE Controller:
  SUBSCRIBE Redis channel "progress:{taskId}" → Flux → SSE stream
```

---

### Phase 3 — Python Worker（第 3-5 周）

**3.1 节点基类**

```python
# worker/nodes/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class NodeContext:
    task_id: str
    node_id: str
    config: dict
    minio_client: Any  # minio.Minio

class BaseNode(ABC):
    @abstractmethod
    def execute(self, inputs: list, ctx: NodeContext) -> Any:
        pass
```

**3.2 节点注册表**

```python
# worker/nodes/__init__.py
from .readers.csv_reader import CsvReaderNode
from .readers.minio_reader import MinioReaderNode
from .transforms.filter_node import FilterNode
from .transforms.map_node import MapNode
from .media.image_resize import ImageResizeNode
from .media.image_ocr import ImageOCRNode
from .media.video_extract import VideoExtractNode
from .writers.minio_writer import MinioWriterNode

NODE_REGISTRY = {
    "csv_reader": CsvReaderNode,
    "minio_reader": MinioReaderNode,
    "filter": FilterNode,
    "map": MapNode,
    "image_resize": ImageResizeNode,
    "image_ocr": ImageOCRNode,
    "video_extract": VideoExtractNode,
    "minio_writer": MinioWriterNode,
}
```

**3.3 Ray 执行器**

```python
# worker/executor.py
import ray

@ray.remote
def execute_node(node_type: str, inputs: list, config: dict, ctx_dict: dict):
    from nodes import NODE_REGISTRY
    node = NODE_REGISTRY[node_type]()
    ctx = NodeContext(**ctx_dict)
    return node.execute(inputs, ctx)

def run_pipeline(graph: dict, task_id: str, reporter):
    """拓扑排序图节点，串行/并行提交 Ray remote tasks"""
    ordered_nodes = topological_sort(graph["nodes"], graph["edges"])
    results = {}
    for node in ordered_nodes:
        deps = [results[src] for src in get_input_node_ids(node, graph["edges"])]
        future = execute_node.remote(node["type"], deps, node["data"], {...})
        results[node["id"]] = ray.get(future)
        reporter.report(task_id, node["id"], progress=calc_progress(...))
```

**3.4 Kafka Dispatcher**

```python
# worker/dispatcher.py
from kafka import KafkaConsumer
import json, ray
ray.init()

consumer = KafkaConsumer("task.dispatch", bootstrap_servers="localhost:9092",
                          value_deserializer=lambda m: json.loads(m.decode()))
for msg in consumer:
    task = msg.value
    run_pipeline(task["graph"], task["taskId"], reporter)
```

**3.5 支持的节点类型清单**

| 类别 | 节点 | 实现库 |
|---|---|---|
| 读取 | CSV Reader | pandas |
| 读取 | JSON Reader | json |
| 读取 | MinIO Reader | minio-py |
| 转换 | Filter | pandas query |
| 转换 | Map (字段映射) | pandas rename/apply |
| 转换 | Aggregate (分组聚合) | pandas groupby |
| 转换 | JSON Transform (jq-like) | jmespath |
| 图像 | Image Resize | Pillow |
| 图像 | Image OCR | EasyOCR |
| 图像 | Image Format Convert | Pillow |
| 视频 | Frame Extract | OpenCV / FFmpeg |
| 视频 | Video Transcode | ffmpeg-python |
| 视频 | Audio Extract | ffmpeg-python |
| 写出 | MinIO Writer | minio-py |
| 写出 | CSV Writer | pandas to_csv |

---

### Phase 4 — 前端核心功能（第 4-7 周）

**4.1 路由结构**

```
/login          → Login.vue
/dashboard      → Dashboard.vue  (流水线列表)
/editor/:id     → FlowEditor.vue (核心画布)
/tasks          → TaskMonitor.vue
/tasks/:id      → TaskDetail.vue + ResultPreview
```

**4.2 FlowEditor.vue — 核心画布**

使用 VueFlow：
```vue
<VueFlow v-model:nodes="nodes" v-model:edges="edges"
         @node-click="onNodeClick"
         @drop="onDrop" @dragover.prevent>
  <Background />
  <Controls />
  <MiniMap />
  <template #node-csv_reader="props">
    <CsvReaderNode v-bind="props" />
  </template>
  <template #node-image_resize="props">
    <ImageResizeNode v-bind="props" />
  </template>
</VueFlow>
```

布局：
```
┌──────────┬────────────────────────────┬──────────────┐
│ 节点面板  │      VueFlow 画布           │  配置抽屉    │
│ (拖拽源) │  (节点图、连线、缩放、小地图) │ (选中节点属性)│
│          │                            │              │
│ CSV Read │                            │  路径配置    │
│ JSON Read│                            │  过滤条件    │
│ Filter   │                            │  输出格式    │
│ Map      │                            │              │
│ OCR      │                            │ [保存] [运行] │
│ Resize   │                            │              │
└──────────┴────────────────────────────┴──────────────┘
```

**4.3 Pinia Stores**

```typescript
// stores/pipeline.ts
export const usePipelineStore = defineStore('pipeline', () => {
  const pipelines = ref<Pipeline[]>([])
  const currentGraph = ref<PipelineGraph | null>(null)
  
  async function savePipeline(nodes: Node[], edges: Edge[]) {
    await api.pipeline.update(currentGraph.value!.id, { nodes, edges })
  }
  async function runPipeline(pipelineId: number, inputKey: string) {
    return api.task.submit({ pipelineId, inputKey })
  }
  return { pipelines, currentGraph, savePipeline, runPipeline }
})

// stores/task.ts
export const useTaskStore = defineStore('task', () => {
  const tasks = ref<Task[]>([])
  
  function subscribeProgress(taskId: number, onProgress: (p: number) => void) {
    const source = new EventSource(`/api/tasks/${taskId}/progress`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    source.onmessage = (e) => onProgress(JSON.parse(e.data).progress)
    return () => source.close()
  }
  return { tasks, subscribeProgress }
})
```

**4.4 UI 组件复用（tailwindui_template）**

| 组件 | 来源模板 |
|---|---|
| `Navbar.vue` | `application-ui/navigation/navbars/` |
| `Modal.vue` | `application-ui/overlays/modals/` |
| `Table.vue` | `application-ui/lists/tables/` |
| `SlideOver.vue` (配置抽屉) | `application-ui/overlays/slide-overs/` |
| `Badge.vue` (任务状态) | `application-ui/elements/badges/` |
| `ProgressBar.vue` | `application-ui/feedback/` |
| 登录页背景 | `marketing/hero-sections/01__simple-centered.vue` |

> tailwindui_template 组件均使用 `<script setup>` + Composition API + @headlessui/vue，与目标前端栈完全兼容，直接复制后修改业务逻辑即可。

**4.5 文件上传流程**

```
用户选择文件
    ↓
POST /api/files/presign-upload → { url, key }
    ↓
前端 PUT file to MinIO presigned URL（进度条显示）
    ↓
POST /api/tasks { pipelineId, inputKey: key }
    ↓
SSE /api/tasks/{id}/progress → 实时进度
```

---

### Phase 5 — 集成测试与完善（第 7-8 周）

**5.1 端到端测试场景**

1. **CSV 批处理**：上传 CSV → Filter 节点 → Aggregate 节点 → 下载结果 CSV
2. **图片批处理**：上传图片文件夹（zip）→ Image Resize → OCR → 输出文本
3. **视频处理**：上传 MP4 → Frame Extract → 输出帧图片到 MinIO
4. **混合流水线**：MinIO Reader → 多个并行转换分支 → MinIO Writer

**5.2 Spring Boot 测试**

- Controller 层：`@WebFluxTest` + MockBeans
- Service 层：单元测试 + Testcontainers（MySQL + Kafka + Redis）
- 集成测试：完整 Docker Compose 环境

**5.3 Python Worker 测试**

- 每个 Node 独立单元测试（pytest）
- 使用 minio mock 或本地 MinIO 容器

---

## 关键技术决策汇总

| 决策 | 选择 | 理由 |
|---|---|---|
| Python 调度 | Ray only（去掉 Celery） | Ray 覆盖 Celery 所有功能且更适合计算密集型 |
| 任务进度推送 | SSE（非 WebSocket） | 单向推送，WebFlux 原生支持，实现简单 |
| 文件传输 | MinIO 预签名 URL | 大文件不经过 Spring Boot，节省内存与带宽 |
| 节点执行模型 | DAG 拓扑排序 + Ray remote | 支持节点间数据依赖，自然并行无依赖分支 |
| 图结构存储 | MongoDB（灵活 schema） | 节点/边 JSON 结构变化频繁，避免 MySQL 迁移 |
| 业务数据存储 | MySQL（R2DBC） | 用户、任务、流水线等强关系数据 |
| 认证 | JWT（无状态） | 适配 WebFlux 响应式链，不需要 session 存储 |

---

## 需补充到 compose.yaml 的服务

```yaml
  kafka:          # KRaft 模式（无 Zookeeper）
  minio:          # 对象存储
  ray-head:       # Ray cluster head（可选，开发阶段直接本地启动）
```

---

## 开发优先级（MVP 路径）

1. **Week 1-2**：后端基础（Auth + Pipeline CRUD + Task 提交）+ 数据库 Schema
2. **Week 2-3**：Python Worker（CSV + Filter + MinIO 读写）+ Kafka 打通
3. **Week 3-4**：前端画布（VueFlow + 节点面板 + CSV/Filter 节点）+ SSE 进度
4. **Week 4-5**：图片处理节点（Resize + OCR）
5. **Week 5-6**：视频处理节点（Frame Extract + Transcode）
6. **Week 6-7**：前端完善（数据预览 + 结果下载 + 任务历史）
7. **Week 7-8**：集成测试 + Docker Compose 全栈启动脚本
