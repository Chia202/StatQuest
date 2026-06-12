# StatQuest

StatQuest 是一个用于设计“应用统计智能体评测任务集”的 Codex skill 项目。

它读取一个应用统计作业项目中的 `README.md` 与 `dataset/` 或 `dataset.*` 数据文件，帮助生成固定任务集、多模型 CLI 提示词、评价准则、答案比较材料和最终数据分析报告框架。它不直接调用三个大模型；你可以把同一套提示词复制到不同模型 CLI 中，再把回答放回 `output/model_answers/` 进行比较和整合。

## 项目结构

```text
StatQuest/
  README.md
  README.en.md
  skill/
    SKILL.md
    scripts/
      profile_dataset.py
  examples/
    applied-stat-assignment/
      README.md
      reference_taskset.html
      dataset/
        .gitkeep
      output/
        .gitkeep
  LICENSE
```

## 功能

- 从作业要求和数据集背景中抽取研究场景、交付物和评分约束。
- 对数据集做轻量画像：文件列表、字段类型、缺失率、目标变量候选、数值摘要、分类变量概览和明显质量提醒。
- 生成四个应用统计环节的固定任务集：
  - 问题陈述与精练
  - 数据探索性分析
  - 建模分析
  - 结果解释
- 每个环节默认生成简单、中等、困难各 1 道题，共 12 道题。
- 生成可复制到三个模型 CLI 的统一提示词。
- 生成三模型答案记录模板、评价准则、比较表和最终报告框架。

数据画像脚本保持领域无关，不会硬编码参考 HTML 案例或某个具体数据集的变量名。

## 安装

Codex 会从 `.agents/skills`、`~/.agents/skills` 等位置发现本地 skills。这个仓库把可复用 skill 放在 `skill/` 目录中；安装时可以复制或软链接到 Codex 会扫描的位置。

### 方式一：仓库内安装

适合开发、演示和在本仓库中测试。

```bash
mkdir -p .agents/skills
ln -s ../../skill .agents/skills/StatQuest
```

如果系统不适合使用软链接，可以复制：

```bash
mkdir -p .agents/skills/StatQuest
cp -R skill/. .agents/skills/StatQuest/
```

然后在本仓库中重新启动 Codex，或开启一个新的 Codex 会话。可用 `/skills` 查看是否出现 `StatQuest`。

### 方式二：全局安装

适合在多个项目中复用。

```bash
mkdir -p ~/.agents/skills/StatQuest
cp -R skill/. ~/.agents/skills/StatQuest/
```

安装后重新启动 Codex，或开启新的 Codex 会话。之后可以在任意项目中通过 `/skills` 选择该 skill，或在提示中显式写 `$StatQuest`。

## 依赖

核心 skill 是 Markdown 指令，不需要额外依赖。数据画像脚本需要 Python 和 pandas：

```bash
pip install pandas openpyxl xlrd
```

其中 `openpyxl` 和 `xlrd` 用于读取 Excel 文件。没有数据或缺少依赖时，脚本会在 `output/data_profile.md` 中写明原因和建议，不会静默失败。

## 输入项目结构

被分析的作业项目建议采用以下结构：

```text
project/
  README.md
  dataset/              # 可选：数据目录
  dataset.csv           # 或单个 dataset.* 文件
  output/               # skill 生成物目录
```

`README.md` 应包含作业要求、场景说明、研究问题或评分标准。`dataset/` 或 `dataset.*` 支持 `.csv`、`.tsv`、`.xlsx`、`.xls`。

skill 不应修改输入项目的 `README.md` 和数据文件，只写入 `output/`。

## 输出文件

默认会覆盖 `output/` 中的标准生成物。覆盖前，Codex 应先说明将重写哪些文件。非标准文件默认保留。

```text
output/data_profile.md
output/process_log.md
output/taskset.md
output/evaluation_rubric.md
output/model_prompts.md
output/model_answers/model_a.md
output/model_answers/model_b.md
output/model_answers/model_c.md
output/answer_comparison.md
output/final_report.md
output/index.html
```

## 使用方法

### 1. 初始化任务集

进入一个包含作业 `README.md` 和数据文件的项目，然后在 Codex 中请求：

```text
$StatQuest 初始化这个应用统计评测任务集。
读取 README.md 和 dataset，生成 data_profile.md、taskset.md、evaluation_rubric.md、model_prompts.md 和 model_answers 模板。
```

初始化阶段会生成固定的 12 道题和统一的模型回答提示词。

### 2. 在三个模型 CLI 中收集回答

打开 `output/model_prompts.md`，将同一份提示词分别复制到三个模型 CLI 中。把三个模型的输出分别放入：

```text
output/model_answers/model_a.md
output/model_answers/model_b.md
output/model_answers/model_c.md
```

每个文件都应保留 `Q1-Easy` 到 `Q12-Hard` 的题号结构，便于公平比较。

### 3. 比较三模型答案

模型回答整理好后，在 Codex 中请求：

```text
$StatQuest 比较 output/model_answers/ 中三个模型的回答。
请根据 evaluation_rubric.md 生成 answer_comparison.md，并补充 process_log.md。
```

比较阶段会按统一总 rubric 和每题评价要点给出评分、排序和理由。

### 4. 整合最终报告

比较完成后，在 Codex 中请求：

```text
$StatQuest 基于高质量回答和 answer_comparison.md，整合 final_report.md。
必要时生成 index.html 作为汇总展示版。
```

最终报告应整合高质量模型回答，同时保留统计判断、局限性说明和课程要求对应关系。

## 单独运行数据画像脚本

可以不调用完整 skill，单独运行轻量数据画像：

```bash
python skill/scripts/profile_dataset.py --project examples/applied-stat-assignment
```

默认输出到：

```text
examples/applied-stat-assignment/output/data_profile.md
```

也可以指定输出路径：

```bash
python skill/scripts/profile_dataset.py \
  --project examples/applied-stat-assignment \
  --output /tmp/data_profile.md
```

## 示例项目

示例位于：

```text
examples/applied-stat-assignment/
  README.md
  reference_taskset.html
  dataset/
  output/
```

其中 `README.md` 保存应用统计期末作业要求，`reference_taskset.html` 是重命名后的参考任务集。示例目录不包含 `应用统计期末作业.pdf`。

## 开发说明

- `skill/SKILL.md` 是核心 skill 指令。
- `skill/scripts/profile_dataset.py` 只做轻量、通用的数据画像，不做建模。
- 如果修改了 skill，但 Codex 没有识别到更新，重启 Codex 或开启新会话。
- 如果通过复制方式安装，全局 skill 不会自动跟随仓库更新；开发时优先使用软链接。
