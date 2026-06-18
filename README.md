<p align="center">
  <img src="frontend/public/DataFlow.svg" alt="DataFlow Logo" width="80" />
</p>

<h1 align="center">DataFlow</h1>

<p align="center">
  <strong>Visual Drag-and-Drop Data Pipeline Platform</strong>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#features">Features</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#development">Development</a> ·
  <a href="LICENSE">License</a> ·
  <a href="README.zh-CN.md">中文文档</a>
</p>

---

DataFlow is a full-stack visual data pipeline platform that lets you build, execute, and monitor data processing workflows by dragging and connecting nodes on a canvas. It supports structured data (CSV, JSON), images, video, and audio — powered by a distributed Python worker cluster with real-time progress tracking.

---

## Features

### Visual Flow Editor

- **Drag-and-drop canvas** — Build pipelines by dragging nodes from the panel onto a VueFlow-powered canvas, connecting them with edges to define data flow.
- **20+ built-in processing nodes** — Readers, transforms, media processing, and writers covering common data pipeline scenarios.
- **Real-time node configuration** — Double-click any node to open a configuration modal with type-specific settings (file paths, filter conditions, resize dimensions, etc.).
- **Auto-save & run** — Save pipeline graphs and execute them directly from the editor with one-click run.

### Processing Nodes

| Category | Nodes |
|---|---|
| **Readers** | CSV Reader, JSON Reader, MinIO Reader |
| **Transforms** | Filter, Map, Aggregate, JSON Transform, JSON Mapper |
| **Image** | Resize, OCR, Format Convert, Convolution, Edge Detect, Gaussian Blur, Pooling, Sharpen, Threshold |
| **Video/Audio** | Frame Extract, Video Transcode, Audio Extract |
| **Writers** | CSV Writer, MinIO Writer |
| **Utils** | Preview |

### Task Monitoring

- **Real-time SSE progress** — Track pipeline execution progress via Server-Sent Events with live progress bars.
- **Task history & status** — View all submitted tasks with status (Pending / Running / Success / Failed), timing, and error details.
- **Dashboard analytics** — Overview dashboard with ECharts-powered statistics: task run history, status distribution, storage usage, and node usage breakdown.

### File Management

- **MinIO-backed object storage** — Upload, browse, download, and manage files in MinIO buckets via presigned URLs.
- **Direct browser upload** — Files upload directly to MinIO through presigned PUT URLs, bypassing the backend to handle large files efficiently.

### Other

- **Internationalization (i18n)** — Full Chinese and English UI support.
- **Dark mode** — System-aware dark theme across all pages.
- **JWT authentication** — Secure user registration and login with stateless JWT tokens.
- **Responsive layout** — Mobile-friendly sidebar navigation with HeadlessUI transitions.
- **Command palette** — Quick keyboard-driven navigation.
- **Notification system** — In-app notification panel for task updates.

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

### Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vue 3, TypeScript, Vite, VueFlow, Pinia, Tailwind CSS 4, HeadlessUI, Heroicons, ECharts, vue-i18n, Axios |
| **Backend** | Spring Boot 4 (WebFlux), Java 25, R2DBC (MySQL), MongoDB Reactive, Redis Reactive, Spring Kafka, Spring Security, JWT (JJWT), MinIO SDK, MapStruct, Lombok |
| **Worker** | Python 3.12, Ray, kafka-python, MinIO SDK, Pandas, Pillow, OpenCV, EasyOCR, ffmpeg-python, JMESPath |
| **Infrastructure** | MySQL 9, MongoDB 8, Redis 8, Apache Kafka (Confluent 8), MinIO, Docker Compose |

---

## Project Structure

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

### Prerequisites

- **Docker & Docker Compose** — for infrastructure services
- **Java 25+** — for the Spring Boot backend
- **Node.js 20.19+ or 22.12+** — for the Vue frontend
- **Python 3.12+** — for the worker

### 1. Start Infrastructure

```bash
cd backend
docker compose up -d
```

This starts MySQL, MongoDB, Redis, Kafka, and MinIO.

### 2. Start Backend

```bash
cd backend
./gradlew bootRun
```

The API server starts at `http://localhost:8080`.

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server starts at `http://localhost:5173`.

### 4. Start Worker

```bash
cd worker
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python cli.py start
```

Worker management commands:

| Command | Description |
|---|---|
| `python cli.py start` | Start the worker process |
| `python cli.py stop` | Stop the worker process |
| `python cli.py restart` | Restart the worker process |
| `python cli.py status` | Check worker status |
| `python cli.py logs` | View worker logs |
| `python cli.py logs -f` | Follow worker logs in real-time |

The worker writes its PID to `worker.pid` and logs to `worker.log`.

### 5. Access the Application

1. Open `http://localhost:5173` in your browser.
2. Register a new account.
3. Create a pipeline from the **Pipeline** page.
4. Drag nodes onto the canvas, connect them, configure each node, and click **Run**.
5. Monitor progress in real-time from the **Tasks** page.

---

## API Endpoints

### Authentication

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login and receive JWT |

### Pipelines

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/pipelines` | List user's pipelines |
| `POST` | `/api/pipelines` | Create a pipeline |
| `GET` | `/api/pipelines/{id}` | Get pipeline with graph |
| `PUT` | `/api/pipelines/{id}` | Update pipeline graph |
| `DELETE` | `/api/pipelines/{id}` | Delete a pipeline |

### Tasks

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/tasks` | Submit a task for execution |
| `GET` | `/api/tasks` | List tasks (paginated) |
| `GET` | `/api/tasks/{id}` | Get task details |
| `GET` | `/api/tasks/{id}/progress` | SSE progress stream |

### Files

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/files/presign-upload` | Get presigned upload URL |
| `GET` | `/api/files/presign-download` | Get presigned download URL |

---

## Development

### Frontend Scripts

```bash
npm run dev          # Start dev server
npm run build        # Type-check & build for production
npm run type-check   # TypeScript type checking
npm run test:unit    # Run unit tests (Vitest)
npm run lint         # Lint with OxLint + ESLint
npm run format       # Format with Prettier
```

### Backend Scripts

```bash
./gradlew bootRun    # Start dev server with Docker Compose integration
./gradlew test       # Run tests
./gradlew build      # Build JAR
```

### Default Ports

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

### Default Credentials

| Service | Username | Password |
|---|---|---|
| MySQL | `dataflow` | `dataflow123` |
| MongoDB | `dataflow` | `dataflow123` |
| MinIO | `dataflow` | `dataflow123` |

> **Note**: These are development defaults. Change them for any non-local deployment.

---

## How It Works

1. **Design** — User drags nodes onto the VueFlow canvas and connects them to form a DAG (Directed Acyclic Graph).
2. **Save** — The frontend sends the node/edge graph to the backend, which stores it in MongoDB while pipeline metadata goes to MySQL.
3. **Execute** — When the user clicks "Run", the backend creates a Task record, serializes the pipeline graph, and publishes it to Kafka topic `task.dispatch`.
4. **Process** — The Python worker consumes the message, performs topological sort on the DAG, and executes nodes via Ray — parallelizing independent branches automatically.
5. **Report** — Each node reports progress to Kafka topic `task.progress`. The backend consumes these events, updates MySQL/Redis, and pushes them to the frontend via SSE.
6. **Result** — Output files are written to MinIO. The user can download results via presigned URLs.

---

## License

[MIT](LICENSE) &copy; 2026 Hades
