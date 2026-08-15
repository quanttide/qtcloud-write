//! O-Organize:LLM 从日志提取主题,更新各日志文件 YAML 归属。
//!
//! 流程:读全部日志 → 收集未标注条目 → LLM 建议主题 → 合并写入
//! 各文件 front matter(仅写入未标注条目,保留人工标注)。

use std::collections::BTreeMap;
use std::path::Path;

use quanttide_agent::llm::{CompleteOptions, LLM};
use quanttide_agent::message::Message;

use crate::frontmatter;
use crate::journal::{self, JournalFile};

/// 调用 LLM(与 qtdata CLI 同款用法,读 DEEPSEEK_API_KEY)。
pub fn run_llm(prompt: &str) -> Result<String, String> {
    let api_key = std::env::var("DEEPSEEK_API_KEY")
        .map_err(|_| "DEEPSEEK_API_KEY 未设置".to_string())?;
    let llm = LLM::new("deepseek-v4-flash", "https://api.deepseek.com", &api_key);
    let msg = Message::new("user", prompt);
    let opts = CompleteOptions {
        temperature: Some(0.1),
        ..Default::default()
    };
    llm.complete(&[msg], opts)
        .map(|r| r.content)
        .map_err(|e| format!("llm: {e}"))
}

/// 构建 prompt:列出所有未标注条目,要求 LLM 输出 YAML 归属。
fn build_prompt(journals: &[JournalFile]) -> String {
    let mut lines = vec![];
    for jf in journals {
        for e in &jf.entries {
            if !jf.fm.topics.contains_key(&e.id) {
                lines.push(format!("{}#{}: {}", e.file, e.id, e.text));
            }
        }
    }
    if lines.is_empty() {
        return String::new();
    }
    format!(
        "以下是一批日志条目(来源文件名#条目ID: 内容):\n{}\n\n\
         为每条条目分配一个简短主题名(可复用、中文,2-6 字)。只输出 YAML:\n\
         ---\ntopics:\n  \"来源文件名#条目ID\": 主题名\n---",
        lines.join("\n")
    )
}

/// 解析 LLM 输出的归属映射(容忍 ```yaml 围栏与缺失的 ---)。
pub fn parse_llm_output(text: &str) -> BTreeMap<String, String> {
    let t = text.trim().trim_matches('`');
    let t = t.strip_prefix("yaml\n").unwrap_or(t);
    let doc = if t.starts_with("---") {
        t.to_string()
    } else {
        format!("---\n{}\n---", t)
    };
    frontmatter::parse(&doc)
        .0
        .map(|fm| fm.topics)
        .unwrap_or_default()
}

/// 执行 organize:返回更新的条目数。
pub fn organize(workdir: &Path) -> Result<usize, String> {
    let journals = journal::read_all(workdir)?;
    let prompt = build_prompt(&journals);
    if prompt.is_empty() {
        return Ok(0);
    }
    let output = run_llm(&prompt)?;
    let suggestions = parse_llm_output(&output);
    if suggestions.is_empty() {
        return Err(format!("LLM 输出无法解析为主题归属: {}", output));
    }

    let mut updated = 0;
    for jf in &journals {
        // 收集本文件内未标注条目的建议(支持 "文件#id" 与纯 "id" 两种 key)
        let mut changes: BTreeMap<String, String> = BTreeMap::new();
        for (key, topic) in &suggestions {
            let (file, id) = match key.split_once('#') {
                Some((f, i)) => (f, i),
                None => ("", key.as_str()),
            };
            if !file.is_empty() && file != jf.file {
                continue;
            }
            let exists = jf.entries.iter().any(|e| e.id == id);
            if exists && !jf.fm.topics.contains_key(id) {
                changes.insert(id.to_string(), topic.clone());
            }
        }
        if !changes.is_empty() {
            let c = changes.clone();
            journal::update_front_matter(workdir, &jf.file, move |fm| {
                for (id, topic) in &c {
                    fm.topics.insert(id.clone(), topic.clone());
                }
            })?;
            updated += changes.len();
        }
    }
    Ok(updated)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_yaml_with_fences() {
        let out = "```yaml\n---\ntopics:\n  \"2026-08-15.md#09-30\": 宣传册\n---\n```";
        let m = parse_llm_output(out);
        assert_eq!(m.get("2026-08-15.md#09-30"), Some(&"宣传册".to_string()));
    }

    #[test]
    fn parse_yaml_bare() {
        let out = "topics:\n  \"09-30\": 内容策略";
        let m = parse_llm_output(out);
        assert_eq!(m.get("09-30"), Some(&"内容策略".to_string()));
    }

    #[test]
    fn build_prompt_skips_assigned() {
        let mut fm = frontmatter::FrontMatter::default();
        fm.topics.insert("09-30".into(), "宣传册".into());
        let jf = JournalFile {
            file: "2026-08-15.md".into(),
            fm,
            entries: vec![
                journal::Entry { file: "2026-08-15.md".into(), id: "09-30".into(), title: "09:30".into(), text: "已标注".into() },
                journal::Entry { file: "2026-08-15.md".into(), id: "12-15".into(), title: "12:15".into(), text: "未标注".into() },
            ],
        };
        let prompt = build_prompt(&[jf]);
        assert!(prompt.contains("2026-08-15.md#12-15"));
        assert!(!prompt.contains("#09-30"));
    }
}
