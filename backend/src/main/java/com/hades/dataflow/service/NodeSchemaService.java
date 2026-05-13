package com.hades.dataflow.service;

import com.hades.dataflow.domain.dto.NodeSchemaDTO;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class NodeSchemaService {

    public List<NodeSchemaDTO> getAll() {
        List<NodeSchemaDTO> schemas = new ArrayList<>();

        schemas.add(new NodeSchemaDTO("csv_reader", "CSV 读取", "readers", "DocumentTextIcon", List.of(
            new NodeSchemaDTO.FieldDef("key", "MinIO 对象 Key", "file-picker", "input/xxx/data.csv", true, false, null, null, null)
        )));

        schemas.add(new NodeSchemaDTO("json_reader", "JSON 读取", "readers", "CodeBracketIcon", List.of(
                new NodeSchemaDTO.FieldDef("key", "MinIO 对象 Key", "file-picker", "input/xxx/data.json", true, false, null, null, null)
        )));

        schemas.add(new NodeSchemaDTO("minio_reader", "MinIO 读取", "readers", "CloudArrowDownIcon", List.of(
            new NodeSchemaDTO.FieldDef("key", "MinIO 对象 Key", "file-picker", "input/xxx/file", false, false, null, null, null),
              new NodeSchemaDTO.FieldDef("bucket", "源 Bucket（默认 dataflow-input）", "text", "dataflow-input", false, false, null, null, null)
        )));

        schemas.add(new NodeSchemaDTO("filter", "过滤", "transforms", "FunnelIcon", List.of(
                new NodeSchemaDTO.FieldDef("query", "Pandas Query 表达式", "text", "age > 18", true, false, null, null, null)
        )));

      schemas.add(new NodeSchemaDTO("map", "字段映射", "transforms", "ArrowsRightLeftIcon", List.of(
                new NodeSchemaDTO.FieldDef("rename", "字段重命名", "textarea", "{\"old\":\"new\"}", false, false, null, "key-value",
                new NodeSchemaDTO.WidgetConfig("原字段名", "新字段名", "text", null)),
                new NodeSchemaDTO.FieldDef("select", "保留列", "text", "[\"colA\",\"colB\"]", false, false, null, "string-array", null)
      )));

        schemas.add(new NodeSchemaDTO("aggregate", "聚合", "transforms", "ChartBarIcon", List.of(
                new NodeSchemaDTO.FieldDef("group_by", "分组列", "text", "[\"category\"]", true, false, null, "string-array", null),
     new NodeSchemaDTO.FieldDef("agg", "聚合方法", "textarea", "{\"amount\":\"sum\"}", true, false, null, "key-value",
          new NodeSchemaDTO.WidgetConfig("字段名", "聚合函数", "select", List.of("sum", "avg", "min", "max", "count", "first", "last")))
        )));

        schemas.add(new NodeSchemaDTO("json_transform", "JSON 转换", "transforms", "CodeBracketSquareIcon", List.of(
              new NodeSchemaDTO.FieldDef("expression", "JMESPath 表达式", "text", "items[*].name", true, false, null, "jmespath", null)
        )));

        schemas.add(new NodeSchemaDTO("image_resize", "图片缩放", "media", "PhotoIcon", List.of(
          new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/image.jpg", false, false, null, null, null),
         new NodeSchemaDTO.FieldDef("width", "宽度 (px)", "number", "800", false, false, null, null, null),
         new NodeSchemaDTO.FieldDef("height", "高度 (px)", "number", "600", false, false, null, null, null),
            new NodeSchemaDTO.FieldDef("format", "输出格式", "select", "JPEG", false, false, List.of("JPEG", "PNG", "WEBP"), null, null)
        )));

        schemas.add(new NodeSchemaDTO("image_ocr", "图片 OCR", "media", "LanguageIcon", List.of(
                new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/image.jpg", false, false, null, null, null),
                new NodeSchemaDTO.FieldDef("lang", "语言", "text", "[\"ch_sim\",\"en\"]", false, false, null, "string-array", null)
        )));

        schemas.add(new NodeSchemaDTO("image_format_convert", "图片格式转换", "media", "ArrowPathIcon", List.of(
                new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/image.jpg", false, false, null, null, null),
                new NodeSchemaDTO.FieldDef("format", "目标格式", "select", "PNG", true, false, List.of("JPEG", "PNG", "WEBP", "BMP", "TIFF"), null, null)
      )));

        schemas.add(new NodeSchemaDTO("video_extract", "视频抽帧", "media", "FilmIcon", List.of(
        new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/video.mp4", false, false, null, null, null),
                new NodeSchemaDTO.FieldDef("fps", "抽帧率 (FPS)", "number", "1", false, false, null, null, null),
            new NodeSchemaDTO.FieldDef("output_prefix", "输出前缀", "text", "frames/task1/", false, false, null, null, null)
     )));

        schemas.add(new NodeSchemaDTO("video_transcode", "视频转码", "media", "VideoCameraIcon", List.of(
                new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/video.mp4", false, false, null, null, null),
                new NodeSchemaDTO.FieldDef("codec", "编码格式", "select", "h264", true, false, List.of("h264", "h265", "vp9"), null, null),
           new NodeSchemaDTO.FieldDef("bitrate", "码率 (kbps)", "number", "2000", false, false, null, null, null)
        )));

        schemas.add(new NodeSchemaDTO("audio_extract", "音频提取", "media", "MusicalNoteIcon", List.of(
         new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/video.mp4", false, false, null, null, null),
                new NodeSchemaDTO.FieldDef("format", "音频格式", "select", "mp3", true, false, List.of("mp3", "aac", "wav"), null, null)
        )));

        schemas.add(new NodeSchemaDTO("minio_writer", "MinIO 写出", "writers", "CloudArrowUpIcon", List.of(
                new NodeSchemaDTO.FieldDef("key", "输出 Key", "text", "output/result", false, false, null, null, null),
                new NodeSchemaDTO.FieldDef("bucket", "目标 Bucket（默认 dataflow-output）", "text", "dataflow-output", false, false, null, null, null)
        )));

        schemas.add(new NodeSchemaDTO("csv_writer", "CSV 写出", "writers", "TableCellsIcon", List.of(
          new NodeSchemaDTO.FieldDef("key", "输出 Key", "text", "output/result.csv", false, false, null, null, null)
        )));

        return schemas;
    }
}
