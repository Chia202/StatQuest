---
name: StatQuest
description: Design applied-statistics agent evaluation task sets from an assignment README and dataset, then support multi-model CLI answer comparison and final report synthesis.
---

# StatQuest Skill

Use this skill when the user wants to design an applied-statistics intelligent-agent evaluation task set, especially for assignments requiring scenario selection, statistical workflow decomposition, question difficulty design, multi-model answer comparison, and a final integrated data analysis report.

Default language: Chinese. If the user explicitly requests English, generate all deliverables in English. Always preserve original dataset variable names.

## Input Contract

Expect the working project to contain:

```text
README.md
dataset/ or dataset.*
output/
```

`README.md` contains assignment requirements, scenario context, research questions, or grading criteria. `dataset/` or `dataset.*` contains one or more data files. `output/` stores generated materials.

Never modify `README.md`, `dataset/`, or any `dataset.*` file.

## Output Contract

Before writing files, tell the user which standard generated files will be overwritten.

Default overwrite targets:

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

Do not delete the whole `output/` directory. Preserve non-standard files unless the user explicitly asks to remove them.

## Stage 1: initialize

Use this stage when the user asks to initialize, design, generate, or prepare the task set.

Steps:

1. Read `README.md` and extract assignment requirements, required deliverables, grading criteria, scenario constraints, and any specified statistical workflow.
2. Inspect the project for `dataset/` or root-level `dataset.*` files.
3. Run `skill/scripts/profile_dataset.py` when available:

   ```bash
   python skill/scripts/profile_dataset.py --project .
   ```

4. Read `output/data_profile.md` and use it as evidence for task design.
5. Generate the standard Stage 1 deliverables:
   - `output/data_profile.md`
   - `output/process_log.md`
   - `output/taskset.md`
   - `output/evaluation_rubric.md`
   - `output/model_prompts.md`
   - `output/model_answers/model_a.md`
   - `output/model_answers/model_b.md`
   - `output/model_answers/model_c.md`

The dataset profiler must remain domain-agnostic. Do not hard-code field names, target names, anomaly rules, or modeling assumptions from the reference HTML case or from any single example dataset.

### Task Set Structure

Use exactly four applied-statistics phases by default:

1. 问题陈述与精练
2. 数据探索性分析
3. 建模分析
4. 结果解释

Generate three questions per phase:

```text
Q1-Easy
Q2-Medium
Q3-Hard
...
Q12-Hard
```

Each question must include:

- 题目
- 任务背景
- 作答要求
- 难度等级
- 难度依据
- 评价要点

Do not create a fifth task phase for report generation. Treat report generation as the independent final deliverable `final_report.md`.

### Difficulty Principles

Use at least these dimensions when explaining difficulty:

- Statistical concept depth
- Amount of dataset-specific evidence required
- Need to translate business questions into statistical questions
- Need to compare methods rather than name one method
- Need to discuss assumptions, bias, uncertainty, and limitations
- Communication quality for technical and non-technical readers

### `taskset.md` Template

```markdown
# 应用统计智能体评测任务集

## 场景与研究问题

## 数据画像摘要

## 任务设计原则

## 环节一：问题陈述与精练

### Q1-Easy：...

- 任务背景：
- 作答要求：
- 难度等级：简单
- 难度依据：
- 评价要点：

### Q2-Medium：...

### Q3-Hard：...

## 环节二：数据探索性分析

## 环节三：建模分析

## 环节四：结果解释
```

### `evaluation_rubric.md` Template

Use a two-level rubric.

Global rubric:

- 统计正确性
- 场景贴合度
- 数据证据使用
- 方法选择与假设意识
- 结果解释与沟通质量
- 可复现性
- 局限性意识

Question-specific rubric:

```markdown
## Q1-Easy：...

- 评价要点 1：
- 评价要点 2：
- 评价要点 3：
```

Use a simple 1-5 score scale unless the user asks for another scoring format. Always explain ranking criteria in words, not only numbers.

### `model_prompts.md` Template

Create a copyable prompt for model CLIs. It must require every model to answer the same fixed task set in the same format:

```markdown
# Model Answer Prompt

你将回答同一套应用统计智能体评测任务。请严格按以下 Markdown 结构输出，不要改题号，不要删题。

## Q1-Easy：题目标题
回答：

## Q2-Medium：题目标题
回答：

...

## Q12-Hard：题目标题
回答：
```

### `model_answers` Templates

Create:

```text
output/model_answers/model_a.md
output/model_answers/model_b.md
output/model_answers/model_c.md
```

Each file must use this structure:

```markdown
# Model A Answers

## Q1-Easy：题目标题
回答：

## Q2-Medium：题目标题
回答：

...

## Q12-Hard：题目标题
回答：
```

### `process_log.md` Stage 1 Contents

Include:

- README 作业要求摘要
- 数据画像摘要
- 场景选择理由
- 四个统计环节拆分理由
- 题目难度设计原则
- 评价准则设计理由
- 任务集从初稿到定稿的修改说明, if revisions happened

## Stage 2: compare

Use this stage when the user has collected three model answers in `output/model_answers/`.

Steps:

1. Read `output/taskset.md`, `output/evaluation_rubric.md`, and all files under `output/model_answers/`.
2. Verify that at least three model answer files exist and each follows Q1-Easy through Q12-Hard.
3. Score each model's answer for every question using the global and question-specific rubrics.
4. Write `output/answer_comparison.md`.
5. Append a comparison-process section to `output/process_log.md`.

### `answer_comparison.md` Template

```markdown
# 三模型答案评价与排序

## 评价方法

## 总体排序

| 排名 | 模型 | 总体评价 | 主要优势 | 主要不足 |
| --- | --- | --- | --- | --- |

## 分题评价

### Q1-Easy：...

| 模型 | 评分 | 排名 | 理由 |
| --- | ---: | ---: | --- |

## 可用于最终报告的高质量内容
```

## Stage 3: synthesize

Use this stage when the user asks to integrate high-quality model answers into the final report.

Steps:

1. Read `output/taskset.md`, `output/data_profile.md`, `output/answer_comparison.md`, and the model answer files.
2. Extract only high-quality, statistically defensible content.
3. Resolve contradictions across models using the dataset profile, assignment README, and rubric.
4. Write `output/final_report.md`.
5. Optionally write `output/index.html` when the user wants a reviewable HTML version.
6. Append a synthesis section to `output/process_log.md`.

### `final_report.md` Template

```markdown
# 应用统计数据分析报告

## 执行摘要

## 1. 场景背景与研究问题

## 2. 数据说明与探索性分析

## 3. 建模分析方案

## 4. 结果解释与统计判断

## 5. 结论、建议与局限性

## 附录：任务集与模型比较说明
```

## Quality Bar

The generated task set should be concrete enough that three model CLIs answer the same questions fairly. Avoid vague tasks such as "analyze the data" without specifying evidence, assumptions, and deliverable format.

The final report must reflect course understanding through difficulty design and answer-quality judgment, not only through polished writing.
