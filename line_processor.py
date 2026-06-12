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


def process_lines(gpx_file, elev_name="ELEV", speed_name="speed", progress_callback=None, densify=0):
    """Parse GPX and return a LineStringZ memory layer.

    Points are grouped by track segment and exploded into individual
    2-point line segments.  Each segment carries the average speed
    and elevation of its endpoints.
    """

    tree = ET.parse(gpx_file)
    root = tree.getroot()

    # ---- collect raw trkpt values, tracking segment boundaries ---- #
    points = []
    seg_idx = 0
    prev_tag = None
    for elem in root.iter():
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

        # a new <trkseg> means the next <trkpt> starts a new segment
        if tag == "trkseg":
            prev_tag = tag
            continue

        if tag != "trkpt":
            prev_tag = tag
            continue

        # first trkpt after a trkseg starts a new segment counter
        if prev_tag == "trkseg":
            seg_idx += 1
            # (seg_idx starts at 0 for the first trkseg; here it becomes 1.
            #  so we shift: the first trkseg gets seg_idx = 0)
            # Actually simpler: increment seg_idx before processing the group.
            pass

        # Actually, let me rethink: track segments explicitly.
        # Reset: iterate by finding <trkseg> and processing its children.
        prev_tag = tag

    # ---- simpler approach: iterate trk elements ---- #
    points = []
    seg_idx = 0
    for trk in root:
        if not trk.tag.endswith("trk"):
            continue
        for trkseg in trk:
            if not trkseg.tag.endswith("trkseg"):
                continue
            # ---- process each <trkpt> inside this <trkseg> ---- #
            for trkpt in trkseg:
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
                        except Exception:
                            pass
                    elif ct == "speed":
                        try:
                            speed = float(child.text)
                        except Exception:
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

    # ---- build the LineStringZ memory layer ---- #
    crs = QgsCoordinateReferenceSystem("EPSG:4326")
    out = QgsVectorLayer(f"LineStringZM?crs={crs.authid()}", "coloredGPX_lines", "memory")
    provider = out.dataProvider()
    provider.addAttributes([
        QgsField(speed_name, _Double, "double"),
        QgsField(elev_name, _Double, "double"),
        QgsField("time", _String, "string"),
    ])
    out.updateFields()

    # ---- group by seg_idx and explode into 2-point segments ---- #
    seg_groups = {}
    for d in points:
        seg_groups.setdefault(d["seg_idx"], []).append(d)

    feats = []
    total_pairs = sum(max(0, len(pts) - 1) for pts in seg_groups.values())
    total_lines = total_pairs * (densify + 1) if densify > 0 else total_pairs
    done = 0
    for pts in seg_groups.values():
        for i in range(len(pts) - 1):
            p1, p2 = pts[i], pts[i + 1]
            # Generate sub-segments (original or densified)
            segments = []
            if densify > 0:
                sub = [p1]
                for j in range(1, densify + 1):
                    t = j / (densify + 1)
                    sub.append({
                        "lon": p1["lon"] + t * (p2["lon"] - p1["lon"]),
                        "lat": p1["lat"] + t * (p2["lat"] - p1["lat"]),
                        "ele": p1["ele"] + t * (p2["ele"] - p1["ele"]),
                        "speed": p1["speed"] + t * (p2["speed"] - p1["speed"]),
                    })
                sub.append(p2)
                segments = [(sub[k], sub[k + 1]) for k in range(len(sub) - 1)]
            else:
                segments = [(p1, p2)]
            # Create features for each sub-segment
            for d1, d2 in segments:
                g1 = QgsPoint(d1["lon"], d1["lat"], d1["ele"], d1["speed"])
                g2 = QgsPoint(d2["lon"], d2["lat"], d2["ele"], d2["speed"])
                line = QgsGeometry.fromPolyline([g1, g2])
                f = QgsFeature(out.fields())
                f.setGeometry(line)
                f.setAttributes([(d1["speed"] + d2["speed"]) / 2.0,
                                 (d1["ele"] + d2["ele"]) / 2.0, ""])
                feats.append(f)
                done += 1
                if progress_callback:
                    progress_callback(done, total_lines)

    provider.addFeatures(feats)
    return out
