# gee_export_manager.py
import sys
import types
sys.modules['blessings'] = types.SimpleNamespace()
import ee
import datetime
import time

# 初始化 Earth Engine
ee.Initialize(project='ee-xupingpan415')

# 设置区域（可按需参数化）
roi = ee.FeatureCollection("projects/ee-xupingpan415/assets/Export_Custom_Region")

def mask_s2_clouds(image):
    qa = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    return image.updateMask(mask).divide(10000)

def export_monthly_images(start_year=2023, end_year=2023, folder_name="Sentinel2_Monthly", delay_sec=2):

    """
    将某年份范围内每个月的影像导出到 Google Drive 的指定文件夹中。
    """
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            start = datetime.date(year, month, 1)
            end = datetime.date(year + 1, 1, 1) if month == 12 else datetime.date(year, month + 1, 1)

            collection = (
                ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(roi)
                .filterDate(str(start), str(end))
                .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
                .map(mask_s2_clouds)
                .select(["B8", "B4", "B3"])
            )

            image = collection.median().clip(roi)
            description = f"S2_{year}_{month:02d}"

            task = ee.batch.Export.image.toDrive(
                image=image,
                description=description,
                folder=folder_name,
                fileNamePrefix=description,
                region=roi.geometry(),
                scale=10,
                crs="EPSG:4326",
                maxPixels=1e13
            )
            task.start()
            print(f"[GEE导出任务提交] {description}")
            time.sleep(delay_sec)
def export_one_day_image(year: int, month: int, day: int, folder_name="Sentinel2_OneDay", delay_sec=2):
    """
    导出某一天的 Sentinel-2 影像（中位数合成）到 Google Drive。
    """
    start = datetime.date(year, month, day)
    end = start + datetime.timedelta(days=1)

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(roi)
        .filterDate(str(start), str(end))
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 70))
        .map(mask_s2_clouds)
        .select(["B8", "B4", "B3"])
    )

    # 🚫 检查影像是否为空
    if collection.size().getInfo() == 0:
        print(f"[跳过] S2_{year}_{month:02d}_{day:02d}：无可用影像")
        return

    image = collection.median().clip(roi)
    description = f"S2_{year}_{month:02d}_{day:02d}"

    task = ee.batch.Export.image.toDrive(
        image=image,
        description=description,
        folder=folder_name,
        fileNamePrefix=description,
        region=roi.geometry(),
        scale=10,
        crs="EPSG:4326",
        maxPixels=1e13
    )
    task.start()
    print(f"[GEE导出任务提交] {description}")
    time.sleep(delay_sec)
