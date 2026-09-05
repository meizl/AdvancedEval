"""Tracer 记录器：把「创建 span + 记父子 + 记时间」封装进 start_span，并自动组织成 Trace。"""

import time
from contextlib import contextmanager

from .context import get_current_span, use_span
from .models import Span, Trace


class Tracer:
    def __init__(self):
        self.traces = []       # 所有链路（Trace）
        self.spans = []        # 所有步骤（Span，平铺，方便查看）
        self._trace_map = {}   # trace_id -> Trace，用于把 span 归到对应链路

    @contextmanager
    def start_span(self, name):
        """开始一个步骤。用法：

            with tracer.start_span("研究") as span:
                ...
        """
        # ① 看当前在哪个 span 里 → 那就是爹
        parent = get_current_span()

        # ② 创建 span，确定父子关系和归属链路
        span = Span(name=name)
        if parent is not None:
            # 子步骤：爹是 parent，和爹在同一条链上
            span.parent_id = parent.span_id
            span.trace_id = parent.trace_id
        else:
            # 根步骤：没有爹，开一条新链路（Trace）
            trace = Trace(name=name)          # 链路名字默认 = 根步骤的名字
            span.trace_id = trace.trace_id
            self.traces.append(trace)
            self._trace_map[trace.trace_id] = trace

        # ③ 记开始时间，并把 span 设为「当前」
        span.start_time = time.perf_counter()
        with use_span(span):
            try:
                yield span  # 把 span 交给外面，with 块里随便用
            finally:
                # ④ 退出时自动：记结束时间 + 归到对应链路
                span.end_time = time.perf_counter()
                self.spans.append(span)
                trace = self._trace_map.get(span.trace_id)
                if trace is not None:
                    trace.add_span(span)
