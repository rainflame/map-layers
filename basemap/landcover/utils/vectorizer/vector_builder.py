import os
import sys

import rasterio
import geopandas as gpd

vectorizer_dir = os.path.dirname(__file__)
sys.path.append(vectorizer_dir)
import cover_computer as cc
import loop_computer as lc
import segments_computer as sc


class VectorBuilder:
    def __init__(self, raster_filepath):
        self.raster_filepath = raster_filepath
        self.get_data_and_transform()
        self.build()

    def get_data_and_transform(self):
        with rasterio.open(self.raster_filepath,) as src:
            self.meta = src.meta
            self.data = src.read(1)
            self.transform = src.transform

    def build(self):
        self.covers = cc.build(self.data, self.transform)
        self.loops = lc.build(self.covers)
        self.segments = sc.build(self.loops)

    def run_per_segment(self, per_segment_function):
        sc.update(self.segments, per_segment_function)
    
    def rebuild(self):
        lc.rebuild(self.loops)
        cc.rebuild(self.covers)

    def save(self, output_filepath):
        modified_polygons = [c.modified_polygon for c in self.covers]
        labels = [c.label for c in self.covers]
        crs = self.meta['crs']

        gdf = gpd.GeoDataFrame(geometry=modified_polygons)
        gdf['label'] = labels
        gdf.crs = crs
        gdf.to_file(output_filepath)