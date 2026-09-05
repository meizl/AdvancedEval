"""Tracer 记录器：把「创建 span + 记父子 + 记时间」封装进 start_span。"""

import time
from contextlib import contextmanager

from .context import get_current_span, use_span
from .models import Span


class Tracer:
    def __init__(self):
        self.spans = []  # 先简单用列表存所有 span，后面换成存储插件

    @contextmanager
    def start_span(self, name):
        """开始一个步骤。用法：

            with tracer.start_span("研究") as span:
                ...
        """
        # ① 看当前在哪个 span 里 → 那就是爹
        parent = get_current_span()

        # ② 创建 span，填上爹
        span = Span(name=name)
        if parent is not None:
            span.parent_id = parent.span_id
            span.trace_id = parent.trace_id  # 和爹在同一条链上

        # ③ 记开始时间，并把这个 span 设为「当前」
        span.start_time = time.perf_counter()
        with use_span(span):            
            try:
                yield span  # 把 span 交给外面，with 块里随便用
            finally:
                # ④ 退出时自动：记结束时间 + 存起来
                span.end_time = time.perf_counter()
                self.spans.append(span)
