# -*- coding: utf-8 -*-
def classFactory(iface):
    from .coloredgpx import ColoredGPX
    return ColoredGPX(iface)