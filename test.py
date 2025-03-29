import time

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

console = Console()
raw_buffer = []
final_md = None

# 第一个Live显示原始文本
with Live(console=console, transient=True) as preliminary_live:
    # 模拟流式接收
    for chunk in ["# 标题\n", "```python\nprint('Hello')\n```\n", "正文内容"]:
        raw_buffer.append(chunk)
        preliminary_live.update("".join(raw_buffer))
        time.sleep(1)

    final_md = Markdown("".join(raw_buffer))

# 第二个Live覆盖显示
with Live(auto_refresh=False) as final_live:
    final_live.update(final_md)
    final_live.refresh()
