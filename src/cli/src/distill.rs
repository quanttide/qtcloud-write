//! D-Distill:按主题聚合日志条目 → materials/<topic>.md(纯拼接)。

use std::fs;
use std::path::{Path, PathBuf};

use crate::frontmatter::FrontMatter;
use crate::journal::{self, Entry};

/// 执行 distill:聚合归属 `topic` 的条目,生成 materials/<topic>.md。
/// 文件已存在时重新生成(幂等)。返回输出路径。
pub fn distill(workdir: &Path, topic: &str) -> Result<PathBuf, String> {
    let journals = journal::read_all(workdir)?;

    // 按 YAML 归属收集条目
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
        return Err(format!("主题「{}」暂无归属条目,先用 material organize 提取主题", topic));
    }

    // 按文件 + 时间排序
    collected.sort_by(|a, b| (a.file.clone(), a.id.clone()).cmp(&(b.file.clone(), b.id.clone())));

    // 素材 front matter
    let mut fm = FrontMatter::default();
    fm.topic = Some(topic.to_string());
    for e in &collected {
        fm.sources.push(format!("journal/{}", e.reference()));
    }

    // 正文:纯聚合拼接,每条带来源引用
    let mut body = String::new();
    for e in &collected {
        if !body.is_empty() {
            body.push('\n');
        }
        body.push_str(&e.text);
        body.push_str(&format!("\n\n> 来源:journal/{}\n", e.reference()));
    }

    let dir = workdir.join("materials");
    fs::create_dir_all(&dir).map_err(|e| format!("mkdir materials: {e}"))?;
    let path = dir.join(format!("{}.md", topic));
    fs::write(&path, format!("{}{}", crate::frontmatter::render(&fm), body))
        .map_err(|e| format!("write {}: {e}", path.display()))?;
    Ok(path)
}

/// 执行 distill 提炼:先聚合,再调 LLM 删除次要信息,输出提炼稿
/// `materials/<topic>-refined.md`(聚合文件保留,人工可对比)。
pub fn distill_refine(workdir: &Path, topic: &str) -> Result<PathBuf, String> {
    let base = distill(workdir, topic)?;
    let material = fs::read_to_string(&base).map_err(|e| format!("读聚合稿: {e}"))?;
    let prompt = format!(
        "以下是从日志聚合的写作素材(主题:{})。\n\
         请删除次要信息、保留要点,输出提炼后的素材(markdown,与素材同语言)。\n\
         只输出提炼结果,不要解释。\n\n素材:\n{}",
        topic, material
    );
    let refined = crate::organize::run_llm(&prompt)?;
    let path = workdir.join("materials").join(format!("{}-refined.md", topic));
    fs::write(&path, refined).map_err(|e| format!("write {}: {e}", path.display()))?;
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

    #[test]
    fn distill_aggregates_by_topic() {
        let dir = tmpdir("agg");
        let jdir = dir.join("journal");
        fs::create_dir_all(&jdir).unwrap();
        // 2026-08-15.md:两条条目,一条归宣传册
        fs::write(
            jdir.join("2026-08-15.md"),
            "---\ntopics:\n  \"09-30\": 宣传册\n  \"12-15\": 内容策略\n---\n\n## 09:30\n宣传册想法一\n\n## 12:15\n内容策略想法\n",
        )
        .unwrap();
        // 2026-08-16.md:一条归宣传册
        fs::write(
            jdir.join("2026-08-16.md"),
            "---\ntopics:\n  \"08-00\": 宣传册\n---\n\n## 08:00\n宣传册想法二\n",
        )
        .unwrap();

        let out = distill(&dir, "宣传册").unwrap();
        let doc = fs::read_to_string(&out).unwrap();
        assert!(doc.contains("topic: 宣传册"));
        assert!(doc.contains("journal/2026-08-15.md#09-30"));
        assert!(doc.contains("journal/2026-08-16.md#08-00"));
        assert!(doc.contains("宣传册想法一"));
        assert!(doc.contains("宣传册想法二"));
        assert!(!doc.contains("内容策略想法"));
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn distill_empty_topic_errors() {
        let dir = tmpdir("empty");
        let out = distill(&dir, "不存在");
        assert!(out.is_err());
        let _ = fs::remove_dir_all(&dir);
    }
}
