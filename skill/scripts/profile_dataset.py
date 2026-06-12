#!/usr/bin/env python3
"""Generate a lightweight Markdown profile for applied-statistics datasets."""

from __future__ import annotations

import argparse
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable


SUPPORTED_SUFFIXES = {".csv", ".tsv", ".xlsx", ".xls"}
TARGET_NAME_HINTS = (
    "target",
    "label",
    "outcome",
    "response",
    "class",
    "目标",
    "标签",
    "结果",
    "是否",
)
EXACT_TARGET_NAMES = {"y"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile dataset files and write output/data_profile.md."
    )
    parser.add_argument(
        "--project",
        default=".",
        help="Project directory containing README.md and dataset/ or dataset.* files.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Markdown output path. Defaults to <project>/output/data_profile.md.",
    )
    parser.add_argument(
        "--max-categorical-values",
        type=int,
        default=12,
        help="Maximum top values to show for categorical columns.",
    )
    return parser.parse_args()


def md_escape(value: object) -> str:
    text = str(value)
    text = text.replace("|", "\\|").replace("\n", " ")
    return text


def percent(value: float) -> str:
    if math.isnan(value):
        return "NA"
    return f"{value:.1%}"


def discover_dataset_files(project: Path) -> list[Path]:
    files: list[Path] = []

    dataset_dir = project / "dataset"
    if dataset_dir.is_dir():
        files.extend(
            path
            for path in sorted(dataset_dir.rglob("*"))
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
        )

    files.extend(
        path
        for path in sorted(project.glob("dataset.*"))
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )

    seen: set[Path] = set()
    unique_files: list[Path] = []
    for path in files:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_files.append(path)
    return unique_files


def dependency_report(output_path: Path, error: Exception) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(
            [
                "# 数据画像",
                "",
                "无法生成数据画像，因为缺少必要依赖。",
                "",
                "## 缺少依赖",
                "",
                f"- `{type(error).__name__}: {error}`",
                "",
                "## 安装建议",
                "",
                "```bash",
                "pip install pandas openpyxl xlrd",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )


def no_dataset_report(project: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(
            [
                "# 数据画像",
                "",
                f"生成时间：{datetime.now().isoformat(timespec='seconds')}",
                "",
                "## 数据文件",
                "",
                "未发现可画像的数据文件。",
                "",
                "请在项目中提供以下任一输入：",
                "",
                "- `dataset/` 目录下的 `.csv`、`.tsv`、`.xlsx` 或 `.xls` 文件",
                "- 根目录下的 `dataset.csv`、`dataset.tsv`、`dataset.xlsx` 或 `dataset.xls`",
                "",
                "## 项目路径",
                "",
                f"`{project}`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def read_table(pd, path: Path) -> list[tuple[str, object, str | None]]:
    suffix = path.suffix.lower()
    tables: list[tuple[str, object, str | None]] = []

    if suffix == ".csv":
        try:
            return [(path.name, pd.read_csv(path), None)]
        except UnicodeDecodeError:
            return [(path.name, pd.read_csv(path, encoding="utf-8-sig"), None)]

    if suffix == ".tsv":
        try:
            return [(path.name, pd.read_csv(path, sep="\t"), None)]
        except UnicodeDecodeError:
            return [
                (path.name, pd.read_csv(path, sep="\t", encoding="utf-8-sig"), None)
            ]

    if suffix in {".xlsx", ".xls"}:
        excel = pd.ExcelFile(path)
        for sheet_name in excel.sheet_names:
            label = f"{path.name} [{sheet_name}]"
            tables.append((label, pd.read_excel(path, sheet_name=sheet_name), None))
        return tables

    return [(path.name, None, f"Unsupported file type: {suffix}")]


def is_binary_series(series) -> bool:
    non_null = series.dropna()
    if non_null.empty:
        return False
    unique_values = list(non_null.unique())
    if len(unique_values) != 2:
        return False

    dtype_kind = getattr(series.dtype, "kind", "")
    normalized = {str(value).strip().lower() for value in unique_values}
    yes_no_values = {"0", "1", "true", "false", "yes", "no", "y", "n", "是", "否"}

    if dtype_kind == "b":
        return True
    if dtype_kind in {"i", "u", "f"}:
        try:
            return {float(value) for value in unique_values}.issubset({0.0, 1.0})
        except (TypeError, ValueError):
            return False
    return normalized.issubset(yes_no_values) or dtype_kind in {"O", "U", "S"}


def target_candidates(df, pd) -> list[str]:
    candidates: list[str] = []
    for column in df.columns:
        lower = str(column).lower()
        if lower in EXACT_TARGET_NAMES or any(
            hint in lower for hint in TARGET_NAME_HINTS
        ):
            candidates.append(str(column))

    for column in df.columns:
        if str(column) in candidates:
            continue
        series = df[column]
        if is_binary_series(series):
            candidates.append(str(column))

    return candidates[:8]


def dataframe_sections(label: str, df, pd, max_categorical_values: int) -> list[str]:
    lines: list[str] = [f"## 表：{md_escape(label)}", ""]
    row_count, column_count = df.shape
    lines.extend(
        [
            f"- 数据维度：{row_count} 行 x {column_count} 列",
            f"- 重复行数：{int(df.duplicated().sum())}",
            "",
        ]
    )

    lines.extend(
        [
            "### 字段与类型",
            "",
            "| 字段 | 类型 | 非空数 | 缺失率 | 唯一值数 |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for column in df.columns:
        series = df[column]
        missing_rate = float(series.isna().mean())
        unique_count = int(series.nunique(dropna=True))
        lines.append(
            f"| {md_escape(column)} | {md_escape(series.dtype)} | {int(series.notna().sum())} | {percent(missing_rate)} | {unique_count} |"
        )
    lines.append("")

    candidates = target_candidates(df, pd)
    lines.extend(["### 目标变量候选", ""])
    if candidates:
        for column in candidates:
            series = df[column]
            value_counts = series.value_counts(dropna=False, normalize=True).head(5)
            distribution = ", ".join(
                f"{md_escape(index)}: {share:.1%}"
                for index, share in value_counts.items()
            )
            lines.append(f"- `{md_escape(column)}`：{distribution}")
    else:
        lines.append("- 未发现明显目标变量候选。")
    lines.append("")

    numeric_df = df.select_dtypes(include=["number"])
    lines.extend(["### 数值变量摘要", ""])
    if numeric_df.empty:
        lines.append("未发现数值变量。")
    else:
        summary = numeric_df.describe().T
        lines.append("| 字段 | 均值 | 标准差 | 最小值 | 25% | 中位数 | 75% | 最大值 |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for column, row in summary.iterrows():
            lines.append(
                "| "
                + f"{md_escape(column)} | "
                + f"{row.get('mean', float('nan')):.4g} | "
                + f"{row.get('std', float('nan')):.4g} | "
                + f"{row.get('min', float('nan')):.4g} | "
                + f"{row.get('25%', float('nan')):.4g} | "
                + f"{row.get('50%', float('nan')):.4g} | "
                + f"{row.get('75%', float('nan')):.4g} | "
                + f"{row.get('max', float('nan')):.4g} |"
            )
    lines.append("")

    categorical_columns = [
        column
        for column in df.columns
        if column not in numeric_df.columns
        or df[column].nunique(dropna=True) <= max_categorical_values
    ]
    lines.extend(["### 分类变量取值概览", ""])
    if not categorical_columns:
        lines.append("未发现适合概览的分类变量。")
    else:
        for column in categorical_columns[:30]:
            series = df[column]
            counts = series.value_counts(dropna=False).head(max_categorical_values)
            values = ", ".join(
                f"{md_escape(index)} ({int(count)})" for index, count in counts.items()
            )
            lines.append(f"- `{md_escape(column)}`：{values}")
    lines.append("")

    alerts = quality_alerts(df, candidates)
    lines.extend(["### 明显数据质量提醒", ""])
    if alerts:
        lines.extend(f"- {alert}" for alert in alerts)
    else:
        lines.append("- 未发现显著的轻量画像层面异常。")
    lines.append("")

    return lines


def quality_alerts(df, candidates: Iterable[str]) -> list[str]:
    alerts: list[str] = []
    row_count = len(df)

    if row_count == 0:
        return ["数据表为空。"]

    duplicate_count = int(df.duplicated().sum())
    if duplicate_count:
        alerts.append(f"存在 {duplicate_count} 行完全重复记录。")

    for column in df.columns:
        series = df[column]
        missing_rate = float(series.isna().mean())
        unique_count = int(series.nunique(dropna=True))
        unique_rate = unique_count / row_count if row_count else 0.0
        name = str(column)
        lower = name.lower()

        if missing_rate == 1:
            alerts.append(f"`{md_escape(name)}` 全部缺失。")
        elif missing_rate >= 0.2:
            alerts.append(f"`{md_escape(name)}` 缺失率较高：{percent(missing_rate)}。")

        if unique_count == 1 and missing_rate < 1:
            alerts.append(f"`{md_escape(name)}` 为常量字段。")

        if unique_rate >= 0.95 and ("id" in lower or "编号" in name or "序号" in name):
            alerts.append(
                f"`{md_escape(name)}` 可能是标识符字段，不宜直接作为普通解释变量。"
            )

    for column in candidates:
        if column not in df.columns:
            continue
        proportions = df[column].value_counts(dropna=False, normalize=True)
        if not proportions.empty and float(proportions.iloc[0]) >= 0.9:
            alerts.append(
                f"`{md_escape(column)}` 类别分布高度不平衡，最大类别占比 {proportions.iloc[0]:.1%}。"
            )

    return alerts


def build_report(
    project: Path,
    output_path: Path,
    dataset_files: list[Path],
    pd,
    max_categorical_values: int,
) -> str:
    lines: list[str] = [
        "# 数据画像",
        "",
        f"生成时间：{datetime.now().isoformat(timespec='seconds')}",
        f"项目路径：`{project}`",
        "",
        "## 数据文件",
        "",
        "| 文件 | 大小 |",
        "| --- | ---: |",
    ]

    for path in dataset_files:
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        lines.append(f"| `{md_escape(path.relative_to(project))}` | {size} bytes |")
    lines.append("")

    for path in dataset_files:
        try:
            tables = read_table(pd, path)
        except Exception as exc:  # pragma: no cover - depends on local file engines
            error_message = f"{type(exc).__name__}: {md_escape(exc)}"
            lines.extend(
                [
                    f"## 表：{md_escape(path.name)}",
                    "",
                    f"读取失败：`{error_message}`",
                    "",
                ]
            )
            if isinstance(exc, ImportError) or "Missing optional dependency" in str(
                exc
            ):
                lines.extend(
                    [
                        "安装建议：",
                        "",
                        "```bash",
                        "pip install pandas openpyxl xlrd",
                        "```",
                        "",
                    ]
                )
            continue

        for label, df, error in tables:
            if error:
                lines.extend(
                    [
                        f"## 表：{md_escape(label)}",
                        "",
                        f"读取失败：`{md_escape(error)}`",
                        "",
                    ]
                )
                continue
            lines.extend(dataframe_sections(label, df, pd, max_categorical_values))

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    project = Path(args.project).expanduser().resolve()
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else project / "output" / "data_profile.md"
    )

    try:
        import pandas as pd  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        dependency_report(output_path, exc)
        print(f"Wrote dependency report to {output_path}")
        return 0

    dataset_files = discover_dataset_files(project)
    if not dataset_files:
        no_dataset_report(project, output_path)
        print(f"Wrote no-dataset report to {output_path}")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = build_report(
        project, output_path, dataset_files, pd, args.max_categorical_values
    )
    output_path.write_text(report + "\n", encoding="utf-8")
    print(f"Wrote data profile to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
