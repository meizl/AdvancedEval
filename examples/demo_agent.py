"""演示：一个 agent 怎么用现在的 AdvancedEval 追踪执行过程。

运行方式（在项目根目录）：
    PYTHONPATH=. python3 examples/demo_agent.py
"""

import time

from advancedeval.tracer import Tracer

# ① 创建一个记录器
tracer = Tracer()


# ② 你的 agent 代码：每个步骤用 with 包起来
def 调大模型(提示):
    with tracer.start_span("调大模型"):
        time.sleep(0.1)          # 假装在调大模型，花 0.1 秒
        return "大模型的结果"


def 查数据库(查询):
    with tracer.start_span("查数据库"):
        time.sleep(0.05)         # 假装查库，花 0.05 秒
        return "数据库的结果"


def 查天气(城市):
    with tracer.start_span("查天气"):
        结果1 = 调大模型(f"分析{城市}")   # 嵌套调用 → 自动成为「查天气」的子步骤
        结果2 = 查数据库(结果1)
        return 结果2


# ③ 运行 agent
查天气("北京")

# ④ 查看记录下来的轨迹
print("记录到的所有步骤：")
for span in tracer.spans:
    print(f"  步骤【{span.name}】 耗时 {span.duration:.3f} 秒")
