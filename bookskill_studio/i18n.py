from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Strings:
    unknown_author: str
    section_title: str
    overview: str
    no_body_text: str
    default_summary: str
    default_takeaway: str
    core_concepts: str
    core_idea: str
    review_source: str
    rule_when_context: str
    rule_source_conditions: str
    rule_fallback: str
    rule_prefix: str
    rule_joiner: str
    evidence_no_rules: str
    evidence_core_idea: str
    evidence_summary: str
    evidence_concepts: str
    evidence_rules: str
    evidence_excerpt: str
    chapter_heading: str
    core_idea_heading: str
    frameworks_heading: str
    decision_rules_heading: str
    takeaways_heading: str
    takeaway_read_summary: str
    concepts_title: str
    cheatsheet_title: str
    cheatsheet_fallback: str
    evidence_map_title: str
    skill_description: str
    author_label: str
    how_to_use: str
    use_topic_jump: str
    use_evidence_map: str
    use_cheatsheet: str
    chapter_index: str
    chapter_col: str
    title_col: str
    key_concepts_col: str
    core_ideas: str
    topic_index: str
    topic_overview: str
    supporting_files: str
    validation_title: str
    validation_pending: str
    validation_skill_slug: str
    validation_source: str
    validation_score: str
    validation_status: str
    validation_checks: str
    validation_missing: str
    validation_broken: str
    validation_none: str
    validation_pass: str
    validation_fail: str
    html_title: str
    html_intro: str
    html_coverage: str
    html_chapters: str
    html_check_col: str
    html_status_col: str


STRINGS: dict[str, Strings] = {
    "en": Strings(
        unknown_author="Unknown",
        section_title="Section {index}",
        overview="Overview",
        no_body_text="No body text was extracted for this chapter.",
        default_summary="This chapter captures one reusable idea from the source.",
        default_takeaway="Translate the chapter into concrete actions.",
        core_concepts="core concepts",
        core_idea="Core Idea",
        review_source="Review the source chapter for the main concept.",
        rule_when_context="you face the matching context",
        rule_source_conditions="the source conditions apply",
        rule_fallback="When details matter, open the source-aligned evidence map first.",
        rule_prefix="When {when}, do {do}.",
        rule_joiner="When {when}, do {do}",
        evidence_no_rules="No explicit decision rules detected.",
        evidence_core_idea="Core idea",
        evidence_summary="Summary",
        evidence_concepts="Concepts",
        evidence_rules="Rules",
        evidence_excerpt="Source excerpt",
        chapter_heading="Chapter {number}: {title}",
        core_idea_heading="Core Idea",
        frameworks_heading="Frameworks Introduced",
        decision_rules_heading="Decision Rules",
        takeaways_heading="Key Takeaways",
        takeaway_read_summary="Read the summary before diving into the source.",
        concepts_title="Concepts",
        cheatsheet_title="Cheatsheet",
        cheatsheet_fallback="- Start with the chapter index, then read the matching chapter file.",
        evidence_map_title="Evidence Map",
        skill_description=(
            'Evidence-backed skill compiled from {title}. '
            "Use when you need chapter-level guidance, concepts, and decision rules from this source."
        ),
        author_label="Author",
        how_to_use="How to Use This Skill",
        use_topic_jump="Ask for a topic to jump to the matching chapter.",
        use_evidence_map="Read `references/evidence-map.md` when you need traceable support.",
        use_cheatsheet="Use `references/cheatsheet.md` for quick decisions.",
        chapter_index="Chapter Index",
        chapter_col="Chapter",
        title_col="Title",
        key_concepts_col="Key Concepts",
        core_ideas="core ideas",
        topic_index="Topic Index",
        topic_overview="Overview",
        supporting_files="Supporting Files",
        validation_title="Validation Report",
        validation_pending="Pending validation.",
        validation_skill_slug="Skill slug",
        validation_source="Source",
        validation_score="Overall score",
        validation_status="Status",
        validation_checks="Checks",
        validation_missing="Missing Files",
        validation_broken="Broken Links",
        validation_none="None",
        validation_pass="pass",
        validation_fail="fail",
        html_title="BookSkill Studio Validation Report",
        html_intro=(
            "Human-readable proof that the generated skill package is structurally sound "
            "and ready for local installation."
        ),
        html_coverage="Coverage",
        html_chapters="{chapter_count} chapters, {evidence_sections} evidence sections.",
        html_check_col="Check",
        html_status_col="Status",
    ),
    "zh": Strings(
        unknown_author="未知",
        section_title="第 {index} 节",
        overview="概览",
        no_body_text="本章未提取到正文内容。",
        default_summary="本章从原书提炼出一个可复用的核心观点。",
        default_takeaway="把本章观点转成可执行动作。",
        core_concepts="核心概念",
        core_idea="核心观点",
        review_source="请回看原书章节，抓住主线概念。",
        rule_when_context="遇到对应场景时",
        rule_source_conditions="满足原文所述条件时",
        rule_fallback="需要细节支撑时，先打开证据映射表。",
        rule_prefix="当{when}，就{do}。",
        rule_joiner="当{when}，就{do}",
        evidence_no_rules="未检测到明确的决策规则。",
        evidence_core_idea="核心观点",
        evidence_summary="摘要",
        evidence_concepts="概念",
        evidence_rules="规则",
        evidence_excerpt="原文摘录",
        chapter_heading="第 {number} 章：{title}",
        core_idea_heading="核心观点",
        frameworks_heading="引入的框架",
        decision_rules_heading="决策规则",
        takeaways_heading="关键 takeaway",
        takeaway_read_summary="先读摘要，再深入原文。",
        concepts_title="概念索引",
        cheatsheet_title="速查表",
        cheatsheet_fallback="- 先看章节目录，再打开对应章节文件。",
        evidence_map_title="证据映射",
        skill_description="由《{title}》编译而成的可追溯 Agent Skill。需要章节级指导、概念与决策规则时使用。",
        author_label="作者",
        how_to_use="如何使用本 Skill",
        use_topic_jump="按主题提问，跳转到对应章节。",
        use_evidence_map="需要可追溯依据时，阅读 `references/evidence-map.md`。",
        use_cheatsheet="快速决策时，使用 `references/cheatsheet.md`。",
        chapter_index="章节目录",
        chapter_col="章节",
        title_col="标题",
        key_concepts_col="关键概念",
        core_ideas="核心观点",
        topic_index="主题索引",
        topic_overview="概览",
        supporting_files="配套文件",
        validation_title="校验报告",
        validation_pending="等待校验。",
        validation_skill_slug="Skill 标识",
        validation_source="来源",
        validation_score="总分",
        validation_status="状态",
        validation_checks="检查项",
        validation_missing="缺失文件",
        validation_broken="失效链接",
        validation_none="无",
        validation_pass="通过",
        validation_fail="未通过",
        html_title="BookSkill Studio 校验报告",
        html_intro="用于确认生成的 Skill 包结构完整，可直接本地安装。",
        html_coverage="覆盖范围",
        html_chapters="{chapter_count} 章，{evidence_sections} 段证据映射。",
        html_check_col="检查项",
        html_status_col="状态",
    ),
}


def resolve_lang(requested: str | None, text: str) -> str:
    if requested and requested not in {"auto", ""}:
        return requested if requested in STRINGS else "en"
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin_count = len(re.findall(r"[A-Za-z]", text))
    return "zh" if cjk_count > latin_count else "en"


def get_strings(lang: str) -> Strings:
    return STRINGS.get(lang, STRINGS["en"])
