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
from nodes.utils.preview_node import PreviewNode
from nodes.writers.csv_writer import CsvWriterNode
from nodes.writers.minio_writer import MinioWriterNode

from nodes.media.image_s2_indices import ImageS2IndicesNode
from nodes.media.image_drone_index import ImageDroneIndexNode

from .S2Indices.image_s2_ndvi import ImageS2NdviNode
from .S2Indices.image_s2_gndvi import ImageS2GndviNode
from .S2Indices.image_s2_ndre import ImageS2NdreNode
from .S2Indices.image_s2_ireci import ImageS2IreciNode
from .S2Indices.image_s2_savi import ImageS2SaviNode
from .S2Indices.image_s2_lswi import ImageS2LswiNode
from .S2Indices.image_s2_ndwi import ImageS2NdwiNode
from .S2Indices.image_s2_mndwi import ImageS2MndwiNode
from .S2Indices.image_s2_evi import ImageS2EviNode

from .droneIndices.image_drone_ndvi import ImageDroneNdviNode
from .droneIndices.image_drone_gndvi import ImageDroneGndviNode
from .droneIndices.image_drone_ndre import ImageDroneNdreNode
from .droneIndices.image_drone_lci import ImageDroneLciNode
from .droneIndices.image_drone_sipi2 import ImageDroneSipi2Node
from .droneIndices.image_drone_gci import ImageDroneGciNode
from .droneIndices.image_drone_cirededge import ImageDroneCirededgeNode
from .droneIndices.image_drone_ngrdi import ImageDroneNgrdiNode
from .droneIndices.image_drone_rvi import ImageDroneRviNode
from .droneIndices.image_drone_dvi import ImageDroneDviNode
from .droneIndices.image_drone_savi import ImageDroneSaviNode
from .droneIndices.image_drone_msavi import ImageDroneMsaviNode

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

    "image_drone_index": ImageDroneIndexNode,
    "image_s2_indices": ImageS2IndicesNode,

     "image_s2_ndvi": ImageS2NdviNode,
    "image_s2_gndvi": ImageS2GndviNode,
    "image_s2_ndre": ImageS2NdreNode,
    "image_s2_ireci": ImageS2IreciNode,
    "image_s2_savi": ImageS2SaviNode,
    "image_s2_lswi": ImageS2LswiNode,
    "image_s2_ndwi": ImageS2NdwiNode,
    "image_s2_mndwi": ImageS2MndwiNode,
    "image_s2_evi": ImageS2EviNode,

    "image_drone_ndvi": ImageDroneNdviNode,
    "image_drone_gndvi": ImageDroneGndviNode,
    "image_drone_ndre": ImageDroneNdreNode,
    "image_drone_lci": ImageDroneLciNode,
    "image_drone_sipi2": ImageDroneSipi2Node,
    "image_drone_gci": ImageDroneGciNode,
    "image_drone_cirededge": ImageDroneCirededgeNode,
    "image_drone_ngrdi": ImageDroneNgrdiNode,
    "image_drone_rvi": ImageDroneRviNode,
    "image_drone_dvi": ImageDroneDviNode,
    "image_drone_savi": ImageDroneSaviNode,
    "image_drone_msavi": ImageDroneMsaviNode,
    
    "preview": PreviewNode,
    "minio_writer": MinioWriterNode,
    "csv_writer": CsvWriterNode,
}
