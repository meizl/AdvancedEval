"""数据模型：Span、Trace（纯数据结构，谁也不依赖）。"""

from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import uuid4


@dataclass
class Span:
    # ---- 必填 ----
    name: str  # 这一步叫什么，如 "llm_call"

    # ---- 标识（后面串成一条链时用，现在先不管）----
    span_id: str = field(default_factory=lambda: uuid4().hex)  # 自己的唯一 ID
    trace_id: Optional[str] = None  # 归属哪条 trace（同一条 trace 的 span 共享）
    parent_id: Optional[str] = None  # 父 span 的 ID（None 表示根节点）

    # ---- 输入输出 ----
    input: Any = None  # 这一步的输入
    output: Any = None  # 这一步的输出

    # ---- 时间 ----
    start_time: Optional[float] = None  # 开始时间（time.perf_counter()）
    end_time: Optional[float] = None  # 结束时间（time.perf_counter()）

    # ---- 类型与状态 ----
    kind: str = "span"  # span 类型：llm / tool / chain / span
    status: str = "ok"  # ok / error
    error: Optional[str] = None  # 出错时的异常信息

    # ---- 元数据与事件（后面做流式/统计时用）----
    attributes: dict = field(default_factory=dict)  # 任意键值：model、tokens 等
    events: list = field(default_factory=list)  # 内部带时间戳的小事件

    @property
    def duration(self) -> Optional[float]:
        """耗时（秒）；还没结束时返回 None。"""
        if self.start_time is None or self.end_time is None:
            return None
        return self.end_time - self.start_time


@dataclass
class Trace:
    """一次完整请求的整条链路，包含多个 Span。"""

    trace_id: str = field(default_factory=lambda: uuid4().hex)
    name: Optional[str] = None
    spans: list = field(default_factory=list)  # 这条链包含的所有 span（平铺存放）
    attributes: dict = field(default_factory=dict)

    def add_span(self, span: Span) -> None:
        """加入一个 span，并把它的 trace_id 回填成本 trace 的 ID。"""
        span.trace_id = self.trace_id
        self.spans.append(span)

    def get_span(self, span_id: str) -> Optional[Span]:
        """按 span_id 查找 span；找不到返回 None。"""
        for span in self.spans:
            if span.span_id == span_id:
                return span
        return None

    @property
    def duration(self) -> Optional[float]:
        """整条链的耗时：最晚结束 - 最早开始。"""
        starts = [s.start_time for s in self.spans if s.start_time is not None]
        ends = [s.end_time for s in self.spans if s.end_time is not None]
        if not starts or not ends:
            return None
        return max(ends) - min(starts)
