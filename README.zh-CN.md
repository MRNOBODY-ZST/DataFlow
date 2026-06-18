<p align="center">
  <img src="frontend/public/DataFlow.svg" alt="DataFlow Logo" width="80" />
</p>

<h1 align="center">DataFlow</h1>

<p align="center">
  <strong>可视化拖拽数据流水线平台</strong>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> ·
  <a href="#功能特性">功能特性</a> ·
  <a href="#系统架构">系统架构</a> ·
  <a href="#开发指南">开发指南</a> ·
  <a href="LICENSE">许可证</a> ·
  <a href="README.md">English</a>
</p>

---

DataFlow 是一个全栈可视化数据流水线平台，通过在画布上拖拽和连接节点来构建、执行和监控数据处理工作流。支持结构化数据（CSV、JSON）、图像、视频和音频的批量处理，由分布式 Python Worker 集群驱动，提供实时任务进度追踪。

---

## 功能特性

### 可视化流程编辑器

- **拖拽画布** — 从节点面板拖拽节点至 VueFlow 画布，连线定义数据流向。
- **20+ 内置处理节点** — 涵盖读取、转换、媒体处理和写出等常见数据流水线场景。
- **实时节点配置** — 双击节点打开配置弹窗，支持每种节点类型的专属参数设置（文件路径、过滤条件、缩放尺寸等）。
- **自动保存与运行** — 保存流水线图并一键执行。

### 处理节点

| 分类 | 节点 |
|---|---|
| **读取** | CSV Reader, JSON Reader, MinIO Reader |
| **转换** | Filter, Map, Aggregate, JSON Transform, JSON Mapper |
| **图像** | Resize, OCR, Format Convert, Convolution, Edge Detect, Gaussian Blur, Pooling, Sharpen, Threshold |
| **视频/音频** | Frame Extract, Video Transcode, Audio Extract |
| **写出** | CSV Writer, MinIO Writer |
| **工具** | Preview |

### 任务监控

- **SSE 实时进度** — 通过 Server-Sent Events 实时追踪流水线执行进度，带有实时进度条。
- **任务历史与状态** — 查看所有已提交任务的状态（等待中 / 运行中 / 成功 / 失败）、耗时及错误详情。
- **仪表盘分析** — 基于 ECharts 的统计概览：任务运行历史、状态分布、存储用量、节点使用统计。

### 文件管理

- **MinIO 对象存储** — 通过预签名 URL 上传、浏览、下载和管理 MinIO 存储桶中的文件。
- **浏览器直传** — 文件通过预签名 PUT URL 直接上传至 MinIO，不经过后端，高效处理大文件。

### 其他

- **国际化 (i18n)** — 完整的中英文界面支持。
- **暗色模式** — 全页面跟随系统的暗色主题。
- **JWT 认证** — 基于无状态 JWT 的安全注册和登录。
- **响应式布局** — 移动端友好的侧边栏导航，HeadlessUI 过渡动画。
- **命令面板** — 键盘驱动的快速导航。
- **通知系统** — 应用内通知面板，推送任务状态更新。

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    前端 (Vue 3 + Vite)                       │
│  VueFlow 画布  │  仪表盘  │  任务监控  │  文件管理            │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP REST + SSE
┌───────────────────────────▼─────────────────────────────────┐
│              后端 (Spring Boot 4 + WebFlux)                   │
│  认证  │  流水线 CRUD  │  任务提交  │  文件预签名              │
│       MySQL (R2DBC)  │  MongoDB  │  Redis  │  MinIO          │
└──────┬──────────────────────────────────────┬───────────────┘
       │ Kafka                                │ MinIO SDK
       │  topic: task.dispatch                │
       │  topic: task.progress                │
┌──────▼──────────────────────────────────────▼───────────────┐
│               Python Worker (Ray 集群)                       │
│  Kafka 消费者 → DAG 执行器 → 节点注册表 (20+ 节点)            │
│  进度上报器 → Kafka → Redis Pub/Sub → SSE                    │
└─────────────────────────────────────────────────────────────┘
                            │
                    MinIO 对象存储
              (input / output / temp 存储桶)
```

### 技术栈

| 层 | 技术 |
|---|---|
| **前端** | Vue 3, TypeScript, Vite, VueFlow, Pinia, Tailwind CSS 4, HeadlessUI, Heroicons, ECharts, vue-i18n, Axios |
| **后端** | Spring Boot 4 (WebFlux), Java 25, R2DBC (MySQL), MongoDB Reactive, Redis Reactive, Spring Kafka, Spring Security, JWT (JJWT), MinIO SDK, MapStruct, Lombok |
| **Worker** | Python 3.12, Ray, kafka-python, MinIO SDK, Pandas, Pillow, OpenCV, EasyOCR, ffmpeg-python, JMESPath |
| **基础设施** | MySQL 9, MongoDB 8, Redis 8, Apache Kafka (Confluent 8), MinIO, Docker Compose |

---

## 项目结构

```
DataFlow/
├── backend/                    # Spring Boot 4 WebFlux API 服务
│   ├── src/main/java/com/hades/dataflow/
│   │   ├── config/             # Security、Kafka、MinIO、Redis 配置
│   │   ├── controller/         # REST 接口 (Auth, Pipeline, Task, File, Node)
│   │   ├── service/            # 业务逻辑
│   │   ├── kafka/              # Kafka 生产者与消费者
│   │   ├── security/           # JWT 过滤器与工具类
│   │   ├── repository/         # R2DBC (MySQL) 与 MongoDB 仓库
│   │   └── domain/             # 实体、文档、DTO
│   ├── src/main/resources/
│   │   ├── application.properties
│   │   └── schema.sql          # MySQL DDL
│   ├── compose.yaml            # Docker Compose (MySQL, MongoDB, Redis, Kafka, MinIO)
│   └── build.gradle            # Gradle 构建配置
│
├── frontend/                   # Vue 3 单页应用
│   └── src/
│       ├── views/              # 页面: 仪表盘、流程编辑器、流水线列表、
│       │                       #   任务监控、文件管理、设置、登录、注册
│       ├── components/
│       │   ├── flow/           # VueFlow 节点、边、配置面板、字段组件
│       │   ├── layout/         # AppLayout（侧边栏导航）
│       │   ├── task/           # 任务详情弹窗
│       │   └── ui/             # 命令面板、通知面板、弹窗
│       ├── stores/             # Pinia 状态管理 (auth, pipeline, task, file, notification, nodeSchema)
│       ├── api/                # Axios HTTP 客户端与接口模块
│       ├── i18n/               # 中英文翻译
│       └── router/             # Vue Router 路由与认证守卫
│
└── worker/                     # Python 分布式 Worker
    ├── dispatcher.py           # Kafka 消费者入口
    ├── executor.py             # Ray DAG 执行器（拓扑排序 → 并行执行）
    ├── reporter.py             # 进度上报器（Kafka → 后端 → SSE）
    ├── cli.py                  # Worker 进程管理 CLI
    ├── nodes/                  # 节点实现
    │   ├── base.py             # BaseNode 抽象基类与 NodeContext
    │   ├── readers/            # csv_reader, json_reader, minio_reader
    │   ├── transforms/         # filter, map, aggregate, json_transform, json_mapper
    │   ├── media/              # 图像 (resize, ocr, convolution, edge_detect, blur,
    │   │                       #   pooling, sharpen, threshold, format_convert)
    │   │                       # 视频 (extract, transcode), 音频 (extract)
    │   ├── writers/            # csv_writer, minio_writer
    │   └── utils/              # preview
    └── requirements.txt
```

---

## 快速开始

### 前置要求

- **Docker & Docker Compose** — 用于基础设施服务
- **Java 25+** — 用于 Spring Boot 后端
- **Node.js 20.19+ 或 22.12+** — 用于 Vue 前端
- **Python 3.12+** — 用于 Worker

### 1. 启动基础设施

```bash
cd backend
docker compose up -d
```

启动 MySQL、MongoDB、Redis、Kafka 和 MinIO。

### 2. 启动后端

```bash
cd backend
./gradlew bootRun
```

API 服务运行在 `http://localhost:8080`。

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

开发服务器运行在 `http://localhost:5173`。

### 4. 启动 Worker

```bash
cd worker
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python cli.py start
```

Worker 管理命令:

| 命令 | 说明 |
|---|---|
| `python cli.py start` | 启动 Worker 进程 |
| `python cli.py stop` | 停止 Worker 进程 |
| `python cli.py restart` | 重启 Worker 进程 |
| `python cli.py status` | 查看 Worker 状态 |
| `python cli.py logs` | 查看 Worker 日志 |
| `python cli.py logs -f` | 实时追踪 Worker 日志 |

Worker 将 PID 写入 `worker.pid`，日志写入 `worker.log`。

### 5. 访问应用

1. 在浏览器中打开 `http://localhost:5173`。
2. 注册一个新账户。
3. 在 **流水线** 页面创建流水线。
4. 将节点拖拽到画布上，连接节点，配置参数，点击 **运行**。
5. 在 **任务** 页面实时监控执行进度。

---

## API 接口

### 认证

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/auth/register` | 注册新用户 |
| `POST` | `/api/auth/login` | 登录获取 JWT |

### 流水线

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/pipelines` | 获取用户流水线列表 |
| `POST` | `/api/pipelines` | 创建流水线 |
| `GET` | `/api/pipelines/{id}` | 获取流水线详情（含节点图） |
| `PUT` | `/api/pipelines/{id}` | 更新流水线图 |
| `DELETE` | `/api/pipelines/{id}` | 删除流水线 |

### 任务

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/tasks` | 提交任务执行 |
| `GET` | `/api/tasks` | 获取任务列表（分页） |
| `GET` | `/api/tasks/{id}` | 获取任务详情 |
| `GET` | `/api/tasks/{id}/progress` | SSE 进度推送流 |

### 文件

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/files/presign-upload` | 获取预签名上传 URL |
| `GET` | `/api/files/presign-download` | 获取预签名下载 URL |

---

## 开发指南

### 前端脚本

```bash
npm run dev          # 启动开发服务器
npm run build        # 类型检查 & 生产构建
npm run type-check   # TypeScript 类型检查
npm run test:unit    # 运行单元测试 (Vitest)
npm run lint         # 代码检查 (OxLint + ESLint)
npm run format       # 代码格式化 (Prettier)
```

### 后端脚本

```bash
./gradlew bootRun    # 启动开发服务器（集成 Docker Compose）
./gradlew test       # 运行测试
./gradlew build      # 构建 JAR
```

### 默认端口

| 服务 | 端口 |
|---|---|
| 前端 (Vite) | 5173 |
| 后端 (Spring Boot) | 8080 |
| MySQL | 3306 |
| MongoDB | 27017 |
| Redis | 6379 |
| Kafka | 9092 |
| MinIO API | 9000 |
| MinIO 控制台 | 9001 |

### 默认凭据

| 服务 | 用户名 | 密码 |
|---|---|---|
| MySQL | `dataflow` | `dataflow123` |
| MongoDB | `dataflow` | `dataflow123` |
| MinIO | `dataflow` | `dataflow123` |

> **注意**: 以上为开发环境默认值，非本地部署时请务必修改。

---

## 工作原理

1. **设计** — 用户在 VueFlow 画布上拖拽节点并连线，构建 DAG（有向无环图）。
2. **保存** — 前端将节点/边图发送至后端，节点图存储在 MongoDB，流水线元数据存储在 MySQL。
3. **执行** — 用户点击"运行"后，后端创建任务记录，序列化流水线图并发布至 Kafka topic `task.dispatch`。
4. **处理** — Python Worker 消费消息，对 DAG 进行拓扑排序，通过 Ray 执行节点——自动并行化无依赖分支。
5. **上报** — 每个节点向 Kafka topic `task.progress` 上报进度。后端消费事件，更新 MySQL/Redis，并通过 SSE 推送至前端。
6. **结果** — 输出文件写入 MinIO，用户通过预签名 URL 下载结果。

---

## 许可证

[MIT](LICENSE) &copy; 2026 Hades
