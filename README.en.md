# StatQuest

StatQuest is a Codex skill project for designing applied-statistics agent evaluation task sets.

It reads an applied-statistics assignment project with a `README.md` file and a `dataset/` directory or `dataset.*` data file, then helps generate a fixed task set, model CLI prompts, evaluation rubrics, answer comparison materials, and a final analysis report scaffold. It does not call three large language models directly. Instead, you can copy the same prompt into multiple model CLIs, collect their answers, and place those answers back under `output/model_answers/` for comparison and synthesis.

## Repository Structure

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

## Features

- Extracts research context, deliverables, and grading constraints from assignment requirements and dataset context.
- Generates a lightweight dataset profile: file list, column types, missing rates, target-variable candidates, numeric summaries, categorical value overviews, and obvious data-quality warnings.
- Generates a fixed task set across four applied-statistics phases:
  - Problem statement and refinement
  - Exploratory data analysis
  - Modeling analysis
  - Result interpretation
- Creates three questions per phase by default: easy, medium, and hard, for 12 questions total.
- Generates one shared prompt that can be copied into three model CLIs.
- Generates model answer templates, rubrics, comparison tables, and a final report scaffold.

The dataset profiler is domain-agnostic. It does not hard-code assumptions from the reference HTML case or from any single dataset.

## Installation

Codex discovers local skills from locations such as `.agents/skills` and `~/.agents/skills`. This repository stores the reusable skill in `skill/`; install it by copying or symlinking that directory into a location Codex scans.

### Option 1: Repository-Local Installation

Use this option for development, demos, and testing inside this repository.

```bash
mkdir -p .agents/skills
ln -s ../../skill .agents/skills/StatQuest
```

If symlinks are inconvenient on your system, copy the skill instead:

```bash
mkdir -p .agents/skills/StatQuest
cp -R skill/. .agents/skills/StatQuest/
```

Then restart Codex or open a new Codex session in this repository. Use `/skills` to check whether `StatQuest` appears.

### Option 2: Global Installation

Use this option if you want to reuse the skill across multiple projects.

```bash
mkdir -p ~/.agents/skills/StatQuest
cp -R skill/. ~/.agents/skills/StatQuest/
```

After installation, restart Codex or open a new Codex session. You can then select the skill with `/skills` or invoke it explicitly in a prompt with `$StatQuest`.

## Dependencies

The core skill is Markdown instructions and has no runtime dependency. The dataset profiling script requires Python and pandas:

```bash
pip install pandas openpyxl xlrd
```

`openpyxl` and `xlrd` are used for Excel files. If no dataset is present or a dependency is missing, the script writes a clear explanation and installation suggestion to `output/data_profile.md` instead of failing silently.

## Expected Input Project

The target assignment project should look like this:

```text
project/
  README.md
  dataset/              # optional data directory
  dataset.csv           # or a single dataset.* file
  output/               # generated materials
```

`README.md` should describe the assignment requirements, scenario, research question, or grading criteria. `dataset/` or `dataset.*` supports `.csv`, `.tsv`, `.xlsx`, and `.xls`.

The skill should not modify the input project's `README.md` or data files. It writes generated materials only to `output/`.

## Generated Outputs

By default, the skill overwrites standard generated files under `output/`. Before overwriting files, Codex should state which files will be rewritten. Non-standard files are preserved by default.

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

## Usage

### 1. Initialize the Task Set

Enter a project that contains an assignment `README.md` and dataset files, then ask Codex:

```text
$StatQuest Initialize this applied-statistics evaluation task set.
Read README.md and dataset, then generate data_profile.md, taskset.md, evaluation_rubric.md, model_prompts.md, and model_answers templates.
```

The initialization stage creates a fixed 12-question task set and one shared model-answer prompt.

### 2. Collect Answers from Three Model CLIs

Open `output/model_prompts.md` and copy the same prompt into three model CLIs. Save their outputs as:

```text
output/model_answers/model_a.md
output/model_answers/model_b.md
output/model_answers/model_c.md
```

Each file should preserve the question structure from `Q1-Easy` through `Q12-Hard` so the answers can be compared fairly.

### 3. Compare the Three Model Answers

After collecting the model answers, ask Codex:

```text
$StatQuest Compare the three model answers in output/model_answers/.
Use evaluation_rubric.md to generate answer_comparison.md and update process_log.md.
```

The comparison stage scores and ranks the answers using the global rubric and question-specific evaluation points.

### 4. Synthesize the Final Report

After comparison, ask Codex:

```text
$StatQuest Use the high-quality answers and answer_comparison.md to synthesize final_report.md.
Generate index.html as a compact review page if useful.
```

The final report should integrate high-quality model answers while preserving statistical judgment, limitation discussion, and alignment with the assignment requirements.

## Run the Dataset Profiler Directly

You can run the lightweight data profiler without invoking the full skill:

```bash
python skill/scripts/profile_dataset.py --project examples/applied-stat-assignment
```

The default output is:

```text
examples/applied-stat-assignment/output/data_profile.md
```

You can also specify a custom output path:

```bash
python skill/scripts/profile_dataset.py \
  --project examples/applied-stat-assignment \
  --output /tmp/data_profile.md
```

## Example Project

The example project is located at:

```text
examples/applied-stat-assignment/
  README.md
  reference_taskset.html
  dataset/
  output/
```

`README.md` contains the applied-statistics final assignment requirements. `reference_taskset.html` is the renamed reference task set. The example directory does not include `应用统计期末作业.pdf`.

## Development Notes

- `skill/SKILL.md` contains the core skill instructions.
- `skill/scripts/profile_dataset.py` performs only lightweight, general-purpose data profiling. It does not train models.
- If Codex does not detect an updated skill, restart Codex or open a new session.
- If you installed the skill by copying files, the global installed copy will not automatically track repository changes. Prefer a symlink during development.
