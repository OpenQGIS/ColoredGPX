from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsPoint, QgsGeometry, QgsCoordinateReferenceSystem
from qgis.PyQt.QtCore import QVariant
try:
    from qgis.PyQt.QtCore import QMetaType
    _Int = QMetaType.Int
    _Double = QMetaType.Double
    _String = QMetaType.QString
except (ImportError, AttributeError):
    _Int = _Int
    _Double = _Double
    _String = _String
import xml.etree.ElementTree as ET


def process_points(gpx_file, elev_name="ELEV", speed_name="speed", progress_callback=None):
    """Parse GPX and return a PointZM memory layer with speed, elevation, time, track_seg_point_id."""

    tree = ET.parse(gpx_file)
    root = tree.getroot()

    points = []
    seg_idx = 0
    for elem in root.iter():
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if tag != "trkseg":
            continue
        for trkpt in elem:
            if not trkpt.tag.endswith("trkpt"):
                continue
            ele = 0.0
            speed = 0.0
            time_val = ""
            for child in trkpt:
                ct = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if ct == "ele":
                    try:
                        ele = float(child.text)
                    except:
                        pass
                elif ct == "speed":
                    try:
                        speed = float(child.text)
                    except:
                        pass
                elif ct == "time":
                    time_val = child.text or ""
            points.append(dict(
                lon=float(trkpt.attrib.get("lon", 0)),
                lat=float(trkpt.attrib.get("lat", 0)),
                ele=ele,
                speed=speed,
                time=time_val,
                seg_idx=seg_idx,
            ))
        seg_idx += 1

    # memory layer: PointZM (ele -> Z, speed -> M)
    crs = QgsCoordinateReferenceSystem("EPSG:4326")
    out = QgsVectorLayer(f"PointZM?crs={crs.authid()}", "coloredGPX_points", "memory")
    provider = out.dataProvider()
    provider.addAttributes([
        QgsField(speed_name, _Double, "double"),
        QgsField(elev_name, _Double, "double"),
        QgsField("time", _String, "string"),
        QgsField("track_seg_point_id", _Int, "integer"),
    ])
    out.updateFields()

    # group by seg_idx, assign per-segment point index
    seg_groups = {}
    for d in points:
        seg_groups.setdefault(d["seg_idx"], []).append(d)

    feats = []
    total = len(points)
    for sid, pts in seg_groups.items():
        for pt_idx, d in enumerate(pts):
            f = QgsFeature(out.fields())
            pt = QgsPoint(d["lon"], d["lat"], d["ele"], d["speed"])
            f.setGeometry(QgsGeometry(pt))
            f.setAttributes([d["speed"], d["ele"], d["time"], pt_idx])
            feats.append(f)
            if progress_callback:
                progress_callback(len(feats), total)

    provider.addFeatures(feats)
    return out
