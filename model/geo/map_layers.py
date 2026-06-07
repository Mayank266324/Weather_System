try:
    import geopandas as gpd
except ImportError:
    gpd = None


class MapLayerRegistry:
    """Boundary for GIS vector/raster layers without coupling them to the GUI."""

    def __init__(self):
        self.layers = []

    def list_layers(self):
        return list(self.layers)

    def add_vector_file(self, path, name=None):
        if gpd is None:
            raise RuntimeError("GeoPandas is required to load external vector GIS layers.")

        frame = gpd.read_file(path)
        layer = {
            "name": name or str(path),
            "type": "vector",
            "path": str(path),
            "crs": str(frame.crs) if frame.crs else "",
            "bounds": tuple(float(value) for value in frame.total_bounds),
            "feature_count": int(len(frame)),
            "data": frame,
        }
        self.layers.append(layer)
        return layer
