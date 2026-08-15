//! 极简 YAML front matter 解析/序列化。
//!
//! 仅支持本工具需要的子集:
//! ```yaml
//! ---
//! topic: 宣传册            # 素材文件的主题(可选)
//! topics:                  # 日志文件的条目归属
//!   "09-30": 宣传册
//! sources:                 # 素材文件的来源引用(可选)
//!   - journal/2026-08-15.md#09-30
//! ---
//! ```

use std::collections::BTreeMap;

/// front matter 数据。
#[derive(Debug, Default, Clone, PartialEq)]
pub struct FrontMatter {
    /// 日志条目归属:条目 id → 主题
    pub topics: BTreeMap<String, String>,
    /// 素材自身的主题(用于 materials/*.md)
    pub topic: Option<String>,
    /// 来源引用列表(用于 materials/*.md)
    pub sources: Vec<String>,
}

/// 解析文档,返回 (front matter, 正文)。无 front matter 时返回 (None, 全文)。
pub fn parse(content: &str) -> (Option<FrontMatter>, String) {
    let Some(rest) = content.strip_prefix("---\n") else {
        return (None, content.to_string());
    };
    let Some(end) = rest.find("\n---") else {
        return (None, content.to_string());
    };
    let fm_text = &rest[..end];
    let body = rest[end + 4..].trim_start_matches('\n');

    let mut fm = FrontMatter::default();
    let mut current_key: Option<String> = None;
    for line in fm_text.lines() {
        let trimmed = line.trim();
        if line.starts_with(' ') || line.starts_with('\t') {
            // 缩进条目:key: value 或 - item
            if let Some(key) = &current_key {
                if let Some(item) = trimmed.strip_prefix("- ") {
                    if key == "sources" {
                        fm.sources.push(item.trim().to_string());
                    }
                } else if let Some((k, v)) = trimmed.split_once(':') {
                    let k = k.trim().trim_matches('"').to_string();
                    let v = v.trim().trim_matches('"').to_string();
                    if key == "topics" {
                        fm.topics.insert(k, v);
                    }
                }
            }
        } else if let Some((k, v)) = trimmed.split_once(':') {
            let k = k.trim();
            let v = v.trim();
            match k {
                "topics" | "sources" => current_key = Some(k.to_string()),
                "topic" => {
                    fm.topic = if v.is_empty() {
                        None
                    } else {
                        Some(v.trim_matches('"').to_string())
                    }
                }
                _ => current_key = Some(k.to_string()),
            }
        }
    }
    (Some(fm), body.to_string())
}

/// 渲染 front matter(带 `---` 包裹)。
pub fn render(fm: &FrontMatter) -> String {
    let mut out = String::from("---\n");
    if let Some(t) = &fm.topic {
        out.push_str(&format!("topic: {}\n", t));
    }
    if !fm.topics.is_empty() {
        out.push_str("topics:\n");
        for (k, v) in &fm.topics {
            out.push_str(&format!("  \"{}\": {}\n", k, v));
        }
    }
    if !fm.sources.is_empty() {
        out.push_str("sources:\n");
        for s in &fm.sources {
            out.push_str(&format!("  - {}\n", s));
        }
    }
    out.push_str("---\n");
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_with_topics() {
        let doc = "---\ntopics:\n  \"09-30\": 宣传册\n  \"12-15\": 内容策略\n---\n\n## 09-30\n正文";
        let (fm, body) = parse(doc);
        let fm = fm.expect("should have front matter");
        assert_eq!(fm.topics.get("09-30"), Some(&"宣传册".to_string()));
        assert_eq!(fm.topics.get("12-15"), Some(&"内容策略".to_string()));
        assert!(body.starts_with("## 09-30"));
    }

    #[test]
    fn parse_with_topic_and_sources() {
        let doc = "---\ntopic: 宣传册\ntopics:\n  \"09-30\": 宣传册\nsources:\n  - journal/2026-08-15.md#09-30\n---\n\n正文";
        let (fm, _) = parse(doc);
        let fm = fm.expect("should have front matter");
        assert_eq!(fm.topic.as_deref(), Some("宣传册"));
        assert_eq!(fm.sources, vec!["journal/2026-08-15.md#09-30".to_string()]);
    }

    #[test]
    fn parse_no_front_matter() {
        let doc = "## 09:30\n纯正文";
        let (fm, body) = parse(doc);
        assert!(fm.is_none());
        assert_eq!(body, doc);
    }

    #[test]
    fn render_roundtrip() {
        let mut fm = FrontMatter::default();
        fm.topic = Some("宣传册".into());
        fm.topics.insert("09-30".into(), "宣传册".into());
        fm.sources.push("journal/2026-08-15.md#09-30".into());
        let doc = render(&fm);
        let (parsed, _) = parse(&doc);
        assert_eq!(parsed, Some(fm));
    }
}
