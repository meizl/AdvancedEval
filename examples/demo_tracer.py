"""演示 Tracer 怎么用：对比之前手动写，现在 with 一行搞定，父子关系自动对。

运行方式（在项目根目录）：
    PYTHONPATH=. python3 examples/demo_tracer.py
"""

from advancedeval.tracer import Tracer

tracer = Tracer()

# 之前要手动 new Span、手动记 parent_id；现在一个 with 全搞定
with tracer.start_span("研究") as 研究:
    with tracer.start_span("调LLM") as 调LLM:
        with tracer.start_span("查数据库") as 查库:
            pass  # 这里就是真正干活的代码

# 验证父子关系（自动记对没有）
print("查库 的爹是 调LLM 吗？", 查库.parent_id == 调LLM.span_id)
print("调LLM 的爹是 研究 吗？", 调LLM.parent_id == 研究.span_id)
print()

# 打印记录到的所有步骤
for span in tracer.spans:
    print(f"步骤【{span.name}】 耗时 {round(span.duration, 5)} 秒")
