import argparse
import json
import os
import re
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_MD_PATH = ROOT / "MoneyPrinter G Official Fan Website.md"
TEAM_TXT_PATH = ROOT / "team-fullstack.txt"
DOCS_DIR = ROOT / "docs"
CONFIG_DIR = ROOT / "config"
DIST_DIR = ROOT / "dist"
SITE_DIR = ROOT / "Moneyprinterg"


def ensure_dirs():
    for d in [DOCS_DIR, CONFIG_DIR, DIST_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def parse_project_doc():
    if not DOC_MD_PATH.exists():
        return {"exists": False, "sections": []}
    text = DOC_MD_PATH.read_text(encoding="utf-8")
    # 粗略按 Markdown 标题分段
    sections = []
    current = None
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            if current:
                sections.append(current)
            current = {"title": m.group(2).strip(), "content": []}
        else:
            if current:
                current["content"].append(line)
    if current:
        sections.append(current)
    # 输出到 docs
    (DOCS_DIR / "ProjectDocumentation.md").write_text(text, encoding="utf-8")
    (DOCS_DIR / "ProjectDocumentation.summary.json").write_text(
        json.dumps({"section_count": len(sections), "sections": sections}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"exists": True, "section_count": len(sections)}


def extract_team_config():
    if not TEAM_TXT_PATH.exists():
        return {"exists": False}
    txt = TEAM_TXT_PATH.read_text(encoding="utf-8")
    # 提取 .bmad-core/agent-teams/team-fullstack.yaml 区块
    start_tag = "==================== START: .bmad-core/agent-teams/team-fullstack.yaml ===================="
    end_tag = "==================== END: .bmad-core/agent-teams/team-fullstack.yaml ===================="
    start_idx = txt.find(start_tag)
    end_idx = txt.find(end_tag)
    yaml_block = None
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        yaml_block = txt[start_idx + len(start_tag):end_idx].strip()
    # 回退策略：查找首个 YAML 样式 bundle 片段
    if not yaml_block:
        m = re.search(r"bundle:\n[\s\S]+?agents:[\s\S]+?workflows:[\s\S]+", txt)
        if m:
            yaml_block = m.group(0)
    if not yaml_block:
        return {"exists": True, "extracted": False}
    (CONFIG_DIR / "team-fullstack.yaml").write_text(yaml_block, encoding="utf-8")
    # 使用 pyyaml 解析
    agents = []
    workflows = []
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(yaml_block) or {}
        bundle = data.get("bundle", {})
        agents = bundle.get("agents", []) or []
        workflows = bundle.get("workflows", []) or []
    except Exception as e:
        # pyyaml 不可用或解析失败，回退到简单抽取
        agents = []
        workflows = []
        for line in yaml_block.splitlines():
            if line.strip().startswith("- ") and "agents:" in yaml_block:
                agents.append(line.strip().lstrip("- "))
        for line in yaml_block.splitlines():
            if line.strip().startswith("- ") and ".yaml" in line and "workflows:" in yaml_block:
                workflows.append(line.strip().lstrip("- "))
    summary = {"agents": agents, "workflows": workflows}
    (CONFIG_DIR / "team-fullstack.summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"exists": True, "extracted": True, "agent_count": len(agents), "workflow_count": len(workflows)}


def quality_checks():
    issues = []
    # 检查站点基本文件
    for fname in ["index.html", "discography.html", "events.html", "styles.css", "script.js"]:
        p = SITE_DIR / fname
        if not p.exists():
            issues.append(f"缺少站点文件: {fname}")
    # 检查根数据 JSON
    for j in ["discography.json", "events.json", "links.json"]:
        p = ROOT / j
        if not p.exists():
            issues.append(f"缺少数据文件: {j}")
        else:
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                issues.append(f"JSON 解析失败: {j}: {e}")
    # 简单检查封面目录
    covers_dir = ROOT / "covers"
    if not covers_dir.exists():
        issues.append("缺少封面目录: covers/")
    else:
        # 至少存在一张图片
        has_image = any(p.suffix.lower() in {".png", ".jpg", ".jpeg"} for p in covers_dir.iterdir())
        if not has_image:
            issues.append("封面目录未找到图片文件")
    return issues


def copy_to_dist():
    # 清理并复制站点与资源
    if DIST_DIR.exists():
        for item in DIST_DIR.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)
            else:
                shutil.rmtree(item, ignore_errors=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SITE_DIR, DIST_DIR / "site", dirs_exist_ok=True)
    # 复制封面与数据
    if (ROOT / "covers").exists():
        shutil.copytree(ROOT / "covers", DIST_DIR / "site" / "covers", dirs_exist_ok=True)
    for j in ["discography.json", "events.json", "links.json"]:
        p = ROOT / j
        if p.exists():
            shutil.copy2(p, DIST_DIR / "site" / j)
    # 复制文档与配置
    for src_dir in [DOCS_DIR, CONFIG_DIR]:
        if src_dir.exists():
            shutil.copytree(src_dir, DIST_DIR / src_dir.name, dirs_exist_ok=True)


def write_build_report(structure, team_cfg, issues):
    report_md = ROOT / "BUILD_REPORT.md"
    lines = []
    lines.append("# 构建报告\n")
    lines.append("## 整合后的项目结构\n")
    lines.append("- 根目录：" + str(ROOT))
    lines.append("- 主要目录：docs/、config/、Moneyprinterg/、dist/\n")
    lines.append("\n## 团队资源配置情况\n")
    lines.append(f"- 已提取 agents 数量：{team_cfg.get('agent_count', 0)}")
    lines.append(f"- 已提取 workflows 数量：{team_cfg.get('workflow_count', 0)}\n")
    lines.append("## 构建过程中发现的问题或冲突\n")
    if issues:
        for i in issues:
            lines.append(f"- {i}")
    else:
        lines.append("- 未发现阻塞问题\n")
    lines.append("## 最终构建产物完整性验证结果\n")
    # 基本完整性校验
    dist_ok = (DIST_DIR / "site" / "index.html").exists()
    lines.append(f"- 站点入口存在：{'是' if dist_ok else '否'}")
    docs_ok = (DIST_DIR / "docs" / "ProjectDocumentation.md").exists()
    lines.append(f"- 文档打包：{'是' if docs_ok else '否'}")
    cfg_ok = (DIST_DIR / "config" / "team-fullstack.yaml").exists()
    lines.append(f"- 团队配置打包：{'是' if cfg_ok else '否'}\n")
    report_md.write_text("\n".join(lines), encoding="utf-8")


def zip_release():
    # 生成压缩包 release.zip
    zip_path = ROOT / "release.zip"
    if zip_path.exists():
        zip_path.unlink()
    shutil.make_archive(str(zip_path).replace(".zip", ""), "zip", DIST_DIR)
    return zip_path


def main():
    parser = argparse.ArgumentParser(description="MoneyPrinter G 项目构建脚本")
    parser.add_argument("--release", action="store_true", help="生成发行版压缩包")
    args = parser.parse_args()

    ensure_dirs()
    doc_info = parse_project_doc()
    team_info = extract_team_config()
    issues = quality_checks()
    copy_to_dist()
    write_build_report(structure={}, team_cfg=team_info, issues=issues)
    if args.release:
        zip_release()
    print("构建完成。报告已生成：BUILD_REPORT.md")


if __name__ == "__main__":
    main()