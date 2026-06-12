from qgis.core import QgsGraduatedSymbolRenderer, QgsMarkerSymbol, QgsClassificationJenks, QgsRendererRange, QgsGradientColorRamp, QgsStyle
from qgis.PyQt.QtGui import QColor

def apply_renderer(layer, field_name, render_type="speed"):
    """使用 Jenks 自然断点分类 + 2mm圆点 + RdYlGn 色带"""

    # 基础符号：2mm 圆点，无外描边
    symbol = QgsMarkerSymbol.createSimple({
        'name': 'circle',
        'size': '2.0',
        'outline_style': 'no'
    })

    # 从 QGIS 样式库加载 RdYlGn 色带
    ramp = QgsStyle().defaultStyle().colorRamp("RdYlGn")
    if not ramp:
        ramp = QgsGradientColorRamp(QColor(0, 180, 0), QColor(180, 0, 0))

    # 使用 Jenks 自然断点计算 6 个分类
    jenks = QgsClassificationJenks()
    classes = jenks.classes(layer, field_name, 6)

    # 为每个分类创建渐染范围，从色带中取色赋给每个符号
    n = len(classes)
    ranges = []
    for i, c in enumerate(classes):
        ratio = i / (n - 1) if n > 1 else 0.5
        color = ramp.color(ratio)
        sym = symbol.clone()
        sym.setColor(color)
        rng = QgsRendererRange(c.lowerBound(), c.upperBound(), sym, c.label())
        ranges.append(rng)

    # 构建渐进渐染器
    renderer = QgsGraduatedSymbolRenderer(field_name, ranges)

    # 应用渐染
    layer.setRenderer(renderer)
    layer.triggerRepaint()
