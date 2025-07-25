```markdown
# 🔌 CircuitBreaker-Sizer · 西门子断路器智能选型助手

[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-orange)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)

基于自然语言大模型（LLM）驱动的 3WA 系列断路器选型助手，支持通过中文需求智能生成产品序列号、匹配脱扣器、订货号与技术参数，提升工业电气工程效率。

---

## 🧭 目录

- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [功能介绍](#功能介绍)
- [模型配置](#模型配置)
- [数据要求](#数据要求)
- [展示截图](#展示截图)
- [开发计划](#开发计划)
- [许可证](#许可证)
- [维护者](#维护者)

---

## 📦 项目结构

```

circuitBreaker-Sizer/
├── config/                  # 配置文件
├── data/                    # 参数表、订货号等数据
├── logs/                    # 聊天与结构化日志
├── utils/                   # 所有核心功能模块
│   ├── app.py               # 主入口逻辑（已简化）
│   ├── breaker\_recommend.py
│   ├── chat\_logic.py
│   ├── data\_loader.py
│   ├── llm\_client.py
│   ├── log\_utils.py
│   ├── product\_code\_generator.py
│   ├── prompt\_template.py
│   ├── search\_product\_info.py
│   ├── trip\_recommend.py
│   └── ui\_components.py
├── .gitignore
└── README.md

````

---

## 🚀 快速开始

### ✅ 环境配置

```bash
git clone https://github.com/yourname/circuitBreaker-Sizer.git
cd circuitBreaker-Sizer

# 安装依赖（推荐使用虚拟环境）
pip install -r requirements.txt
````

---

### ▶️ 启动服务

```bash
streamlit run app.py
```

默认地址：[http://localhost:8501](http://localhost:8501)

---

## 💡 功能介绍

| 功能           | 描述                               |
| ------------ | -------------------------------- |
| 🗣️ 中文自然语言输入 | 输入“我要额定电流2500A，4极，抽屉式”，自动解析需求    |
| 🤖 LLM参数解析   | 基于 Prompt Template 提取断路器参数和脱扣器参数 |
| 🧩 脱扣器筛选匹配   | 支持上传脱扣器 Excel 表，字段自动匹配和最优筛选      |
| 📦 产品序列号推荐   | 自动生成完整产品序列号，匹配订货号                |
| 📄 参数查询      | 查询产品型号所对应的技术参数，展示为结构化表格          |
| 📝 聊天记录保存    | 对历史提问、推荐表、脱扣器信息等进行记录与重现          |

---

## ⚙️ 模型配置

支持通过 API 调用本地或远程模型（兼容 OpenAI 接口）。

配置位于 `config/config.py`：

```python
LLM_CFG = {
    "model_name": "glm4-chat",
    "xinference_url": "http://localhost:9997/v1/chat/completions",
    "max_tokens_breaker": 1024,
    "max_tokens_trip": 1024,
}
```

---

## 📸 展示截图

> 以下为部分实际使用截图（用户输入 → 推荐型号 → 技术参数）：

| 自然语言输入   | 推荐产品序列号   | 技术参数展示   |
| -------- | --------- | -------- |
| ✅ 支持模糊匹配 | ✅ 多型号自动推荐 | ✅ 自动提取表头 |

---

## 🧩 开发计划

* [x] 拆分逻辑模块，提升可维护性
* [x] 支持上传脱扣器参数Excel
* [ ] 增加参数导出功能（CSV/Excel）
* [ ] 接入嵌入式向量搜索辅助模型推荐
* [ ] UI界面增强（深色主题、字段过滤等）

---

## 📜 许可证 License

MIT License
仅用于学习与研究用途，请勿用于商业部署。数据以西门子官方资料为准。

---

## 👨‍💻 维护者 Maintainer

**Your Name**
[GitHub](https://github.com/yourname) · [Email](mailto:your@email.com)

---

> 欢迎 star ⭐️ & fork 🍴 ，一起探索工业智能选型的新范式。

```
