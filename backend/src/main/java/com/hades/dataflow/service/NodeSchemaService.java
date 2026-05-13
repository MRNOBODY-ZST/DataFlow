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
            new NodeSchemaDTO.FieldDef("key", "MinIO 对象 Key", "file-picker", "input/xxx/data.csv", true, false, null, null, null, true)
        )));

        schemas.add(new NodeSchemaDTO("json_reader", "JSON 读取", "readers", "CodeBracketIcon", List.of(
                new NodeSchemaDTO.FieldDef("key", "MinIO 对象 Key", "file-picker", "input/xxx/data.json", true, false, null, null, null, true)
        )));

        schemas.add(new NodeSchemaDTO("minio_reader", "MinIO 读取", "readers", "CloudArrowDownIcon", List.of(
            new NodeSchemaDTO.FieldDef("key", "文件或文件夹路径", "file-picker", "input/xxx/file", true, false, null, null, null, true),
              new NodeSchemaDTO.FieldDef("bucket", "源 Bucket（默认 dataflow-input）", "text", "dataflow-input", false, false, null, null, null, false)
        )));


        schemas.add(new NodeSchemaDTO("filter", "过滤", "transforms", "FunnelIcon", List.of(
                new NodeSchemaDTO.FieldDef("query", "Pandas Query 表达式", "text", "age > 18", true, false, null, null, null, true)
        )));

      schemas.add(new NodeSchemaDTO("map", "字段映射", "transforms", "ArrowsRightLeftIcon", List.of(
                new NodeSchemaDTO.FieldDef("rename", "字段重命名", "textarea", "{\"old\":\"new\"}", false, false, null, "key-value",
                new NodeSchemaDTO.WidgetConfig("原字段名", "新字段名", "text", null), false),
                new NodeSchemaDTO.FieldDef("select", "保留列", "text", "[\"colA\",\"colB\"]", false, false, null, "string-array", null, false)
      )));

        schemas.add(new NodeSchemaDTO("aggregate", "聚合", "transforms", "ChartBarIcon", List.of(
                new NodeSchemaDTO.FieldDef("group_by", "分组列", "text", "[\"category\"]", true, false, null, "string-array", null, false),
     new NodeSchemaDTO.FieldDef("agg", "聚合方法", "textarea", "{\"amount\":\"sum\"}", true, false, null, "key-value",
          new NodeSchemaDTO.WidgetConfig("字段名", "聚合函数", "select", List.of("sum", "avg", "min", "max", "count", "first", "last")), false)
        )));

        schemas.add(new NodeSchemaDTO("json_transform", "JSON 转换", "transforms", "CodeBracketSquareIcon", List.of(
              new NodeSchemaDTO.FieldDef("expression", "JMESPath 表达式", "text", "items[*].name", true, false, null, "jmespath", null, true)
        )));

        schemas.add(new NodeSchemaDTO("json_mapper", "JSON 可视化映射", "transforms", "MapIcon", List.of(
            new NodeSchemaDTO.FieldDef("mappings", "字段映射", "text", null, false, false, null, "json-mapper", null, true),
            new NodeSchemaDTO.FieldDef("sample", "JSON 样本（用于解析字段树）", "textarea", "{}", false, false, null, null, null, false)
        )));

        schemas.add(new NodeSchemaDTO("image_resize", "图片缩放", "media", "PhotoIcon", List.of(
          new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/image.jpg", false, false, null, null, null, false),
         new NodeSchemaDTO.FieldDef("width", "宽度 (px)", "number", "800", false, false, null, null, null, true),
         new NodeSchemaDTO.FieldDef("height", "高度 (px)", "number", "600", false, false, null, null, null, true),
            new NodeSchemaDTO.FieldDef("format", "输出格式", "select", "JPEG", false, false, List.of("JPEG", "PNG", "WEBP"), null, null, true)
        )));

        schemas.add(new NodeSchemaDTO("image_ocr", "图片 OCR", "media", "LanguageIcon", List.of(
                new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/image.jpg", false, false, null, null, null, false),
                new NodeSchemaDTO.FieldDef("lang", "语言", "text", "[\"ch_sim\",\"en\"]", false, false, null, "string-array", null, true)
        )));

        schemas.add(new NodeSchemaDTO("image_format_convert", "图片格式转换", "media", "ArrowPathIcon", List.of(
                new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/image.jpg", false, false, null, null, null, false),
                new NodeSchemaDTO.FieldDef("format", "目标格式", "select", "PNG", true, false, List.of("JPEG", "PNG", "WEBP", "BMP", "TIFF"), null, null, true)
      )));

        schemas.add(new NodeSchemaDTO("video_extract", "视频抽帧", "media", "FilmIcon", List.of(
        new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/video.mp4", false, false, null, null, null, false),
                new NodeSchemaDTO.FieldDef("fps", "抽帧率 (FPS)", "number", "1", false, false, null, null, null, true),
            new NodeSchemaDTO.FieldDef("output_prefix", "输出前缀", "text", "frames/task1/", false, false, null, null, null, false)
     )));

        schemas.add(new NodeSchemaDTO("video_transcode", "视频转码", "media", "VideoCameraIcon", List.of(
                new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/video.mp4", false, false, null, null, null, false),
                new NodeSchemaDTO.FieldDef("codec", "编码格式", "select", "h264", true, false, List.of("h264", "h265", "vp9"), null, null, true),
           new NodeSchemaDTO.FieldDef("bitrate", "码率 (kbps)", "number", "2000", false, false, null, null, null, true)
        )));

        schemas.add(new NodeSchemaDTO("audio_extract", "音频提取", "media", "MusicalNoteIcon", List.of(
         new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/video.mp4", false, false, null, null, null, false),
                new NodeSchemaDTO.FieldDef("format", "音频格式", "select", "mp3", true, false, List.of("mp3", "aac", "wav"), null, null, true)
        )));

        schemas.add(new NodeSchemaDTO("image_convolution", "图片卷积", "media", "AdjustmentsHorizontalIcon", List.of(
            new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/image.jpg", false, false, null, null, null, false),
            new NodeSchemaDTO.FieldDef("preset", "预设卷积核", "select", "blur", false, false, List.of("blur", "sharpen", "contour", "detail", "edge_enhance", "emboss", "smooth", "custom"), null, null, true),
            new NodeSchemaDTO.FieldDef("kernel", "自定义卷积核（JSON 数组，preset=custom 时生效）", "textarea", "[0,-1,0,-1,5,-1,0,-1,0]", false, false, null, null, null, false),
            new NodeSchemaDTO.FieldDef("kernel_size", "卷积核尺寸", "select", "3", false, false, List.of("3", "5"), null, null, false),
            new NodeSchemaDTO.FieldDef("offset", "偏移量", "number", "0", false, false, null, null, null, false),
            new NodeSchemaDTO.FieldDef("format", "输出格式", "select", "JPEG", false, false, List.of("JPEG", "PNG", "WEBP"), null, null, true)
        )));

        schemas.add(new NodeSchemaDTO("image_pooling", "图片池化", "media", "Squares2X2Icon", List.of(
            new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/image.jpg", false, false, null, null, null, false),
            new NodeSchemaDTO.FieldDef("method", "池化方法", "select", "max", true, false, List.of("max", "avg"), null, null, true),
            new NodeSchemaDTO.FieldDef("pool_size", "池化窗口大小", "select", "2", false, false, List.of("2", "3", "4", "8"), null, null, true),
            new NodeSchemaDTO.FieldDef("stride", "步长（默认等于窗口大小）", "number", "2", false, false, null, null, null, true),
            new NodeSchemaDTO.FieldDef("format", "输出格式", "select", "JPEG", false, false, List.of("JPEG", "PNG", "WEBP"), null, null, true)
        )));

        schemas.add(new NodeSchemaDTO("image_gaussian_blur", "高斯模糊", "media", "EyeDropperIcon", List.of(
            new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/image.jpg", false, false, null, null, null, false),
            new NodeSchemaDTO.FieldDef("radius", "模糊半径", "number", "2", true, false, null, null, null, true),
            new NodeSchemaDTO.FieldDef("format", "输出格式", "select", "JPEG", false, false, List.of("JPEG", "PNG", "WEBP"), null, null, true)
        )));

        schemas.add(new NodeSchemaDTO("image_sharpen", "图片锐化", "media", "SparklesIcon", List.of(
            new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/image.jpg", false, false, null, null, null, false),
            new NodeSchemaDTO.FieldDef("method", "锐化方法", "select", "unsharp_mask", true, false, List.of("unsharp_mask", "sharpen_filter", "detail"), null, null, true),
            new NodeSchemaDTO.FieldDef("radius", "USM 半径", "number", "2", false, false, null, null, null, true),
            new NodeSchemaDTO.FieldDef("percent", "USM 强度 (%)", "number", "150", false, false, null, null, null, true),
            new NodeSchemaDTO.FieldDef("threshold", "USM 阈值", "number", "3", false, false, null, null, null, true),
            new NodeSchemaDTO.FieldDef("factor", "额外锐化因子（1.0=不变）", "number", "1.0", false, false, null, null, null, false),
            new NodeSchemaDTO.FieldDef("format", "输出格式", "select", "JPEG", false, false, List.of("JPEG", "PNG", "WEBP"), null, null, true)
        )));

        schemas.add(new NodeSchemaDTO("image_edge_detect", "边缘检测", "media", "ViewfinderCircleIcon", List.of(
            new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/image.jpg", false, false, null, null, null, false),
            new NodeSchemaDTO.FieldDef("method", "检测方法", "select", "find_edges", true, false, List.of("find_edges", "sobel", "contour", "edge_enhance", "edge_enhance_more"), null, null, true),
            new NodeSchemaDTO.FieldDef("format", "输出格式", "select", "PNG", false, false, List.of("JPEG", "PNG", "WEBP"), null, null, true)
        )));

        schemas.add(new NodeSchemaDTO("image_threshold", "图片二值化", "media", "SunIcon", List.of(
            new NodeSchemaDTO.FieldDef("key", "源文件 Key（无上游时必填）", "file-picker", "input/xxx/image.jpg", false, false, null, null, null, false),
            new NodeSchemaDTO.FieldDef("method", "阈值方法", "select", "binary", true, false, List.of("binary", "binary_inv", "truncate", "to_zero", "otsu"), null, null, true),
            new NodeSchemaDTO.FieldDef("threshold", "阈值（0-255，Otsu 时自动计算）", "number", "128", false, false, null, null, null, true),
            new NodeSchemaDTO.FieldDef("format", "输出格式", "select", "PNG", false, false, List.of("JPEG", "PNG", "WEBP"), null, null, true)
        )));

        schemas.add(new NodeSchemaDTO("minio_writer", "MinIO 写出", "writers", "CloudArrowUpIcon", List.of(
                new NodeSchemaDTO.FieldDef("key", "输出 Key", "text", "output/result", false, false, null, null, null, true),
                new NodeSchemaDTO.FieldDef("bucket", "目标 Bucket（默认 dataflow-output）", "text", "dataflow-output", false, false, null, null, null, false)
        )));

        schemas.add(new NodeSchemaDTO("csv_writer", "CSV 写出", "writers", "TableCellsIcon", List.of(
          new NodeSchemaDTO.FieldDef("key", "输出 Key", "text", "output/result.csv", false, false, null, null, null, true)
        )));

        return schemas;
    }
}
