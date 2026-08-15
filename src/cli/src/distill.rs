//! D-Distill(提取):读分组产物,过滤次要信息并统一表达,
//! 形成初稿 materials/<topic>.md(产物 03)。
//!
//! 产物链:01 收集(collect) → 02 分组(organize) → 03 初稿(distill)
//! → 04 定稿(express)。

use std::fs;
use std::path::{Path, PathBuf};

/// 初稿提示词:过滤次要信息 + 统一表达(通用判据,不针对特定文本)。
pub fn build_draft_prompt(topic: &str, aggregate: &str) -> String {
    format!(
        "以下是从日志中按主题聚合的写作素材(主题:{topic})。请形成一篇初稿:\n\
         1. 过滤次要信息:\n\
         - 过程性叙述:记录\"正在做/打算做\"的过程性语句(如\"我打算\"\"我在尝试\"\"最近\"),只保留其中的结论或洞察\n\
         - 用途信息:关于素材将被用于什么、发布到哪里的说明(如发布渠道、宣传用途、收益安排、目标账号),除非该用途本身是主题的核心问题\n\
         - 区分动机与用途:\"为什么写\"是主题核心,应保留;\"写完之后拿去做什么\"属于事务性用途,默认删除\n\
         - 重复表述:同一观点多次出现时只保留最完整的一次\n\
         - 即时情绪宣泄:直接的情绪感叹与自我对话;若其中包含可迁移的洞察则保留洞察\n\
         2. 统一表达:用一致的人称与语气连贯组织过滤后的内容,形成一篇结构完整的初稿(markdown,与素材同语言)。\n\
         输出前自查:若结果中仍包含具体事务主体(特定发布渠道、特定事务用途),视为未删净,应删除。\n\
         只输出初稿,不要解释。\n\n素材:\n{aggregate}"
    )
}

/// 执行 distill:读分组产物 groups/<topic>.md → LLM 过滤次要信息并统一表达
/// → 初稿 materials/<topic>.md(产物 03)。
pub fn distill(workdir: &Path, topic: &str) -> Result<PathBuf, String> {
    let src = workdir.join("groups").join(format!("{}.md", topic));
    let group = fs::read_to_string(&src)
        .map_err(|e| format!("读分组 {}: {e}(先运行 material organize 生成分组)", src.display()))?;
    let (fm, body) = crate::frontmatter::parse(&group);

    let prompt = build_draft_prompt(topic, &body);
    let draft = crate::organize::run_llm(&prompt)?;

    // front matter:沿用分组的 sources
    let mut fm = fm.unwrap_or_default();
    fm.topic = Some(topic.to_string());

    let dir = workdir.join("materials");
    fs::create_dir_all(&dir).map_err(|e| format!("mkdir materials: {e}"))?;
    let path = dir.join(format!("{}.md", topic));
    fs::write(&path, format!("{}{}", crate::frontmatter::render(&fm), draft))
        .map_err(|e| format!("write {}: {e}", path.display()))?;
    Ok(path)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tmpdir(name: &str) -> PathBuf {
        let dir = std::env::temp_dir().join(format!("material-distill-{}-{}", name, std::process::id()));
        let _ = fs::remove_dir_all(&dir);
        fs::create_dir_all(&dir).unwrap();
        dir
    }

    fn seed_groups(dir: &Path) {
        let gdir = dir.join("groups");
        fs::create_dir_all(&gdir).unwrap();
        fs::write(
            gdir.join("宣传册.md"),
            "---\ntopic: 宣传册\nsources:\n  - journal/2026-08-15.md#09-30\n---\n\n宣传册想法一\n\n> 来源:journal/2026-08-15.md#09-30\n",
        )
        .unwrap();
    }

    #[test]
    fn distill_missing_group_errors() {
        let dir = tmpdir("nogroup");
        let out = distill(&dir, "宣传册");
        assert!(out.is_err());
        let msg = out.unwrap_err();
        assert!(msg.contains("organize"));
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn draft_prompt_contains_material() {
        let p = build_draft_prompt("宣传册", "素材正文");
        assert!(p.contains("宣传册"));
        assert!(p.contains("素材正文"));
        assert!(p.contains("过滤次要信息"));
        assert!(p.contains("统一表达"));
        assert!(p.contains("初稿"));
    }
}
