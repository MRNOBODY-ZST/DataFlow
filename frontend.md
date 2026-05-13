# Context

这次改动要同时解决 3 件事：

1. 流程图编辑器现在几乎不能用连线，核心原因是前端已经维护了 `edges`，但 `frontend/src/views/FlowEditor.vue` 没有处理 Vue Flow 的 connect 事件，拖线后不会把新边写回状态。
2. 运行前全局选择输入文件的模型和当前节点配置体系冲突。节点配置面板 `frontend/src/components/flow/NodeConfig.vue` 已经有 schema-driven 的 `file-picker`，但 `csv_reader` / `json_reader` 仍被 UI 特判成“运行时自动注入”，而后端/worker 又通过顶层 `inputKey` + `input_key` fallback 驱动执行。这正是“文件应在节点中配置而不是运行前配置”的反人类来源。
3. JSON 流水线目前大量依赖手输表达式或 JSON 字符串。现有架构其实已经具备可复用基础：后端通过 `backend/src/main/java/com/hades/dataflow/service/NodeSchemaService.java` 暴露节点 schema，前端通过 `frontend/src/components/flow/NodeConfig.vue` 统一渲染配置表单。因此推荐在现有 schema-driven 体系上扩展专用可视化控件，而不是再造一套单独配置系统。

用户已确认本次产品范围：
- 运行入口改为“仅保留运行”，不再在运行弹窗里选文件。
- JMESPath 可视化首版做“路径构建器”：支持字段路径选择、数组 `[*]` 投影、最终字段提取，并保留手动表达式兜底。

# Recommended approach

## 1. 修复流程图无法连线

### 目标
让节点拖线后立即创建边，并且保存/刷新后仍然存在。

### 修改点
- `frontend/src/views/FlowEditor.vue`
  - 给 `<VueFlow>` 增加 connect 事件处理。
  - 在现有 `edges` 状态上使用 Vue Flow 标准方式追加新边，而不是只依赖 `v-model:edges`。
  - 保持现有 `pipelineStore.saveGraph()` 存储路径不变，复用 `frontend/src/stores/pipeline.ts` 的保存逻辑。

### 复用点
- 复用 `useVueFlow()` 和当前 `nodes` / `edges` 本地状态。
- 复用已有的保存接口，不改 graph 持久化结构。

## 2. 把文件选择完全收回到节点配置里

### 目标
运行弹窗只负责“保存并提交任务”；所有输入文件都在节点内部选好。

### 修改点
- `frontend/src/components/flow/NodeConfig.vue`
  - 移除 `csv_reader` / `json_reader` 对 `key` 字段的“运行时自动填充”文案和隐藏逻辑。
  - `file-picker` 一律作为真实可编辑字段展示。
  - 继续复用 `frontend/src/components/ui/FilePickerModal.vue`，避免新增独立文件选择器。
- `backend/src/main/java/com/hades/dataflow/service/NodeSchemaService.java`
  - 将 `csv_reader` / `json_reader` 的 `key` 字段改为普通节点配置字段，不再依赖 `autoFilled=true`。
  - 为“可以在没有上游输入时直接从 MinIO 取文件”的媒体节点补充可选 `key` 字段，使它们在作为源节点时也能在节点内指定输入文件。优先覆盖：
    - `image_resize`
    - `image_ocr`
    - `image_format_convert`
    - `video_extract`
    - `video_transcode`
    - `audio_extract`
- `frontend/src/views/FlowEditor.vue`
  - 将运行弹窗简化为提交确认入口，不再提供“选择已上传文件 / 上传新文件”。
  - 在提交前增加图级校验：凡是没有上游输入、且执行时需要直接读取对象的节点，必须已经配置 `key`。

### 为什么媒体节点也要纳入
worker 中这类节点已经支持 `ctx.config["key"] or ctx.config["input_key"]` 的读取模式。既然本次要删除全局 `inputKey`，就必须把仍依赖该 fallback 的源节点一起收口到节点配置，否则一批媒体节点会在“没有上游时”直接失效。

## 3. 删除全局 `inputKey` 提交/执行链路

### 目标
任务提交只传 `pipelineId`；执行阶段完全依赖 graph 中各节点持久化的 `node.data`。

### 修改点
前端：
- `frontend/src/api/task.ts`
- `frontend/src/stores/task.ts`
- `frontend/src/views/FlowEditor.vue`

后端：
- `backend/src/main/java/com/hades/dataflow/domain/dto/TaskSubmitRequest.java`
- `backend/src/main/java/com/hades/dataflow/service/TaskService.java`
- `backend/src/main/java/com/hades/dataflow/kafka/TaskProducer.java`

worker：
- `worker/dispatcher.py`
- `worker/executor.py`

### 实现原则
- `TaskSubmitRequest` 去掉 `inputKey`。
- Kafka dispatch payload 去掉 `inputKey`。
- `worker/executor.py` 删除“对无上游节点自动注入 `input_key`”的逻辑。
- 节点运行时统一读取自身配置里的 `key`；上游有输出时仍优先消费上游 `inputs`，不改变现有 DAG 语义。

### 任务详情最小兼容策略
- 保留数据库中的 `inputPath` 字段，但不再把它当作全局输入来源。
- `TaskService` 可以先将其置空/null；前端任务详情页改为在缺省时显示“由节点配置提供输入”。
- 需要同步调整：
  - `backend/src/main/java/com/hades/dataflow/domain/dto/TaskResponse.java`
  - `backend/src/main/java/com/hades/dataflow/domain/entity/Task.java`
  - `frontend/src/api/task.ts`
  - `frontend/src/views/TaskDetail.vue`

这样可以避免在本次改动里再引入“多个源节点输入如何汇总成 task-level 字符串”的额外产品设计。

## 4. 在现有 schema-driven 体系上增加可视化配置控件

### 目标
不新建第二套配置系统；直接让 `NodeConfig.vue` 基于 schema 渲染更友好的控件，逐步覆盖“手输 JSON / 手输表达式”的场景。

### 第一批可视化控件（本次建议一起做）

#### 4.1 JMESPath 路径构建器
- 目标字段：`json_transform.expression`
- 修改点：
  - `backend/src/main/java/com/hades/dataflow/domain/dto/NodeSchemaDTO.java`
  - `backend/src/main/java/com/hades/dataflow/service/NodeSchemaService.java`
  - `frontend/src/stores/nodeSchema.ts`
  - `frontend/src/components/flow/NodeConfig.vue`
  - 新增一个前端字段组件（例如放在 `frontend/src/components/flow/fields/` 下）
- 方案：
  - schema 为 `expression` 增加专用 widget 元数据。
  - builder 只负责生成最终字符串，真实持久化值仍是普通 JMESPath 表达式。
  - 首版能力限制为：
    - 根路径/字段逐级选择
    - 数组 `[*]` 投影
    - 最终字段提取
    - 手动编辑文本兜底
- 本次不做后端 preview/introspection API，保持首版范围可控。

#### 4.2 字符串数组编辑器
- 目标字段：
  - `map.select`
  - `aggregate.group_by`
  - `image_ocr.lang`
- 方案：把当前文本框里要求手写 JSON 数组的方式改成“可增删的字符串列表”。
- 收益：覆盖一批最常见的“需要手写 JSON 数组”的反人类配置。

#### 4.3 键值映射编辑器
- 目标字段：
  - `map.rename`
  - `aggregate.agg`
- 方案：
  - `map.rename` 使用“原字段 -> 新字段”的键值对列表。
  - `aggregate.agg` 使用“字段 -> 聚合函数”的键值对/行编辑器；聚合函数首版限制在常见枚举（如 `sum` / `avg` / `min` / `max` / `count`）。
- 收益：让“字段映射”“聚合规则”都变成真正的表单，而不是 JSON 文本。

### 为什么建议把这两类结构化编辑器一起做
worker 侧的 `map_node.py` / `aggregate_node.py` 期望拿到的本来就是 `list` / `dict`，而不是字符串。把这些字段从文本输入改成结构化编辑器，不仅改善体验，也能让前端直接保存正确类型的节点配置，减少数据类型不一致的风险。

## 5. 节点卡片摘要与运行前校验

### 节点摘要
- `frontend/src/components/flow/nodes/GenericFlowNode.vue`
  - 扩展摘要优先级，让节点卡片能显示更有意义的配置预览，例如：
    - 文件 `key`
    - JMESPath `expression`
    - 列表/映射的简短摘要

### 运行前校验
- `frontend/src/views/FlowEditor.vue`
  - 在提交任务前校验：
    - 没有上游的 reader / source-capable media 节点必须配置文件 `key`
    - schema 中 `required=true` 的字段不能为空
  - 校验失败时直接在运行入口给出明确报错，而不是提交到 worker 后才失败。

### 旧图兼容策略
旧流水线如果原先依赖运行时输入文件、现在节点里没有 `key`，本次不会做自动迁移；应在前端用清晰校验阻止运行，并提示用户到对应节点补全输入文件。

# Critical files

前端核心：
- `frontend/src/views/FlowEditor.vue`
- `frontend/src/components/flow/NodeConfig.vue`
- `frontend/src/components/flow/nodes/GenericFlowNode.vue`
- `frontend/src/components/ui/FilePickerModal.vue`
- `frontend/src/stores/nodeSchema.ts`
- `frontend/src/api/task.ts`
- `frontend/src/stores/task.ts`
- `frontend/src/views/TaskDetail.vue`

后端核心：
- `backend/src/main/java/com/hades/dataflow/domain/dto/NodeSchemaDTO.java`
- `backend/src/main/java/com/hades/dataflow/service/NodeSchemaService.java`
- `backend/src/main/java/com/hades/dataflow/controller/NodeController.java`
- `backend/src/main/java/com/hades/dataflow/domain/dto/TaskSubmitRequest.java`
- `backend/src/main/java/com/hades/dataflow/domain/dto/TaskResponse.java`
- `backend/src/main/java/com/hades/dataflow/domain/entity/Task.java`
- `backend/src/main/java/com/hades/dataflow/service/TaskService.java`
- `backend/src/main/java/com/hades/dataflow/kafka/TaskProducer.java`

worker 核心：
- `worker/dispatcher.py`
- `worker/executor.py`
- `worker/nodes/readers/csv_reader.py`
- `worker/nodes/readers/json_reader.py`
- `worker/nodes/readers/minio_reader.py`
- `worker/nodes/transforms/json_transform.py`
- `worker/nodes/transforms/map_node.py`
- `worker/nodes/transforms/aggregate_node.py`
- `worker/nodes/media/image_resize.py`
- `worker/nodes/media/image_ocr.py`
- `worker/nodes/media/image_format_convert.py`
- `worker/nodes/media/video_extract.py`
- `worker/nodes/media/video_transcode.py`
- `worker/nodes/media/audio_extract.py`

# Deferred for a follow-up

以下内容建议暂缓，不放进这次首版：
- JMESPath 高级语法全覆盖（过滤、函数、切片、多重选择器等）
- Pandas `filter.query` 的可视化条件编辑器
- 运行时在节点内直接上传新文件
- 基于真实样本 JSON 的后端 schema/introspection/preview API

本次先把 schema-driven 可视化基础搭好，并先覆盖最痛的几类字段。

# Verification

## 前端交互验证
1. 在流程图中拖入两个节点，手动连线，确认边立即出现。
2. 保存后刷新页面，确认边仍存在。
3. 给 `csv_reader` / `json_reader` / 源媒体节点在节点面板中配置文件，保存后重新打开节点，确认 `key` 持久化成功。
4. 运行流水线时不再要求全局选文件；若源节点缺少 `key`，前端直接阻止提交并给出明确提示。
5. `json_transform` 的路径构建器能够生成表达式并回填到 `expression`；切换到手动输入后仍可直接修改。
6. `map.select`、`aggregate.group_by`、`image_ocr.lang` 等列表型字段可通过可视化方式增删项，并在重新打开节点后保留结构化值。
7. `map.rename`、`aggregate.agg` 能通过键值行编辑器配置并正确显示摘要。

## 后端 / worker 验证
1. 提交任务时请求体只包含 `pipelineId`。
2. 后端成功创建任务且 Kafka payload 不再包含 `inputKey`。
3. worker 能基于 graph 中的 `node.data.key` 运行 reader/source 节点。
4. 带上游输入的 transform/media 节点继续优先消费 `inputs`，不因删除全局 `inputKey` 而回归。
5. 旧图若缺少节点级文件配置，会在前端校验阶段失败，而不是进入 worker 后报隐晦错误。

## 建议执行顺序
1. 先修复 `FlowEditor.vue` 连线问题。
2. 再移除运行弹窗的全局选文件，并补齐节点级文件配置与前端校验。
3. 同步改掉 task submit / Kafka / worker 的 `inputKey` 链路。
4. 最后扩展 schema 字段元数据和 `NodeConfig` 的可视化控件，先落地 JMESPath builder + 列表/键值编辑器。
