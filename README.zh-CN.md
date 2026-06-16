# BookSkill Studio

[English](README.md)

把任意书籍或长文档，在 5 分钟内编译成可追溯的 Agent Skill。

BookSkill Studio 是一个轻量 CLI，能把源材料变成：

- 可安装的 `SKILL.md`
- 按章节拆分的配套文件
- 可追溯的证据映射
- 机器可读的校验报告
- 一键本地安装

## 快速开始

运行内置 demo：

```bash
cd bookskill-studio
python3 -m pip install -e .
python3 -m bookskill_studio doctor
python3 -m bookskill_studio demo --output demo-output
python3 -m bookskill_studio validate demo-output
python3 -m bookskill_studio install demo-output --target cursor
python3 -m bookskill_studio open-report demo-output
```

编译中文书籍（自动检测语言，或显式指定）：

```bash
python3 -m bookskill_studio run my-book.md --output my-book-skill --lang zh
python3 -m bookskill_studio run my-book.md --output my-book-skill --lang auto
```

## 语言支持

- `--lang auto`（默认）：根据正文里中文/英文字符比例自动选择
- `--lang zh`：生成中文 Skill 模板、速查表、校验报告
- `--lang en`：生成英文输出

中文源材料支持：

- Markdown 二级标题、`第X章` 章节识别
- 中文概念提取与「当…应该/必须…」规则识别
- 中文校验报告 HTML

## 支持的输入格式

`.md`、`.txt`、`.epub`、`.pdf`

PDF 依赖 `pdftotext`，使用前请先运行 `doctor`。

## CLI

```bash
python3 -m bookskill_studio doctor
python3 -m bookskill_studio demo --output demo-output [--lang zh]
python3 -m bookskill_studio run <book.md> --output outdir [--lang auto]
python3 -m bookskill_studio validate <skill-dir>
python3 -m bookskill_studio install <skill-dir> --target cursor
python3 -m bookskill_studio open-report <skill-dir>
python3 -m bookskill_studio update <skill-dir> <new-source.md>
```

## 开发

```bash
python3 -m pytest
```
