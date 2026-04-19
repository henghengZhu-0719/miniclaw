"""
save_message：把每句对话记进工单
load_session：把完整工单拿出来看
compress_history：把老内容归档并写摘要
load_session_for_agent：给当前Agent一份“摘要 + 最近对话”的精简版
"""


import json
from pathlib import Path
from datetime import datetime
from typing import Any, Optional


class SessionManager:
    """
    负责会话历史的 JSON 持久化

    sessions/
        active/
            <session_id>.json
            <session_id>.summary.txt
        archive/
    """

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.sessions_dir = self.base_dir / "sessions" / "active"
        self.archive_dir = self.base_dir / "sessions" / "archive"

        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def _session_path(self, session_id: str) -> Path:
        """
        获取会话 JSON 文件路径
        """
        return self.sessions_dir / f"{session_id}.json"

    def _summary_path(self, session_id: str) -> Path:
        """
        获取会话摘要文件路径
        """
        return self.sessions_dir / f"{session_id}.summary.txt"

    # CRUD
    def load_session(self, session_id: str) -> list[dict]:
        """
        返回原始消息数组，不做任何合并和注入。
        如果文件不存在，返回 []。
        """
        path = self._session_path(session_id)
        if not path.exists():
            return []

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
            return []
        except Exception:
            return []

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: Optional[list[dict[str, Any]]] = None,
    ) -> dict:
        """
        追加一条消息到会话 JSON 文件。
        返回追加后的 message dict。
        """
        messages = self.load_session(session_id)

        message = {
            "role": role,
            "content": content,
            "tool_calls": tool_calls or [],
            "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }

        messages.append(message)

        path = self._session_path(session_id)
        path.write_text(
            json.dumps(messages, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return message

    def get_compressed_context(self, session_id: str) -> str:
        """
        读取压缩摘要文本。
        如果文件不存在，返回空字符串。
        """
        path = self._summary_path(session_id)
        if not path.exists():
            return ""

        try:
            return path.read_text(encoding="utf-8").strip()
        except Exception:
            return ""

    def load_session_for_agent(self, session_id: str) -> list[dict]:
        """
        返回适合给 LLM 的消息列表：
        1. 合并连续 assistant 消息
        2. 如果存在 compressed_context，则在最前面插入一条虚拟 assistant 消息
        """
        raw_messages = self.load_session(session_id)
        merged_messages: list[dict] = []

        for msg in raw_messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if not role:
                continue

            normalized = {
                "role": role,
                "content": content,
            }

            if not merged_messages:
                merged_messages.append(normalized)
                continue

            prev = merged_messages[-1]

            if prev["role"] == "assistant" and role == "assistant":
                prev_content = prev.get("content", "").rstrip()
                curr_content = content.lstrip()
                prev["content"] = f"{prev_content}\n\n{curr_content}".strip()
            else:
                merged_messages.append(normalized)

        compressed_context = self.get_compressed_context(session_id)
        if compressed_context:
            merged_messages.insert(
                0,
                {
                    "role": "assistant",
                    "content": (
                        "以下是此前对话的压缩摘要，请在理解当前问题时一并参考：\n\n"
                        f"{compressed_context}"
                    ),
                },
            )

        return merged_messages
    
    def compress_history(self, session_id: str, summary: str, n: int) -> None:
        """
        将当前会话前 n 条消息归档，并把摘要写入 compressed_context。

        行为：
        1. 前 n 条消息追加写入 archive 文件
        2. summary 追加写入 <session_id>.summary.txt
        3. active 会话中删除前 n 条消息
        """
        messages = self.load_session(session_id)

        if n <= 0 or not messages:
            return

        n = min(n, len(messages))
        archived = messages[:n]
        remaining = messages[n:]

        # 1) 归档原始消息到 archive jsonl
        archive_path = self.archive_dir / f"{session_id}.jsonl"
        with archive_path.open("a", encoding="utf-8") as f:
            for msg in archived:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")

        # 2) 追加摘要到 summary 文件
        summary_path = self._summary_path(session_id)
        old_summary = ""
        if summary_path.exists():
            try:
                old_summary = summary_path.read_text(encoding="utf-8").strip()
            except Exception:
                old_summary = ""

        new_summary = summary.strip()
        if old_summary and new_summary:
            merged_summary = f"{old_summary}\n---\n{new_summary}"
        else:
            merged_summary = old_summary or new_summary

        summary_path.write_text(merged_summary, encoding="utf-8")

        # 3) 回写剩余 active 消息
        session_path = self._session_path(session_id)
        session_path.write_text(
            json.dumps(remaining, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


if __name__ == "__main__":
    sm = SessionManager("./demo_data")

    session_id = "s1"

    sm.save_message(session_id, "user", "你好")
    sm.save_message(session_id, "assistant", "你好，我在。")
    sm.save_message(session_id, "assistant", "请问要我做什么？")
    sm.save_message(session_id, "user", "帮我总结一下 SessionManager。")

    print("=== load_session ===")
    print(sm.load_session(session_id))

    print("\n=== load_session_for_agent ===")
    print(sm.load_session_for_agent(session_id))