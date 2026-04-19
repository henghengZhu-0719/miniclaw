from pathlib import Path

MAX_CHARS = 20000


class PromptBuilder:
    """
    负责组装 System Prompt

    拼接顺序：
      ① SKILLS_SNAPSHOT.md
      ② workspace/SOUL.md
      ③ workspace/IDENTITY.md
      ④ workspace/USER.md
      ⑤ workspace/AGENTS.md
      ⑥ memory/MEMORY.md（RAG 模式下跳过）
    """

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)

    # =========================
    # 内部工具
    # =========================

    def _read_file(self, path: Path) -> str:
        """
        读取文件内容，并限制最大长度
        """
        if not path.exists():
            return f"[missing file: {path.name}]"

        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return f"[error reading file: {path.name}]"

        if len(text) > MAX_CHARS:
            return text[:MAX_CHARS] + "\n...[truncated]"

        return text

    def _section(self, title: str, content: str) -> str:
        """
        包装成 Markdown section
        """
        return f"# {title}\n\n{content.strip()}"

    # =========================
    # 主入口
    # =========================

    def build(self, rag_enabled: bool = False) -> str:
        """
        构建完整 System Prompt
        """

        parts = []

        # ① SKILLS
        parts.append(
            self._section(
                "SKILLS_SNAPSHOT",
                self._read_file(self.base_dir / "skills" / "SKILLS_SNAPSHOT.md"),
            )
        )

        # ② SOUL
        parts.append(
            self._section(
                "SOUL",
                self._read_file(self.base_dir / "workspace" / "SOUL.md"),
            )
        )

        # ③ IDENTITY
        parts.append(
            self._section(
                "IDENTITY",
                self._read_file(self.base_dir / "workspace" / "IDENTITY.md"),
            )
        )

        # ④ USER
        parts.append(
            self._section(
                "USER",
                self._read_file(self.base_dir / "workspace" / "USER.md"),
            )
        )

        # ⑤ AGENTS
        parts.append(
            self._section(
                "AGENTS",
                self._read_file(self.base_dir / "workspace" / "AGENTS.md"),
            )
        )

        # ⑥ MEMORY / RAG
        if rag_enabled:
            parts.append(
                self._section(
                    "MEMORY_ACCESS",
                    (
                        "长期记忆不会直接包含在 System Prompt 中。\n"
                        "系统会在每次对话前，通过语义检索动态注入相关记忆。\n\n"
                        "请在回答时优先参考这些被注入的记忆片段，"
                        "但不要假设所有历史都已提供。"
                    ),
                )
            )
        else:
            parts.append(
                self._section(
                    "MEMORY",
                    self._read_file(self.base_dir / "memory" / "MEMORY.md"),
                )
            )

        # 拼接
        return "\n\n---\n\n".join(parts)