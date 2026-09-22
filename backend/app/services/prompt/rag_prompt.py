"""RAG Prompt 模板。

核心要求：
- 必须基于【参考资料】回答
- 不允许编造
- 必须引用来源编号
- 无依据时明确拒答
- 支持多轮历史
"""

from typing import List

from app.models.document import SearchResult
from app.models.session import Message


SYSTEM_PROMPT = """你是一个严谨的企业知识库问答助手。

回答规则：
1. 必须严格基于【参考资料】回答，不得编造。
2. 如果【参考资料】中没有相关信息，必须回答："未在知识库中找到相关依据，无法回答该问题。"
3. 回答时引用资料编号，例如 [资料1]、[资料2]。
4. 使用简洁、结构化的中文回答。
5. 不要输出与问题无关的内容。
6. 可以结合【对话历史】理解上下文，但回答必须以【参考资料】为准。
"""


def build_user_prompt(
    query: str,
    contexts: List[SearchResult],
    history: List[Message] | None = None,
) -> str:
    """构建用户 Prompt，支持多轮历史。"""
    # 参考资料
    if not contexts:
        ref_block = "无"
    else:
        lines = []
        for i, ctx in enumerate(contexts, start=1):
            lines.append(f"[资料{i}] 来源：{ctx.title}\n{ctx.content}")
        ref_block = "\n\n".join(lines)

    # 历史
    history_block = "无"
    if history:
        h_lines = []
        for msg in history:
            role = "用户" if msg.role == "user" else "助手"
            h_lines.append(f"{role}：{msg.content}")
        if h_lines:
            history_block = "\n".join(h_lines)

    return f"""【对话历史】
{history_block}

【参考资料】
{ref_block}

【问题】
{query}

【回答】"""