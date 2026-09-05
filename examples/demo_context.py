"""演示 context.py 怎么用：模拟 agent 三个步骤，看父子关系如何自动记对。

运行方式（在项目根目录）：
    PYTHONPATH=. python3 examples/demo_context.py
"""

from advancedeval.context import use_span, get_current_span
from advancedeval.models import Span


# 第一步：研究（最外层）
研究 = Span(name="研究")

with use_sxpan(研究):
    print("当前在：", get_current_span().name)

    # 第二步：调 LLM
    调LLM = Span(name="调LLM")
    调LLM.parent_id = get_current_span().span_id  # 当前是谁，谁就是爹
    with use_span(调LLM):
        print("  当前在：", get_current_span().name)

        # 第三步：查数据库
        查库 = Span(name="查数据库")
        查库.parent_id = get_current_span().span_id
        with use_span(查库):
            print("    当前在：", get_current_span().name)
        print("  退出后当前在：", get_current_span().name)

    print("退出后当前在：", get_current_span().name)

print("全部退出后当前在：", get_current_span())

# 验证父子关系记对没有
print()
print("查库 的爹是 调LLM 吗？", 查库.parent_id == 调LLM.span_id)
print("调LLM 的爹是 研究 吗？", 调LLM.parent_id == 研究.span_id)
