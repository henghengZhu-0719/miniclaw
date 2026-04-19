
```text
架构

mini-OpenClaw/
├── backend/
│   ├── app.py                       # FastAPI 入口，路由注册，启动初始化
│   ├── config.py                    # 全局配置管理（config.json 持久化）
│   ├── requirements.txt             # Python 依赖
│   ├── .env.example                 # 环境变量模板
│   │
│   ├── api/                         # API 路由层
│   │   ├── chat.py                  # POST /api/chat — SSE 流式对话
│   │   ├── sessions.py              # 会话 CRUD + 标题生成
│   │   ├── files.py                 # 文件读写 + 技能列表
│   │   ├── tokens.py                # Token 统计
│   │   ├── compress.py              # 对话压缩
│   │   └── config_api.py            # RAG 模式开关
│   │
│   ├── graph/                       # Agent 核心逻辑
│   │   ├── agent.py                 # AgentManager：构建与流式调用
│   │   ├── session_manager.py       # 会话持久化（JSON 文件）
│   │   ├── prompt_builder.py        # System Prompt 组装器
│   │   └── memory_indexer.py        # MEMORY.md 向量索引（RAG）
│   │
│   ├── tools/                       # 5 个核心工具
│   │   ├── __init__.py              # 工具注册工厂
│   │   ├── terminal_tool.py         # 沙箱终端
│   │   ├── python_repl_tool.py      # Python 解释器
│   │   ├── fetch_url_tool.py        # 网页抓取（HTML → Markdown）
│   │   ├── read_file_tool.py        # 沙箱文件读取
│   │   ├── search_knowledge_tool.py # 知识库搜索
│   │   └── skills_scanner.py        # 技能目录扫描器
│   │
│   ├── workspace/                   # System Prompt 组件
│   │   ├── SOUL.md                  # 人格、语气、边界
│   │   ├── IDENTITY.md              # 名称、风格、Emoji
│   │   ├── USER.md                  # 用户画像
│   │   └── AGENTS.md                # 操作指南 & 记忆/技能协议
│   │
│   ├── skills/                      # 技能目录（每个技能一个子目录）
│   │   └── get_weather/
│   │       └── SKILL.md             # 示例：天气查询技能
│   │
│   ├── memory/
│   │   └── MEMORY.md                # 跨会话长期记忆
│   │
│   ├── knowledge/                   # 知识库文档（供 RAG 检索）
│   ├── sessions/                    # 会话 JSON 文件
│   │   └── archive/                 # 压缩归档
│   ├── storage/                     # LlamaIndex 持久化索引
│   │   └── memory_index/            # MEMORY.md 专用索引
│   └── SKILLS_SNAPSHOT.md           # 技能快照（启动时自动生成）
│
└── frontend/
    └── src/
        ├── app/
        │   ├── layout.tsx           # Next.js 根布局
        │   ├── page.tsx             # 主页面（三栏布局）
        │   └── globals.css          # 全局样式
        ├── lib/
        │   ├── store.tsx            # React Context 状态管理
        │   └── api.ts               # 后端 API 客户端
        └── components/
            ├── chat/
            │   ├── ChatPanel.tsx     # 聊天面板（消息列表 + 输入框）
            │   ├── ChatMessage.tsx   # 消息气泡（Markdown 渲染）
            │   ├── ChatInput.tsx     # 输入框
            │   ├── ThoughtChain.tsx  # 工具调用思维链（可折叠）
            │   └── RetrievalCard.tsx # RAG 检索结果卡片
            ├── layout/
            │   ├── Navbar.tsx        # 顶部导航栏
            │   ├── Sidebar.tsx       # 左侧边栏（会话列表 + Raw Messages）
            │   └── ResizeHandle.tsx  # 面板拖拽分隔条
            └── editor/
                └── InspectorPanel.tsx # 右侧检查器（Monaco 编辑器）
```
