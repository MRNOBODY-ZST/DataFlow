from nodes.readers.csv_reader import CsvReaderNode
from nodes.readers.json_reader import JsonReaderNode
from nodes.readers.minio_reader import MinioReaderNode
from nodes.transforms.aggregate_node import AggregateNode
from nodes.transforms.filter_node import FilterNode
from nodes.transforms.json_mapper import JsonMapperNode
from nodes.transforms.json_transform import JsonTransformNode
from nodes.transforms.map_node import MapNode
from nodes.media.audio_extract import AudioExtractNode
from nodes.media.image_format_convert import ImageFormatConvertNode
from nodes.media.image_ocr import ImageOCRNode
from nodes.media.image_resize import ImageResizeNode
from nodes.media.video_extract import VideoExtractNode
from nodes.media.image_convolution import ImageConvolutionNode
from nodes.media.image_edge_detect import ImageEdgeDetectNode
from nodes.media.image_gaussian_blur import ImageGaussianBlurNode
from nodes.media.image_pooling import ImagePoolingNode
from nodes.media.image_sharpen import ImageSharpenNode
from nodes.media.image_threshold import ImageThresholdNode
from nodes.media.video_transcode import VideoTranscodeNode
from nodes.writers.csv_writer import CsvWriterNode
from nodes.writers.minio_writer import MinioWriterNode

NODE_REGISTRY: dict = {
    "csv_reader": CsvReaderNode,
    "json_reader": JsonReaderNode,
    "minio_reader": MinioReaderNode,
    "filter": FilterNode,
    "map": MapNode,
    "aggregate": AggregateNode,
    "json_transform": JsonTransformNode,
    "json_mapper": JsonMapperNode,
    "image_resize": ImageResizeNode,
    "image_ocr": ImageOCRNode,
    "image_format_convert": ImageFormatConvertNode,
    "video_extract": VideoExtractNode,
    "video_transcode": VideoTranscodeNode,
    "audio_extract": AudioExtractNode,
    "image_convolution": ImageConvolutionNode,
    "image_pooling": ImagePoolingNode,
    "image_gaussian_blur": ImageGaussianBlurNode,
    "image_sharpen": ImageSharpenNode,
    "image_edge_detect": ImageEdgeDetectNode,
    "image_threshold": ImageThresholdNode,
    "minio_writer": MinioWriterNode,
    "csv_writer": CsvWriterNode,
}
