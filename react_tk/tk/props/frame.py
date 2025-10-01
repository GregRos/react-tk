from react_tk.renderable.node.shadow_node import NodeProps
from react_tk.tk.props.background import BackgroundProps
from react_tk.tk.props.border import BorderProps
from react_tk.tk.props.width_height import WidthHeightProps


class FrameProps(NodeProps, WidthHeightProps, BorderProps, BackgroundProps):
    pass
