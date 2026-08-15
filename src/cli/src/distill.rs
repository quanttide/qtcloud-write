//! D-Distill(提取):按主题聚合日志条目,过滤次要信息并统一表达,
//! 形成初稿 materials/<topic>.md(产物 03)。
//!
//! 产物链:01 收集(collect) → 02 分组(organize) → 03 初稿(distill)
//! → 04 定稿(express)。

use std::fs;
use std::path::{Path, PathBuf};

use crate::frontmatter::FrontMatter;
use crate::journal::{self, Entry};

/// 收集归属 `topic` 的全部日志条目(按文件 + 时间排序)。
pub fn collect_for_topic(workdir: &Path, topic: &str) -> Result<Vec<Entry>, String> {
    let journals = journal::read_all(workdir)?;
    let mut collected: Vec<Entry> = vec![];
    for jf in &journals {
        for (id, t) in &jf.fm.topics {
            if t == topic {
                if let Some(e) = jf.entries.iter().find(|e| &e.id == id) {
                    collected.push(e.clone());
                }
            }
        }
    }
    if collected.is_empty() {
        return Err(format!("主题「{}」暂无归属条目,先用 material organize 分组", topic));
    }
    collected.sort_by(|a, b| (a.file.clone(), a.id.clone()).cmp(&(b.file.clone(), b.id.clone())));
    Ok(collected)
}

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

/// 执行 distill:聚合 → LLM 过滤次要信息并统一表达 → 初稿 materials/<topic>.md。
pub fn distill(workdir: &Path, topic: &str) -> Result<PathBuf, String> {
    let collected = collect_for_topic(workdir, topic)?;

    // 聚合文本(LLM 输入,带来源)
    let mut aggregate = String::new();
    for e in &collected {
        if !aggregate.is_empty() {
            aggregate.push('\n');
        }
        aggregate.push_str(&format!("【{}】\n{}\n", e.reference(), e.text));
    }

    let prompt = build_draft_prompt(topic, &aggregate);
    let draft = crate::organize::run_llm(&prompt)?;

    // front matter:topic + sources
    let mut fm = FrontMatter::default();
    fm.topic = Some(topic.to_string());
    for e in &collected {
        fm.sources.push(format!("journal/{}", e.reference()));
    }

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

    fn seed_journal(dir: &Path) {
        let jdir = dir.join("journal");
        fs::create_dir_all(&jdir).unwrap();
        fs::write(
            jdir.join("2026-08-15.md"),
            "---\ntopics:\n  \"09-30\": 宣传册\n  \"12-15\": 内容策略\n---\n\n## 09:30\n宣传册想法一\n\n## 12:15\n内容策略想法\n",
        )
        .unwrap();
        fs::write(
            jdir.join("2026-08-16.md"),
            "---\ntopics:\n  \"08-00\": 宣传册\n---\n\n## 08:00\n宣传册想法二\n",
        )
        .unwrap();
    }

    #[test]
    fn collect_for_topic_aggregates() {
        let dir = tmpdir("agg");
        seed_journal(&dir);
        let entries = collect_for_topic(&dir, "宣传册").unwrap();
        assert_eq!(entries.len(), 2);
        assert_eq!(entries[0].reference(), "2026-08-15.md#09-30");
        assert_eq!(entries[1].reference(), "2026-08-16.md#08-00");
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn collect_empty_topic_errors() {
        let dir = tmpdir("empty");
        let out = collect_for_topic(&dir, "不存在");
        assert!(out.is_err());
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
