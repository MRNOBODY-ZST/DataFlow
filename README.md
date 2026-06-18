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
- **47 built-in processing nodes** — Readers, transforms, media processing, spectral indices, and writers covering common data pipeline scenarios.
- **Real-time node configuration** — Double-click any node to open a configuration modal with type-specific settings (file paths, filter conditions, resize dimensions, etc.).
- **Auto-save & run** — Save pipeline graphs and execute them directly from the editor with one-click run.
- **Chinese error messages** — Every failure comes with a reason, possible cause, and suggested fix, all in Chinese — no Ray / rasterio / OpenCV English stack traces in the UI.

### Processing Nodes

| Category | Nodes | Count |
|---|---|---|
| **Readers** | CSV Reader, JSON Reader, MinIO Reader | 3 |
| **Transforms** | Filter, Map, Aggregate, JSON Transform, JSON Mapper | 5 |
| **Image** | Resize, OCR, Format Convert, Convolution, Edge Detect, Gaussian Blur, Pooling, Sharpen, Threshold | 9 |
| **Video / Audio** | Frame Extract, Video Transcode, Audio Extract | 3 |
| **Drone Spectral Indices** | NDVI, GNDVI, NDRE, SAVI, MSAVI, RVI, NGRDI, GCI, LCI, SIPI2, DVI, CI RedEdge, CIREdge, Generic Drone Index | 14 |
| **Sentinel‑2 Spectral Indices** | NDVI, GNDVI, NDRE, IRECI, SAVI, MSAVI2, OSAVI, LSWI, NDWI, MNDWI, NDMI, EVI, NDSI, NDTI, Generic S2 Index | 15 |
| **Writers** | CSV Writer, JSON Writer, MinIO Writer | 3 |
| **Utils** | Preview | 1 |

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
┌──────────────────────────────────────────────────────────────────┐
│                        Frontend (Vue 3 + Vite)                   │
│  VueFlow Canvas  │  Dashboard  │  Task Monitor  │  Files  │ Node │
└──────────────────────────────┬───────────────────────────────────┘
                                │ HTTP REST + SSE + direct upload to MinIO
┌───────────────────────────────▼───────────────────────────────────┐
│               Backend (Spring Boot 4 + WebFlux)                   │
│  Auth  │  Pipeline CRUD  │  Task Submit  │  File Presign  │ Node  │
│           MySQL (R2DBC)  │  MongoDB  │  Redis  │  MinIO            │
└──────┬──────────────────────────────────────┬───────────────────────┘
       │ Kafka                                │ MinIO SDK
       │  topic: task.dispatch                │  (read/write buckets)
       │  topic: task.progress                │
┌──────▼──────────────────────────────────────▼───────────────────────┐
│                Python Worker (Ray Cluster)                            │
│                                                                      │
│  dispatcher.py    Kafka consumer entry point (single process)         │
│       │                                                              │
│       ▼                                                              │
│  executor.py      DAG executor (topological sort + parallel branches)│
│       │                                                              │
│       ▼                                                              │
│  nodes/           47 nodes — NODE_REGISTRY (single source of truth)   │
│   ├── readers/      CSV, JSON, MinIO                                 │
│   ├── transforms/   filter, map, aggregate, json_transform,          │
│   │                  json_mapper                                      │
│   ├── media/        image (9) + video (extract, transcode) + audio    │
│   ├── S2Indices/   Sentinel‑2 spectral indices (14 + generic)         │
│   ├── droneIndices/  Drone spectral indices (13 + generic)           │
│   ├── writers/      csv, json, minio                                 │
│   ├── utils/        preview                                          │
│   ├── base.py       BaseNode ABC + NodeContext (config / minio)      │
│   └── _input_utils.py  Unified validation + Chinese error template   │
│                        (reason + possible cause + suggested fix)     │
│                                                                      │
│  reporter.py       Progress reporting (Ray → Kafka → Redis Pub/Sub → │
│                    SSE)                                              │
│  schema_export.py  Generates node_schemas.json consumed by backend   │
└──────────────────────────────────────────────────────────────────────┘
                                │
                        MinIO Object Storage
           (dataflow-input / dataflow-output / dataflow-temp)
```

### How an Error Reaches the UI

```
User drags a PNG into the Sentinel‑2 NDVI node
  └ nodes/S2Indices/_s2_base.py  detects only 1 physical band
      raise RuntimeError(
          "Sentinel-2 NDVI: No Sentinel-2 bands detected in the image."
          "\nPossible cause: you uploaded a JPEG/PNG instead of a"
          " multispectral TIFF."
          "\nFix: upload a Sentinel-2 TIFF with B2/B3/B4/B8/B11… bands."
      )
  └ executor.py::_friendly()     RuntimeErrors pass through unchanged
  └ executor.py::run_pipeline()  wraps as "node xxx failed: ..."
  └ _extract_friendly_from_ray_error()   extracts body from RayTaskError
  └ Kafka → Backend → Redis Pub/Sub → SSE → Frontend
  └ TaskDetailModal.vue          whitespace-pre-line preserves newlines
      UI shows three lines: reason + possible cause + suggested fix
```

### Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vue 3, TypeScript, Vite, VueFlow, Pinia, Tailwind CSS 4, HeadlessUI, Heroicons, ECharts, vue-i18n, Axios |
| **Backend** | Spring Boot 4 (WebFlux), Java 25, R2DBC (MySQL), MongoDB Reactive, Redis Reactive, Spring Kafka, Spring Security, JWT (JJWT), MinIO SDK, MapStruct, Lombok |
| **Worker** | Python 3.12, Ray, kafka-python, MinIO SDK, Pandas, Pillow, OpenCV, EasyOCR, ffmpeg-python, JMESPath, rasterio |
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
    ├── executor.py             # Ray DAG executor (topological sort → parallel branches, friendly errors)
    ├── reporter.py             # Progress reporter (Kafka → backend → SSE)
    ├── cli.py                  # Worker process management CLI
    ├── schema_export.py        # Generates node_schemas.json from NODE_REGISTRY
    ├── node_schemas.json      # Backend NodeSchemaService reads this first (generated)
    ├── nodes/                  # 47 nodes — NODE_REGISTRY (single source of truth)
    │   ├── __init__.py         # NODE_REGISTRY dict
    │   ├── base.py             # BaseNode ABC + NodeContext (config / minio)
    │   ├── _input_utils.py     # Unified validation + Chinese error template
    │   │                        #   20+ err_* helpers (reason + cause + fix)
    │   ├── readers/            # csv_reader, json_reader, minio_reader
    │   ├── transforms/         # filter, map, aggregate, json_transform, json_mapper
    │   ├── media/              # image (9) + video (extract, transcode) + audio (extract)
    │   ├── S2Indices/          # Sentinel‑2 spectral indices (14 + generic)
    │   ├── droneIndices/        # Drone spectral indices (13 + generic)
    │   ├── writers/            # csv_writer, json_writer, minio_writer
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
