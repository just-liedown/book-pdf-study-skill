# 书籍 PDF 学习 Skill 实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个可安装到用户目录的 Codex skill。它能先对书籍型 PDF 做一次预处理，然后围绕 `/learn`、`/ask`、`/test` 三种模式和持久化学习状态来工作。

**Architecture:** Skill 放在用户 skill 目录下，包含一个确定性的 PDF 预处理脚本和少量参考文档。脚本负责在源 PDF 旁边建立稳定缓存；SKILL.md 负责指导 Codex 何时触发、何时预处理、如何分析书籍、如何维护状态，以及如何在不同模式下避免反复读取整份 PDF。

**Tech Stack:** Markdown、YAML frontmatter、Python 3 标准库、`pdftotext`、Codex skill 目录规范

---

## Chunk 1: Skill 骨架与文档

### Task 1: 创建 skill 骨架

**Files:**
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/`
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/SKILL.md`
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/agents/openai.yaml`
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/scripts/`
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/references/`

- [ ] **Step 1: 运行初始化脚本**

Run: `python3 /root/.codex/skills/.system/skill-creator/scripts/init_skill.py studying-book-pdfs --path /root/.codex/skills --resources scripts,references --interface display_name='Study Book PDFs' --interface short_description='Learn from long book-style PDF files' --interface default_prompt='Use $studying-book-pdfs to help me study this book PDF.'`
Expected: 生成新的 skill 目录，以及 `SKILL.md`、`agents/openai.yaml` 和所选资源目录

- [ ] **Step 2: 检查生成结果**

Run: `find /home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs -maxdepth 3 -type f | sort`
Expected: 所需文件存在，没有遗留无关占位文件

### Task 2: 定义缓存契约与模式行为

**Files:**
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/references/cache-layout.md`
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/references/commands-and-modes.md`

- [ ] **Step 1: 编写缓存布局文档**

说明缓存目录命名、必须产物、更新规则

- [ ] **Step 2: 编写模式行为文档**

说明 `/learn`、`/ask`、`/test` 的语义、状态更新规则，以及各模式应最少读取哪些缓存文件

## Chunk 2: 预处理脚本

### Task 3: 添加确定性的 PDF 预处理器

**Files:**
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/scripts/preprocess_book_pdf.py`

- [ ] **Step 1: 先写失败的冒烟命令**

Run: `python3 /home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/scripts/preprocess_book_pdf.py --help`
Expected: 如果脚本还不存在，应报 file not found

- [ ] **Step 2: 编写最小脚本**

实现：参数解析、调用 `pdftotext`、分页切分、写出 manifest/pages/chunks/toc candidates

- [ ] **Step 3: 验证 help 正常**

Run: `python3 /home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/scripts/preprocess_book_pdf.py --help`
Expected: PASS，并输出 usage

- [ ] **Step 4: 对一个很小的 PDF 做冒烟测试**

Run: 使用本地生成的小 PDF 或样例 PDF 执行脚本，并检查输出产物
Expected: 缓存目录中生成必需文件

## Chunk 3: Skill 主文档

### Task 4: 将模板替换为正式说明

**Files:**
- Modify: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/SKILL.md`
- Modify: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/agents/openai.yaml`

- [ ] **Step 1: 写好 frontmatter**

frontmatter 只描述触发条件，不摘要流程

- [ ] **Step 2: 写 skill 正文**

覆盖：书籍型 PDF 判断、预处理规则、目标与水平确认、状态持久化、`/learn` `/ask` `/test`

- [ ] **Step 3: 对齐 UI 元数据**

确保 `display_name`、`short_description`、`default_prompt` 与最终内容一致

## Chunk 4: 校验

### Task 5: 校验并做冒烟检查

**Files:**
- Validate: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/`

- [ ] **Step 1: 运行结构校验**

Run: `python3 /root/.codex/skills/.system/skill-creator/scripts/quick_validate.py /home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs`
Expected: PASS，没有 frontmatter 或命名错误

- [ ] **Step 2: 审查最终文件**

Run: `find /home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs -maxdepth 3 -type f | sort`
Expected: 只保留预期文件

- [ ] **Step 3: 记录验证边界**

说明由于当前 harness 策略限制，没有做基于子代理的 forward-testing
