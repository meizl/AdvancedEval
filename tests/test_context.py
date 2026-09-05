"""context.py 的测试。"""

from advancedeval.context import get_current_span, use_span
from advancedeval.models import Span


def test_默认没有当前span():
    assert get_current_span() is None


def test_进入后读到当前span():
    s = Span(name="outer")
    with use_span(s):
        assert get_current_span() is s


def test_嵌套时内层覆盖外层_退出后恢复外层():
    outer = Span(name="outer")
    inner = Span(name="inner")
    with use_span(outer):
        with use_span(inner):
            assert get_current_span() is inner
        assert get_current_span() is outer


def test_全部退出后恢复None():
    s = Span(name="x")
    with use_span(s):
        pass
    assert get_current_span() is None


def test_发生异常也会自动恢复():
    s = Span(name="x")
    try:
        with use_span(s):
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    # 即使块里抛了异常，finally 里的 reset 也会执行，当前 span 应恢复为 None
    assert get_current_span() is None
