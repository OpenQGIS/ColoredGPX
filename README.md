# ColoredGPX

> 将 GPX 轨迹按速度或高程渲染为渐变色图层的 QGIS 插件

**ColoredGPX** 从 GPX 文件的 `track_points` 图层中提取速度（speed）和高程（elevation）信息，生成点或线图层，并按对应属性进行分级色彩渲染，让轨迹数据一目了然。

## 功能特性

- **点渲染 / 线渲染** — 两种模式自由切换，点模式逐点着色，线模式逐段着色
- **速度 / 高程渲染** — 按速度或高程值自动分级，支持 Jenks 自然断裂分类
- **色带选择** — 使用 QGIS 内置色带，带实时预览缩略图，支持滚动选择
- **反转色带** — 一键翻转渐变方向
- **线增密** — 在相邻 GPS 点之间插值，使线段色彩过渡更平滑（滑块 0~5）
- **输出控制** — 创建临时图层或保存为 GeoJSON / GPKG / Shapefile
- **进度条** — 实时显示算法处理进度
- **中英双语** — 界面语言跟随 QGIS 系统设置自动切换

## 安装

1. 下载或克隆本仓库到 QGIS 插件目录：

   ```
   # Windows
   %APPDATA%\QGIS\QGIS3\profiles\<profile>\python\plugins\ColoredGPX

   # macOS / Linux
   ~/.local/share/QGIS/QGIS3/profiles/<profile>/python/plugins/ColoredGPX
   ```

2. 打开 QGIS → 插件 → 管理并安装插件 → 搜索 ColoredGPX → 启用

## 使用方法

1. 加载一个 GPX 文件，QGIS 会自动创建 `track_points` 图层
2. 点击工具栏的 **GPX → coloredGPX** 按钮
3. 在弹出面板中：
   - 选择输入图层（GPX 的 track_points）
   - 选择渲染模式（点 / 线）
   - 选择渲染字段（速度 / 高程）
   - 选择色带并可选反转
   - 线模式下可调整增密间距
4. 点击 **确定运行**
5. 渲染完成后图层自动添加到地图

## 项目结构

```
ColoredGPX/
├── __init__.py          # 插件入口
├── coloredgpx.py        # 主对话框和插件逻辑
├── point_processor.py   # GPX 点数据解析
├── point_renderer.py    # 点分级渲染器
├── line_processor.py    # GPX 线数据解析
├── line_renderer.py     # 线分级渲染器
├── metadata.txt         # QGIS 插件元数据
├── icons/
│   ├── icon.png         # 插件管理器图标
│   └── icon.svg         # 工具栏图标
└── README.md
```

## 兼容性

| 项目 | 要求 |
|------|------|
| QGIS | 3.1 ~ 4.99 (LTR / Latest) |
| Python | 3.x |
| 依赖 | 仅使用 QGIS / PyQt 内置模块，无需额外安装 |

## 许可证

GPL-2.0-or-later

## 作者

**OpenQGIS** · [GitHub](https://github.com/OpenQGIS) · OpenQGIS@outlook.com
