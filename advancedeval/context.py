"""上下文传播：用 contextvars 维护当前 span。"""

import contextvars
from contextlib import contextmanager
from typing import Optional

from .models import Span

# 「当前 span」的槽位：每个线程/协程各有一份，互不干扰。
_current_span = contextvars.ContextVar("current_span", default=None)
#


#读当前的步骤
def get_current_span() -> Optional[Span]:
    """返回当前上下文里的 span；不在任何 span 里时返回 None。"""
    return _current_span.get()



#改牌子+恢复步骤
@contextmanager
def use_span(span: Span):
    """进入一个 span：把它设为「当前 span」，退出时自动恢复成上一个。

    用法：
        with use_span(span):
            ...  # 这里面的代码，get_current_span() 会返回这个 span
    """
    token = _current_span.set(span)
    try:
        yield
    finally:
        _current_span.reset(token)
