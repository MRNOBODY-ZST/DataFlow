from nodes.readers.csv_reader import CsvReaderNode
from nodes.readers.json_reader import JsonReaderNode
from nodes.readers.minio_reader import MinioReaderNode
from nodes.transforms.filter_node import FilterNode
from nodes.transforms.map_node import MapNode
from nodes.transforms.aggregate_node import AggregateNode
from nodes.media.image_resize import ImageResizeNode
from nodes.media.image_ocr import ImageOCRNode
from nodes.media.video_extract import VideoExtractNode
from nodes.writers.minio_writer import MinioWriterNode

NODE_REGISTRY: dict = {
    "csv_reader": CsvReaderNode,
    "json_reader": JsonReaderNode,
    "minio_reader": MinioReaderNode,
    "filter": FilterNode,
    "map": MapNode,
    "aggregate": AggregateNode,
    "image_resize": ImageResizeNode,
    "image_ocr": ImageOCRNode,
    "video_extract": VideoExtractNode,
    "minio_writer": MinioWriterNode,
}
