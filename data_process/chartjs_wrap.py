import json
from typing import (
    Any, Dict, List, Optional, Union, Literal, 
    TypedDict, TypeVar, Generic, overload
)
from dataclasses import dataclass, field, asdict
from enum import Enum

# =====================
# 核心类型定义
# =====================

class ChartType(str, Enum):
    """Chart.js支持的所有图表类型"""
    LINE = 'line'
    BAR = 'bar'
    PIE = 'pie'
    DOUGHNUT = 'doughnut'
    POLAR_AREA = 'polarArea'
    RADAR = 'radar'
    SCATTER = 'scatter'

class PointStyle(str, Enum):
    """数据点样式选项"""
    CIRCLE = 'circle'
    CROSS = 'cross'
    CROSS_ROT = 'crossRot'
    DASH = 'dash'
    LINE = 'line'
    RECT = 'rect'
    RECT_ROUNDED = 'rectRounded'
    RECT_ROT = 'rectRot'
    STAR = 'star'
    TRIANGLE = 'triangle'

class ScaleType(str, Enum):
    """坐标轴类型"""
    LINEAR = 'linear'
    LOGARITHMIC = 'logarithmic'
    CATEGORY = 'category'
    TIME = 'time'
    TIMESERIES = 'timeseries'

class Position(str, Enum):
    """元素位置选项"""
    TOP = 'top'
    LEFT = 'left'
    BOTTOM = 'bottom'
    RIGHT = 'right'

class TextAlign(str, Enum):
    """文本对齐方式"""
    START = 'start'
    CENTER = 'center'
    END = 'end'

class Easing(str, Enum):
    """动画缓动函数"""
    LINEAR = 'linear'
    EASE_IN_QUAD = 'easeInQuad'
    EASE_OUT_QUAD = 'easeOutQuad'
    EASE_IN_OUT_QUAD = 'easeInOutQuad'
    EASE_IN_CUBIC = 'easeInCubic'
    EASE_OUT_CUBIC = 'easeOutCubic'
    EASE_IN_OUT_CUBIC = 'easeInOutCubic'
    EASE_IN_QUART = 'easeInQuart'
    EASE_OUT_QUART = 'easeOutQuart'
    EASE_IN_OUT_QUART = 'easeInOutQuart'
    EASE_IN_QUINT = 'easeInQuint'
    EASE_OUT_QUINT = 'easeOutQuint'
    EASE_IN_OUT_QUINT = 'easeInOutQuint'
    EASE_IN_SINE = 'easeInSine'
    EASE_OUT_SINE = 'easeOutSine'
    EASE_IN_OUT_SINE = 'easeInOutSine'
    EASE_IN_EXPO = 'easeInExpo'
    EASE_OUT_EXPO = 'easeOutExpo'
    EASE_IN_OUT_EXPO = 'easeInOutExpo'
    EASE_IN_CIRC = 'easeInCirc'
    EASE_OUT_CIRC = 'easeOutCirc'
    EASE_IN_OUT_CIRC = 'easeInOutCirc'
    EASE_IN_ELASTIC = 'easeInElastic'
    EASE_OUT_ELASTIC = 'easeOutElastic'
    EASE_IN_OUT_ELASTIC = 'easeInOutElastic'
    EASE_IN_BACK = 'easeInBack'
    EASE_OUT_BACK = 'easeOutBack'
    EASE_IN_OUT_BACK = 'easeInOutBack'
    EASE_IN_BOUNCE = 'easeInBounce'
    EASE_OUT_BOUNCE = 'easeOutBounce'
    EASE_IN_OUT_BOUNCE = 'easeInOutBounce'

# =====================
# 数据结构模型
# =====================

OptionalValue = TypeVar('OptionalValue')

def optional_field(default: OptionalValue = None) -> OptionalValue:
    """辅助函数，为字段创建None默认值"""
    return field(default=default)

@dataclass
class Color:
    """颜色定义 - 支持多种格式"""
    value: Union[str, List[float]]  # '#FF0000', 'rgba(255,0,0,0.5)', [1,0,0]
    
    def __str__(self) -> str:
        if isinstance(self.value, list):
            if len(self.value) == 4:  # RGBA
                return f"rgba({self.value[0]*255}, {self.value[1]*255}, {self.value[2]*255}, {self.value[3]})"
            return f"rgb({self.value[0]*255}, {self.value[1]*255}, {self.value[2]*255})"
        return str(self.value)
    
    def to_dict(self) -> str:
        return str(self)

@dataclass
class Font:
    """字体配置"""
    family: Optional[str] = None
    size: Optional[int] = None
    style: Optional[str] = None
    weight: Optional[str] = None
    lineHeight: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for field_name, value in asdict(self).items():
            if value is not None:
                result[field_name] = value
        return result if result else {}

@dataclass
class Border:
    """边框配置"""
    width: Optional[Union[int, List[int]]] = None
    color: Optional[Union[Color, List[Color], str, List[str]]] = None
    dash: Optional[List[int]] = None  # [dash, gap]
    dashOffset: Optional[float] = None
    capStyle: Optional[str] = None
    joinStyle: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        
        if self.width is not None:
            result['borderWidth'] = self.width
        
        if self.color is not None:
            if isinstance(self.color, list):
                result['borderColor'] = [str(c) if isinstance(c, Color) else c for c in self.color]
            elif isinstance(self.color, Color):
                result['borderColor'] = str(self.color)
            else:
                result['borderColor'] = self.color
        
        if self.dash is not None:
            result['borderDash'] = self.dash
            
        if self.dashOffset is not None:
            result['borderDashOffset'] = self.dashOffset
        
        if self.capStyle is not None:
            result['borderCapStyle'] = self.capStyle
            
        if self.joinStyle is not None:
            result['borderJoinStyle'] = self.joinStyle
            
        return result if result else {}

# =====================
# 数据集基类和子类
# =====================

T = TypeVar('T', bound='Dataset')

@dataclass
class Dataset(Generic[T]):
    """数据集基类 - 所有图表类型的基础"""
    label: Optional[str] = None
    data: Optional[List[Union[int, float, Dict[str, Any]]]] = None
    order: Optional[int] = None
    stack: Optional[str] = None
    hidden: Optional[bool] = None
    
    # 样式属性
    backgroundColor: Optional[Union[Color, List[Color], str, List[str]]] = None
    borderColor: Optional[Union[Color, List[Color], str, List[str]]] = None
    borderWidth: Optional[Union[int, List[int]]] = None
    hoverBackgroundColor: Optional[Union[Color, List[Color], str, List[str]]] = None
    hoverBorderColor: Optional[Union[Color, List[Color], str, List[str]]] = None
    hoverBorderWidth: Optional[Union[int, List[int]]] = None
    
    # 通用悬停/点击配置
    hoverOffset: Optional[int] = None
    
    def _color_to_str(self, color: Any) -> Any:
        """将颜色对象转换为字符串"""
        if color is None:
            return None
        if isinstance(color, Color):
            return str(color)
        if isinstance(color, list):
            return [str(c) if isinstance(c, Color) else c for c in color]
        return color
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为Chart.js兼容的字典"""
        result = {}
        
        # 仅添加非None值
        if self.label is not None:
            result['label'] = self.label
        if self.data is not None:
            result['data'] = self.data
        if self.order is not None:
            result['order'] = self.order
        if self.stack is not None:
            result['stack'] = self.stack
        if self.hidden is not None:
            result['hidden'] = self.hidden
        
        # 处理颜色和边框
        if self.backgroundColor is not None:
            result['backgroundColor'] = self._color_to_str(self.backgroundColor)
        if self.borderColor is not None:
            result['borderColor'] = self._color_to_str(self.borderColor)
        if self.borderWidth is not None:
            result['borderWidth'] = self.borderWidth
        
        # 仅当设置了悬停样式时才添加
        if self.hoverBackgroundColor is not None:
            result['hoverBackgroundColor'] = self._color_to_str(self.hoverBackgroundColor)
        if self.hoverBorderColor is not None:
            result['hoverBorderColor'] = self._color_to_str(self.hoverBorderColor)
        if self.hoverBorderWidth is not None:
            result['hoverBorderWidth'] = self.hoverBorderWidth
        
        # 仅当非None时添加
        if self.hoverOffset is not None:
            result['hoverOffset'] = self.hoverOffset
        
        return result

@dataclass
class LineDataset(Dataset):
    """折线图/面积图数据集"""
    # 线条特定属性
    tension: Optional[float] = None  # 0 = 直线, 1 = 平滑曲线
    fill: Optional[Union[bool, str]] = None  # 'origin', 'start', 'end', false
    stepped: Optional[bool] = None
    spanGaps: Optional[bool] = None
    cubicInterpolationMode: Optional[Literal['default', 'monotone']] = None
    
    # 点样式
    pointStyle: Optional[PointStyle] = None
    pointRadius: Optional[int] = None
    pointBackgroundColor: Optional[Union[Color, str]] = None
    pointBorderColor: Optional[Union[Color, str]] = None
    pointBorderWidth: Optional[int] = None
    pointHoverRadius: Optional[int] = None
    pointHoverBackgroundColor: Optional[Union[Color, str]] = None
    pointHoverBorderColor: Optional[Union[Color, str]] = None
    pointHoverBorderWidth: Optional[int] = None
    pointHitRadius: Optional[int] = None
    pointRotation: Optional[int] = None
    showLine: Optional[bool] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        
        # 线条特定属性
        if self.tension is not None:
            result['tension'] = self.tension
        if self.fill is not None:
            result['fill'] = self.fill
        if self.stepped is not None:
            result['stepped'] = self.stepped
        if self.spanGaps is not None:
            result['spanGaps'] = self.spanGaps
        if self.cubicInterpolationMode is not None:
            result['cubicInterpolationMode'] = self.cubicInterpolationMode
        if self.showLine is not None:
            result['showLine'] = self.showLine
        
        # 点样式
        if self.pointStyle is not None:
            result['pointStyle'] = self.pointStyle.value
        if self.pointRadius is not None:
            result['pointRadius'] = self.pointRadius
        if self.pointBackgroundColor is not None:
            result['pointBackgroundColor'] = str(self.pointBackgroundColor) if isinstance(self.pointBackgroundColor, Color) else self.pointBackgroundColor
        if self.pointBorderColor is not None:
            result['pointBorderColor'] = str(self.pointBorderColor) if isinstance(self.pointBorderColor, Color) else self.pointBorderColor
        if self.pointBorderWidth is not None:
            result['pointBorderWidth'] = self.pointBorderWidth
        if self.pointHoverRadius is not None:
            result['pointHoverRadius'] = self.pointHoverRadius
        if self.pointHoverBackgroundColor is not None:
            result['pointHoverBackgroundColor'] = str(self.pointHoverBackgroundColor) if isinstance(self.pointHoverBackgroundColor, Color) else self.pointHoverBackgroundColor
        if self.pointHoverBorderColor is not None:
            result['pointHoverBorderColor'] = str(self.pointHoverBorderColor) if isinstance(self.pointHoverBorderColor, Color) else self.pointHoverBorderColor
        if self.pointHoverBorderWidth is not None:
            result['pointHoverBorderWidth'] = self.pointHoverBorderWidth
        if self.pointHitRadius is not None:
            result['pointHitRadius'] = self.pointHitRadius
        if self.pointRotation is not None:
            result['pointRotation'] = self.pointRotation
        
        return result

@dataclass
class BarDataset(Dataset):
    """柱状图数据集"""
    barPercentage: Optional[float] = None  # 柱宽相对于类别宽度的比例
    categoryPercentage: Optional[float] = None  # 类别宽度相对于可用宽度的比例
    barThickness: Optional[Union[int, Literal['flex']]] = None  # 柱宽像素值或'flex'
    maxBarThickness: Optional[int] = None
    minBarLength: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        
        if self.barPercentage is not None:
            result['barPercentage'] = self.barPercentage
        if self.categoryPercentage is not None:
            result['categoryPercentage'] = self.categoryPercentage
        if self.barThickness is not None:
            result['barThickness'] = self.barThickness
        if self.maxBarThickness is not None:
            result['maxBarThickness'] = self.maxBarThickness
        if self.minBarLength is not None:
            result['minBarLength'] = self.minBarLength
            
        return result

@dataclass
class PieDataset(Dataset):
    """饼图/甜甜圈图数据集"""
    borderAlign: Optional[Literal['center', 'inner']] = None
    offset: Optional[Union[int, List[int]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        
        if self.borderAlign is not None:
            result['borderAlign'] = self.borderAlign
        if self.offset is not None:
            result['offset'] = self.offset
            
        return result if result else {}

@dataclass
class DoughnutDataset(PieDataset):
    """甜甜圈图数据集 (继承自PieDataset)"""
    weight: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        
        if self.weight is not None:
            result['weight'] = self.weight
            
        return result if result else {}

@dataclass
class PolarAreaDataset(Dataset):
    """极地图数据集"""
    angle: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        
        if self.angle is not None:
            result['angle'] = self.angle
            
        return result if result else {}

@dataclass
class RadarDataset(LineDataset):
    """雷达图数据集 - 基于LineDataset，因为它们在配置上有相似之处"""
    lineTension: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        
        # 雷达图特有属性
        if self.lineTension is not None:
            result['lineTension'] = self.lineTension
            
        return result if result else {}

@dataclass
class ScatterDataset(LineDataset):
    """散点图数据集 (继承自LineDataset)"""
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        return result if result else {}

# =====================
# 主Chart类
# =====================

@dataclass
class TitleConfig:
    """标题配置"""
    display: Optional[bool] = None
    text: Optional[str] = None
    color: Optional[Union[Color, str]] = None
    font: Optional[Font] = None
    padding: Optional[Union[int, Dict[str, int]]] = None
    align: Optional[TextAlign] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        
        if self.display is not None:
            result['display'] = self.display
        if self.text is not None:
            result['text'] = self.text
        if self.color is not None:
            result['color'] = str(self.color) if isinstance(self.color, Color) else self.color
        if self.font is not None:
            font_dict = self.font.to_dict()
            if font_dict:
                result['font'] = font_dict
        if self.padding is not None:
            result['padding'] = self.padding
        if self.align is not None:
            result['align'] = self.align.value
            
        return result if result else {}

@dataclass
class LegendConfig:
    """图例配置"""
    display: Optional[bool] = None
    position: Optional[Position] = None
    align: Optional[TextAlign] = None
    labels: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        
        if self.display is not None:
            result['display'] = self.display
        if self.position is not None:
            result['position'] = self.position.value
        if self.align is not None:
            result['align'] = self.align.value
        if self.labels is not None:
            result['labels'] = self.labels
            
        return result if result else {}

@dataclass
class TooltipConfig:
    """工具提示配置"""
    enabled: Optional[bool] = None
    mode: Optional[str] = None
    intersect: Optional[bool] = None
    backgroundColor: Optional[Union[Color, str]] = None
    titleColor: Optional[Union[Color, str]] = None
    bodyColor: Optional[Union[Color, str]] = None
    borderColor: Optional[Union[Color, str]] = None
    borderWidth: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        
        if self.enabled is not None:
            result['enabled'] = self.enabled
        if self.mode is not None:
            result['mode'] = self.mode
        if self.intersect is not None:
            result['intersect'] = self.intersect
        if self.backgroundColor is not None:
            result['backgroundColor'] = str(self.backgroundColor) if isinstance(self.backgroundColor, Color) else self.backgroundColor
        if self.titleColor is not None:
            result['titleColor'] = str(self.titleColor) if isinstance(self.titleColor, Color) else self.titleColor
        if self.bodyColor is not None:
            result['bodyColor'] = str(self.bodyColor) if isinstance(self.bodyColor, Color) else self.bodyColor
        if self.borderColor is not None:
            result['borderColor'] = str(self.borderColor) if isinstance(self.borderColor, Color) else self.borderColor
        if self.borderWidth is not None:
            result['borderWidth'] = self.borderWidth
            
        return result if result else {}

@dataclass
class ScaleTitle:
    """坐标轴标题配置"""
    display: Optional[bool] = None
    text: Optional[str] = None
    color: Optional[Union[Color, str]] = None
    font: Optional[Font] = None
    padding: Optional[Union[int, Dict[str, int]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        
        if self.display is not None:
            result['display'] = self.display
        if self.text is not None:
            result['text'] = self.text
        if self.color is not None:
            result['color'] = str(self.color) if isinstance(self.color, Color) else self.color
        if self.font is not None:
            font_dict = self.font.to_dict()
            if font_dict:
                result['font'] = font_dict
        if self.padding is not None:
            result['padding'] = self.padding
            
        return result if result else {}

@dataclass
class GridLine:
    """网格线配置"""
    display: Optional[bool] = None
    color: Optional[Union[Color, str, List[Union[Color, str]]]] = None
    lineWidth: Optional[Union[int, List[int]]] = None
    drawBorder: Optional[bool] = None
    drawOnChartArea: Optional[bool] = None
    drawTicks: Optional[bool] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        
        if self.display is not None:
            result['display'] = self.display
        if self.drawBorder is not None:
            result['drawBorder'] = self.drawBorder
        if self.drawOnChartArea is not None:
            result['drawOnChartArea'] = self.drawOnChartArea
        if self.drawTicks is not None:
            result['drawTicks'] = self.drawTicks
        
        if self.color is not None:
            if isinstance(self.color, list):
                result['color'] = [str(c) if isinstance(c, Color) else c for c in self.color]
            else:
                result['color'] = str(self.color) if isinstance(self.color, Color) else self.color
            
        if self.lineWidth is not None:
            result['lineWidth'] = self.lineWidth
            
        return result if result else {}

@dataclass
class AngleLine:
    """雷达图角度线配置"""
    display: Optional[bool] = None
    color: Optional[Union[Color, str]] = None
    lineWidth: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        
        if self.display is not None:
            result['display'] = self.display
        if self.color is not None:
            result['color'] = str(self.color) if isinstance(self.color, Color) else self.color
        if self.lineWidth is not None:
            result['lineWidth'] = self.lineWidth
            
        return result if result else {}

@dataclass
class PointLabel:
    """雷达图点标签配置"""
    font: Optional[Font] = None
    color: Optional[Union[Color, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        
        if self.font is not None:
            font_dict = self.font.to_dict()
            if font_dict:
                result['font'] = font_dict
        if self.color is not None:
            result['color'] = str(self.color) if isinstance(self.color, Color) else self.color
            
        return result if result else {}

@dataclass
class RadialLinearScale:
    """雷达图径向线性坐标轴配置"""
    angleLines: Optional[AngleLine] = None
    grid: Optional[GridLine] = None
    pointLabels: Optional[PointLabel] = None
    suggestedMin: Optional[float] = None
    suggestedMax: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    ticks: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        
        if self.angleLines is not None:
            angle_lines = self.angleLines.to_dict()
            if angle_lines:
                result['angleLines'] = angle_lines
                
        if self.grid is not None:
            grid = self.grid.to_dict()
            if grid:
                result['grid'] = grid
                
        if self.pointLabels is not None:
            point_labels = self.pointLabels.to_dict()
            if point_labels:
                result['pointLabels'] = point_labels
                
        if self.suggestedMin is not None:
            result['suggestedMin'] = self.suggestedMin
        if self.suggestedMax is not None:
            result['suggestedMax'] = self.suggestedMax
        if self.min is not None:
            result['min'] = self.min
        if self.max is not None:
            result['max'] = self.max
        if self.ticks is not None:
            result['ticks'] = self.ticks
            
        return result if result else {}

@dataclass
class ScaleConfig:
    """坐标轴配置"""
    type: Optional[ScaleType] = None
    display: Optional[bool] = None
    position: Optional[Position] = None
    title: Optional[ScaleTitle] = None
    grid: Optional[GridLine] = None
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    stacked: Optional[bool] = None
    reverse: Optional[bool] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        
        if self.type is not None:
            result['type'] = self.type.value
        if self.display is not None:
            result['display'] = self.display
        if self.position is not None:
            result['position'] = self.position.value
        if self.title is not None:
            title_dict = self.title.to_dict()
            if title_dict:
                result['title'] = title_dict
        if self.grid is not None:
            grid_dict = self.grid.to_dict()
            if grid_dict:
                result['grid'] = grid_dict
        if self.min is not None:
            result['min'] = self.min
        if self.max is not None:
            result['max'] = self.max
        if self.stacked is not None:
            result['stacked'] = self.stacked
        if self.reverse is not None:
            result['reverse'] = self.reverse
            
        return result if result else {}

@dataclass
class AnimationConfig:
    """动画配置"""
    duration: Optional[int] = None
    easing: Optional[Easing] = None
    delay: Optional[int] = None
    loop: Optional[bool] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        
        if self.duration is not None:
            result['duration'] = self.duration
        if self.easing is not None:
            result['easing'] = self.easing.value
        if self.delay is not None:
            result['delay'] = self.delay
        if self.loop is not None:
            result['loop'] = self.loop
            
        return result if result else {}

class ChartJS:
    """Chart.js配置生成器 - 完全面向对象"""
    
    def __init__(self, chart_type: ChartType = ChartType.BAR):
        self.type: ChartType = chart_type
        self.labels: Optional[List[str]] = None
        self.datasets: List[Dataset] = []
        self.title: Optional[TitleConfig] = None
        self.legend: Optional[LegendConfig] = None
        self.tooltip: Optional[TooltipConfig] = None
        self.scales: Dict[str, Any] = {}
        self.animation: Optional[AnimationConfig] = None
        self.responsive: Optional[bool] = None
        self.maintain_aspect_ratio: Optional[bool] = None
        self.plugins: List[str] = []
    
    def set_labels(self, labels: List[str]) -> 'ChartJS':
        """设置数据标签 (X轴)"""
        self.labels = labels
        return self
    
    def add_dataset(self, dataset: Dataset) -> 'ChartJS':
        """添加数据集"""
        self.datasets.append(dataset)
        return self
    
    @overload
    def create_dataset(self, chart_type: Literal[ChartType.LINE]) -> LineDataset: ...
    @overload
    def create_dataset(self, chart_type: Literal[ChartType.BAR]) -> BarDataset: ...
    @overload
    def create_dataset(self, chart_type: Literal[ChartType.PIE]) -> PieDataset: ...
    @overload
    def create_dataset(self, chart_type: Literal[ChartType.DOUGHNUT]) -> DoughnutDataset: ...
    @overload
    def create_dataset(self, chart_type: Literal[ChartType.POLAR_AREA]) -> PolarAreaDataset: ...
    @overload
    def create_dataset(self, chart_type: Literal[ChartType.RADAR]) -> RadarDataset: ...
    @overload
    def create_dataset(self, chart_type: Literal[ChartType.SCATTER]) -> ScatterDataset: ...
    
    def create_dataset(self, chart_type: Optional[ChartType] = None) -> Dataset:
        """
        创建特定类型的数据集实例
        
        Args:
            chart_type: 图表类型，如果为None则使用图表的主类型
            
        Returns:
            对应图表类型的数据集实例
        """
        chart_type = chart_type or self.type
        
        dataset_map = {
            ChartType.LINE: LineDataset(),
            ChartType.BAR: BarDataset(),
            ChartType.PIE: PieDataset(),
            ChartType.DOUGHNUT: DoughnutDataset(),
            ChartType.POLAR_AREA: PolarAreaDataset(),
            ChartType.RADAR: RadarDataset(),
            ChartType.SCATTER: ScatterDataset()
        }
        
        return dataset_map.get(chart_type, Dataset())
    
    def set_title(self, text: str, **kwargs) -> 'ChartJS':
        """设置图表标题"""
        if self.title is None:
            self.title = TitleConfig()
        
        self.title.text = text
        self.title.display = True
        
        # 应用额外参数
        for key, value in kwargs.items():
            if hasattr(self.title, key):
                setattr(self.title, key, value)
        
        return self
    
    def set_radial_scale(self, scale_config: RadialLinearScale) -> 'ChartJS':
        """配置雷达图的径向坐标轴"""
        scale_dict = scale_config.to_dict()
        if scale_dict:
            self.scales['r'] = scale_dict

        return self
    
    def set_scales(self, x_scale: Optional[ScaleConfig] = None,
                  y_scale: Optional[ScaleConfig] = None) -> 'ChartJS':
        """配置坐标轴"""
        if x_scale:
            scale_dict = x_scale.to_dict()
            if scale_dict:
                if 'x' not in self.scales:
                    self.scales['x'] = {}
                self.scales['x'].update(scale_dict)

        if y_scale:
            scale_dict = y_scale.to_dict()
            if scale_dict:
                if 'y' not in self.scales:
                    self.scales['y'] = {}
                self.scales['y'].update(scale_dict)

        return self
    
    def set_legend(self, display: bool = True, position: Position = Position.TOP, 
                  **kwargs) -> 'ChartJS':
        """配置图例"""
        if self.legend is None:
            self.legend = LegendConfig()
        
        self.legend.display = display
        self.legend.position = position
        
        # 应用额外参数
        for key, value in kwargs.items():
            if hasattr(self.legend, key):
                setattr(self.legend, key, value)
        
        return self
    
    def set_tooltip(self, enabled: bool = True, **kwargs) -> 'ChartJS':
        """配置工具提示"""
        if self.tooltip is None:
            self.tooltip = TooltipConfig()
        
        self.tooltip.enabled = enabled
        
        # 应用额外参数
        for key, value in kwargs.items():
            if hasattr(self.tooltip, key):
                setattr(self.tooltip, key, value)
        
        return self
    
    def set_responsive(self, responsive: bool = True, 
                      maintain_aspect_ratio: bool = True) -> 'ChartJS':
        """设置响应式"""
        self.responsive = responsive
        self.maintain_aspect_ratio = maintain_aspect_ratio
        return self
    
    def set_animation(self, duration: int = 1000, easing: Easing = Easing.EASE_OUT_QUART, 
                     **kwargs) -> 'ChartJS':
        """配置动画"""
        if self.animation is None:
            self.animation = AnimationConfig()
        
        self.animation.duration = duration
        self.animation.easing = easing
        
        # 应用额外参数
        for key, value in kwargs.items():
            if hasattr(self.animation, key):
                setattr(self.animation, key, value)
        
        return self
    
    def add_plugin(self, plugin_name: str) -> 'ChartJS':
        """注册额外插件"""
        if plugin_name not in self.plugins:
            self.plugins.append(plugin_name)
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为Chart.js标准配置字典"""
        config: Dict[str, Any] = {
            'type': self.type.value,
        }
        
        # 数据部分
        data: Dict[str, Any] = {}
        if self.labels is not None:
            data['labels'] = self.labels
        if self.datasets:
            data['datasets'] = [dataset.to_dict() for dataset in self.datasets]
        
        if data:
            config['data'] = data
        
        # 选项部分
        options: Dict[str, Any] = {}
        
        # 响应式配置
        if self.responsive is not None:
            options['responsive'] = self.responsive
        if self.maintain_aspect_ratio is not None:
            options['maintainAspectRatio'] = self.maintain_aspect_ratio
            
        # 动画配置
        if self.animation is not None:
            animation_dict = self.animation.to_dict()
            if animation_dict:
                options['animation'] = animation_dict
        
        # 插件配置
        plugins: Dict[str, Any] = {}
        if self.title is not None:
            title_dict = self.title.to_dict()
            if title_dict:
                plugins['title'] = title_dict
        if self.legend is not None:
            legend_dict = self.legend.to_dict()
            if legend_dict:
                plugins['legend'] = legend_dict
        if self.tooltip is not None:
            tooltip_dict = self.tooltip.to_dict()
            if tooltip_dict:
                plugins['tooltip'] = tooltip_dict
                
        if plugins:
            if 'plugins' not in options:
                options['plugins'] = {}
            options['plugins'].update(plugins)
        
        # 坐标轴配置
        if self.scales:
            options['scales'] = self.scales
        
        if options:
            config['options'] = options
            
        # 插件
        if self.plugins:
            config['plugins'] = self.plugins
            
        return config
    
    def to_json(self, indent: Optional[int] = 2, **kwargs) -> str:
        """序列化为JSON字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, **kwargs)
    
    def __str__(self) -> str:
        return f"ChartJS(type={self.type.value}, datasets={len(self.datasets)})"

# =====================
# 使用示例
# =====================

if __name__ == "__main__":
    # 创建一个雷达图
    chart = ChartJS(ChartType.RADAR)
    
    # 创建并配置第一个数据集
    dataset1 = chart.create_dataset(ChartType.RADAR)
    dataset1.label = "My First Dataset"
    dataset1.data = [65, 59, 90, 81, 56, 55, 40]
    dataset1.fill = True
    dataset1.backgroundColor = "rgba(255, 99, 132, 0.2)"
    dataset1.borderColor = "rgb(255, 99, 132)"
    dataset1.pointBackgroundColor = "rgb(255, 99, 132)"
    dataset1.pointBorderColor = "#fff"
    dataset1.pointHoverBackgroundColor = "#fff"
    dataset1.pointHoverBorderColor = "rgb(255, 99, 132)"
    dataset1.borderWidth = 2
    chart.add_dataset(dataset1)
    
    # 创建并配置第二个数据集
    dataset2 = chart.create_dataset(ChartType.RADAR)
    dataset2.label = "My Second Dataset"
    dataset2.data = [28, 48, 40, 19, 96, 27, 100]
    dataset2.fill = True
    dataset2.backgroundColor = "rgba(54, 162, 235, 0.2)"
    dataset2.borderColor = "rgb(54, 162, 235)"
    dataset2.pointBackgroundColor = "rgb(54, 162, 235)"
    dataset2.pointBorderColor = "#fff"
    dataset2.pointHoverBackgroundColor = "#fff"
    dataset2.pointHoverBorderColor = "rgb(54, 162, 235)"
    dataset2.borderWidth = 2
    chart.add_dataset(dataset2)
    
    # 设置标签
    chart.set_labels(['Eating', 'Drinking', 'Sleeping', 'Designing', 'Coding', 'Cycling', 'Running'])
    
    # 配置径向坐标轴
    radial_scale = RadialLinearScale(
        angleLines=AngleLine(
            display=True,
        ),
        suggestedMin=0,
        suggestedMax=100
    )
    chart.set_radial_scale(radial_scale)
    
    # 配置标题
    chart.set_title("My Radar Chart", 
                   color="#333",
                   font=Font(size=18, weight='bold'))
    
    # 配置图例
    chart.set_legend(position=Position.TOP)
    
    # 配置响应式
    chart.set_responsive(True, True)
    
    # 输出配置
    print("Chart.js雷达图配置:")
    print(chart.to_json())
    
    # 验证配置
    config = chart.to_dict()
    print(f"\n验证: 图表类型 = {config['type']}")
    print(f"标签数量 = {len(config['data']['labels'])}")
    print(f"数据集数量 = {len(config['data']['datasets'])}")