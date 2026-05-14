<p align="center">
  <img src="frontend/public/DataFlow.svg" alt="DataFlow Logo" width="80" />
</p>

<h1 align="center">DataFlow</h1>

<p align="center">
  <strong>Visual Drag-and-Drop Data Pipeline Platform</strong><br>
  <strong>可视化拖拽数据流水线平台</strong>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#features">Features</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#development">Development</a> ·
  <a href="LICENSE">License</a>
</p>

---

DataFlow is a full-stack visual data pipeline platform that lets you build, execute, and monitor data processing workflows by dragging and connecting nodes on a canvas. It supports structured data (CSV, JSON), images, video, and audio — powered by a distributed Python worker cluster with real-time progress tracking.

DataFlow 是一个全栈可视化数据流水线平台，通过在画布上拖拽和连接节点来构建、执行和监控数据处理工作流。支持结构化数据（CSV、JSON）、图像、视频和音频的批量处理，由分布式 Python Worker 集群驱动，提供实时任务进度追踪。

---

## Features

### Visual Flow Editor / 可视化流程编辑器

- **Drag-and-drop canvas** — Build pipelines by dragging nodes from the panel onto a VueFlow-powered canvas, connecting them with edges to define data flow.
- **20+ built-in processing nodes** — Readers, transforms, media processing, and writers covering common data pipeline scenarios.
- **Real-time node configuration** — Double-click any node to open a configuration modal with type-specific settings (file paths, filter conditions, resize dimensions, etc.).
- **Auto-save & run** — Save pipeline graphs and execute them directly from the editor with one-click run.

- **拖拽画布** — 从节点面板拖拽节点至 VueFlow 画布，连线定义数据流向。
- **20+ 内置处理节点** — 涵盖读取、转换、媒体处理和写出等常见数据流水线场景。
- **实时节点配置** — 双击节点打开配置弹窗，支持每种节点类型的专属参数设置。
- **自动保存与运行** — 保存流水线图并一键执行。

### Processing Nodes / 处理节点

| Category 分类 | Nodes 节点 |
|---|---|
| **Readers 读取** | CSV Reader, JSON Reader, MinIO Reader |
| **Transforms 转换** | Filter, Map, Aggregate, JSON Transform, JSON Mapper |
| **Image 图像** | Resize, OCR, Format Convert, Convolution, Edge Detect, Gaussian Blur, Pooling, Sharpen, Threshold |
| **Video/Audio 视频/音频** | Frame Extract, Video Transcode, Audio Extract |
| **Writers 写出** | CSV Writer, MinIO Writer |
| **Utils 工具** | Preview |

### Task Monitoring / 任务监控

- **Real-time SSE progress** — Track pipeline execution progress via Server-Sent Events with live progress bars.
- **Task history & status** — View all submitted tasks with status (Pending / Running / Success / Failed), timing, and error details.
- **Dashboard analytics** — Overview dashboard with ECharts-powered statistics: task run history, status distribution, storage usage, and node usage breakdown.

- **SSE 实时进度** — 通过 Server-Sent Events 实时追踪流水线执行进度。
- **任务历史与状态** — 查看所有已提交任务的状态、耗时及错误详情。
- **仪表盘分析** — 基于 ECharts 的统计概览：任务运行历史、状态分布、存储用量、节点使用统计。

### File Management / 文件管理

- **MinIO-backed object storage** — Upload, browse, download, and manage files in MinIO buckets via presigned URLs.
- **Direct browser upload** — Files upload directly to MinIO through presigned PUT URLs, bypassing the backend to handle large files efficiently.

- **MinIO 对象存储** — 通过预签名 URL 上传、浏览、下载和管理 MinIO 存储桶中的文件。
- **浏览器直传** — 文件通过预签名 PUT URL 直接上传至 MinIO，不经过后端，高效处理大文件。

### Other / 其他

- **Internationalization (i18n)** — Full Chinese and English UI support.
- **Dark mode** — System-aware dark theme across all pages.
- **JWT authentication** — Secure user registration and login with stateless JWT tokens.
- **Responsive layout** — Mobile-friendly sidebar navigation with HeadlessUI transitions.
- **Command palette** — Quick keyboard-driven navigation.
- **Notification system** — In-app notification panel for task updates.

- **国际化 (i18n)** — 完整的中英文界面支持。
- **暗色模式** — 全页面跟随系统的暗色主题。
- **JWT 认证** — 基于无状态 JWT 的安全注册和登录。
- **响应式布局** — 移动端友好的侧边栏导航。
- **命令面板** — 键盘驱动的快速导航。
- **通知系统** — 应用内通知面板，推送任务状态更新。

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Vue 3 + Vite)                 │
│  VueFlow Canvas  │  Dashboard  │  Task Monitor  │  Files    │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP REST + SSE
┌───────────────────────────▼─────────────────────────────────┐
│               Backend (Spring Boot 4 + WebFlux)             │
│  Auth  │  Pipeline CRUD  │  Task Submit  │  File Presign    │
│        MySQL (R2DBC)  │  MongoDB  │  Redis  │  MinIO        │
└──────┬──────────────────────────────────────┬───────────────┘
       │ Kafka                                │ MinIO SDK
       │  topic: task.dispatch                │
       │  topic: task.progress                │
┌──────▼──────────────────────────────────────▼───────────────┐
│                Python Worker (Ray Cluster)                   │
│  Kafka Consumer → DAG Executor → Node Registry (20+ nodes)  │
│  Progress Reporter → Kafka → Redis Pub/Sub → SSE            │
└─────────────────────────────────────────────────────────────┘
                            │
                   MinIO Object Storage
              (input / output / temp buckets)
```

### Tech Stack / 技术栈

| Layer 层 | Technology 技术 |
|---|---|
| **Frontend** | Vue 3, TypeScript, Vite, VueFlow, Pinia, Tailwind CSS 4, HeadlessUI, Heroicons, ECharts, vue-i18n, Axios |
| **Backend** | Spring Boot 4 (WebFlux), Java 25, R2DBC (MySQL), MongoDB Reactive, Redis Reactive, Spring Kafka, Spring Security, JWT (JJWT), MinIO SDK, MapStruct, Lombok |
| **Worker** | Python 3.12, Ray, kafka-python, MinIO SDK, Pandas, Pillow, OpenCV, EasyOCR, ffmpeg-python, JMESPath |
| **Infrastructure** | MySQL 9, MongoDB 8, Redis 8, Apache Kafka (Confluent 8), MinIO, Docker Compose |

---

## Project Structure / 项目结构

```
DataFlow/
├── backend/                    # Spring Boot 4 WebFlux API server
│   ├── src/main/java/com/hades/dataflow/
│   │   ├── config/             # Security, Kafka, MinIO, Redis configs
│   │   ├── controller/         # REST endpoints (Auth, Pipeline, Task, File, Node)
│   │   ├── service/            # Business logic
│   │   ├── kafka/              # Kafka producer & consumer
│   │   ├── security/           # JWT filter & utility
│   │   ├── repository/         # R2DBC (MySQL) & MongoDB repositories
│   │   └── domain/             # Entities, documents, DTOs
│   ├── src/main/resources/
│   │   ├── application.properties
│   │   └── schema.sql          # MySQL DDL
│   ├── compose.yaml            # Docker Compose (MySQL, MongoDB, Redis, Kafka, MinIO)
│   └── build.gradle            # Gradle build with all dependencies
│
├── frontend/                   # Vue 3 SPA
│   └── src/
│       ├── views/              # Pages: Dashboard, FlowEditor, PipelineList,
│       │                       #   TaskMonitor, FileManager, Settings, Login, Register
│       ├── components/
│       │   ├── flow/           # VueFlow nodes, edges, config panels, fields
│       │   ├── layout/         # AppLayout (sidebar navigation)
│       │   ├── task/           # Task detail modal
│       │   └── ui/             # CommandPalette, NotificationPanel, modals
│       ├── stores/             # Pinia stores (auth, pipeline, task, file, notification, nodeSchema)
│       ├── api/                # Axios HTTP client & endpoint modules
│       ├── i18n/               # English & Chinese translations
│       └── router/             # Vue Router with auth guards
│
└── worker/                     # Python distributed worker
    ├── dispatcher.py           # Kafka consumer entry point
    ├── executor.py             # Ray DAG executor (topological sort → parallel execution)
    ├── reporter.py             # Progress reporter (Kafka → backend → SSE)
    ├── cli.py                  # Worker process management CLI
    ├── nodes/                  # Node implementations
    │   ├── base.py             # BaseNode ABC & NodeContext
    │   ├── readers/            # csv_reader, json_reader, minio_reader
    │   ├── transforms/         # filter, map, aggregate, json_transform, json_mapper
    │   ├── media/              # image (resize, ocr, convolution, edge_detect, blur,
    │   │                       #   pooling, sharpen, threshold, format_convert)
    │   │                       # video (extract, transcode), audio (extract)
    │   ├── writers/            # csv_writer, minio_writer
    │   └── utils/              # preview
    └── requirements.txt
```

---

## Quick Start

### Prerequisites / 前置要求

- **Docker & Docker Compose** — for infrastructure services
- **Java 25+** — for the Spring Boot backend
- **Node.js 20.19+ or 22.12+** — for the Vue frontend
- **Python 3.12+** — for the worker

### 1. Start Infrastructure / 启动基础设施

```bash
cd backend
docker compose up -d
```

This starts MySQL, MongoDB, Redis, Kafka, and MinIO.

启动 MySQL、MongoDB、Redis、Kafka 和 MinIO。

### 2. Start Backend / 启动后端

```bash
cd backend
./gradlew bootRun
```

The API server starts at `http://localhost:8080`.

API 服务运行在 `http://localhost:8080`。

### 3. Start Frontend / 启动前端

```bash
cd frontend
npm install
npm run dev
```

The dev server starts at `http://localhost:5173`.

开发服务器运行在 `http://localhost:5173`。

### 4. Start Worker / 启动 Worker

```bash
cd worker
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python cli.py start
```

Worker management commands / Worker 管理命令:

| Command | Description |
|---|---|
| `python cli.py start` | Start the worker process |
| `python cli.py stop` | Stop the worker process |
| `python cli.py restart` | Restart the worker process |
| `python cli.py status` | Check worker status |
| `python cli.py logs` | View worker logs |
| `python cli.py logs -f` | Follow worker logs in real-time |

The worker writes its PID to `worker.pid` and logs to `worker.log`.

### 5. Access the Application / 访问应用

1. Open `http://localhost:5173` in your browser.
2. Register a new account.
3. Create a pipeline from the **Pipeline** page.
4. Drag nodes onto the canvas, connect them, configure each node, and click **Run**.
5. Monitor progress in real-time from the **Tasks** page.

---

## API Endpoints / API 接口

### Authentication / 认证

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register a new user / 注册新用户 |
| `POST` | `/api/auth/login` | Login and receive JWT / 登录获取 JWT |

### Pipelines / 流水线

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/pipelines` | List user's pipelines / 获取用户流水线列表 |
| `POST` | `/api/pipelines` | Create a pipeline / 创建流水线 |
| `GET` | `/api/pipelines/{id}` | Get pipeline with graph / 获取流水线详情 |
| `PUT` | `/api/pipelines/{id}` | Update pipeline graph / 更新流水线图 |
| `DELETE` | `/api/pipelines/{id}` | Delete a pipeline / 删除流水线 |

### Tasks / 任务

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/tasks` | Submit a task for execution / 提交任务执行 |
| `GET` | `/api/tasks` | List tasks (paginated) / 获取任务列表 |
| `GET` | `/api/tasks/{id}` | Get task details / 获取任务详情 |
| `GET` | `/api/tasks/{id}/progress` | SSE progress stream / SSE 进度推送 |

### Files / 文件

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/files/presign-upload` | Get presigned upload URL / 获取预签名上传 URL |
| `GET` | `/api/files/presign-download` | Get presigned download URL / 获取预签名下载 URL |

---

## Development / 开发

### Frontend Scripts / 前端脚本

```bash
npm run dev          # Start dev server / 启动开发服务器
npm run build        # Type-check & build for production / 类型检查 & 生产构建
npm run type-check   # TypeScript type checking / TypeScript 类型检查
npm run test:unit    # Run unit tests (Vitest) / 运行单元测试
npm run lint         # Lint with OxLint + ESLint / 代码检查
npm run format       # Format with Prettier / 代码格式化
```

### Backend Scripts / 后端脚本

```bash
./gradlew bootRun    # Start dev server with Docker Compose integration / 启动开发服务器
./gradlew test       # Run tests / 运行测试
./gradlew build      # Build JAR / 构建 JAR
```

### Default Ports / 默认端口

| Service | Port |
|---|---|
| Frontend (Vite) | 5173 |
| Backend (Spring Boot) | 8080 |
| MySQL | 3306 |
| MongoDB | 27017 |
| Redis | 6379 |
| Kafka | 9092 |
| MinIO API | 9000 |
| MinIO Console | 9001 |

### Default Credentials / 默认凭据

| Service | Username | Password |
|---|---|---|
| MySQL | `dataflow` | `dataflow123` |
| MongoDB | `dataflow` | `dataflow123` |
| MinIO | `dataflow` | `dataflow123` |

> **Note**: These are development defaults. Change them for any non-local deployment.
>
> **注意**: 以上为开发环境默认值，非本地部署时请务必修改。

---

## How It Works / 工作原理

1. **Design** — User drags nodes onto the VueFlow canvas and connects them to form a DAG (Directed Acyclic Graph).
2. **Save** — The frontend sends the node/edge graph to the backend, which stores it in MongoDB while pipeline metadata goes to MySQL.
3. **Execute** — When the user clicks "Run", the backend creates a Task record, serializes the pipeline graph, and publishes it to Kafka topic `task.dispatch`.
4. **Process** — The Python worker consumes the message, performs topological sort on the DAG, and executes nodes via Ray — parallelizing independent branches automatically.
5. **Report** — Each node reports progress to Kafka topic `task.progress`. The backend consumes these events, updates MySQL/Redis, and pushes them to the frontend via SSE.
6. **Result** — Output files are written to MinIO. The user can download results via presigned URLs.

---

1. **设计** — 用户在 VueFlow 画布上拖拽节点并连线，构建 DAG（有向无环图）。
2. **保存** — 前端将节点/边图发送至后端，节点图存储在 MongoDB，流水线元数据存储在 MySQL。
3. **执行** — 用户点击"运行"后，后端创建任务记录，序列化流水线图并发布至 Kafka topic `task.dispatch`。
4. **处理** — Python Worker 消费消息，对 DAG 进行拓扑排序，通过 Ray 执行节点——自动并行化无依赖分支。
5. **上报** — 每个节点向 Kafka topic `task.progress` 上报进度。后端消费事件，更新 MySQL/Redis，并通过 SSE 推送至前端。
6. **结果** — 输出文件写入 MinIO，用户通过预签名 URL 下载结果。

---

## License

[MIT](LICENSE) &copy; 2026 Hades
