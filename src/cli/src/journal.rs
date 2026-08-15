//! 日志(journal)读写:collect 记录 + 条目解析。
//!
//! 布局:<workdir>/journal/YYYY-MM-DD.md,条目格式:
//! ```markdown
//! ## 09:30
//! 想法文本
//! ```

use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};

use crate::frontmatter::{self, FrontMatter};

/// 一条日志条目。
#[derive(Debug, Clone, PartialEq)]
pub struct Entry {
    /// 来源文件名,如 `2026-08-15.md`
    pub file: String,
    /// 条目 id,时间戳连字符形式,如 `09-30`
    pub id: String,
    /// 条目标题,如 `09:30`
    pub title: String,
    /// 条目正文
    pub text: String,
}

impl Entry {
    /// 引用形式:`2026-08-15.md#09-30`
    pub fn reference(&self) -> String {
        format!("{}#{}", self.file, self.id)
    }
}

/// 一个日志文件:文件名 + front matter + 条目列表。
#[derive(Debug, Clone, PartialEq)]
pub struct JournalFile {
    pub file: String,
    pub fm: FrontMatter,
    pub entries: Vec<Entry>,
}

pub fn journal_dir(workdir: &Path) -> PathBuf {
    workdir.join("journal")
}

/// C-Capture:把一条想法追加到今日日志(自动 ## HH:MM 条目)。
pub fn collect(workdir: &Path, text: &str) -> Result<PathBuf, String> {
    let dir = journal_dir(workdir);
    fs::create_dir_all(&dir).map_err(|e| format!("mkdir journal: {e}"))?;
    let now = chrono::Local::now();
    let path = dir.join(format!("{}.md", now.format("%Y-%m-%d")));
    let title = now.format("%H:%M").to_string();

    let mut content = String::new();
    let mut existing_ids: Vec<String> = vec![];
    if path.exists() {
        let prev = fs::read_to_string(&path).map_err(|e| format!("read: {e}"))?;
        existing_ids = read_entries(&prev).into_iter().map(|e| e.id).collect();
        content.push_str(&prev);
        if !content.ends_with('\n') {
            content.push('\n');
        }
        content.push('\n');
    }
    // 标题带序号(同分钟多条):`## 19:53`、`## 19:53-2`、`## 19:53-3`…
    let base = now.format("%H-%M").to_string();
    let same = existing_ids
        .iter()
        .filter(|id| **id == base || id.starts_with(&format!("{}-", base)))
        .count();
    let title = if same == 0 {
        title
    } else {
        format!("{}-{}", title, same + 1)
    };
    content.push_str(&format!("## {}\n{}\n", title, text.trim()));
    fs::write(&path, content).map_err(|e| format!("write: {e}"))?;
    Ok(path)
}

/// 解析日志正文为条目列表(识别 `## ` 小节)。
/// id 直接由标题生成:`## 19:53` → `19-53`;`## 19:53-2` → `19-53-2`
/// (同分钟多条时 collect 会在标题中写序号,故 id 稳定、删除条目不漂移)。
pub fn read_entries(body: &str) -> Vec<Entry> {
    let mut out: Vec<Entry> = vec![];
    let mut current: Option<(String, String, Vec<String>)> = None; // (title, id, lines)
    for line in body.lines() {
        if let Some(title) = line.strip_prefix("## ") {
            if let Some((t, id, lines)) = current.take() {
                out.push(Entry {
                    file: String::new(), // 由调用方填充
                    id,
                    title: t,
                    text: lines.join("\n").trim().to_string(),
                });
            }
            let title = title.trim().to_string();
            let id = title.replace(':', "-");
            current = Some((title, id, vec![]));
        } else if let Some((_, _, lines)) = &mut current {
            lines.push(line.to_string());
        }
    }
    if let Some((t, id, lines)) = current.take() {
        out.push(Entry {
            file: String::new(),
            id,
            title: t,
            text: lines.join("\n").trim().to_string(),
        });
    }
    out
}

/// 读取全部日志文件(按文件名排序),解析 front matter 与条目。
pub fn read_all(workdir: &Path) -> Result<Vec<JournalFile>, String> {
    let dir = journal_dir(workdir);
    let mut out = vec![];
    if !dir.exists() {
        return Ok(out);
    }
    for entry in fs::read_dir(&dir).map_err(|e| format!("read_dir journal: {e}"))? {
        let path = entry.map_err(|e| format!("read_dir entry: {e}"))?.path();
        if path.extension().map(|e| e == "md").unwrap_or(false) {
            let content = fs::read_to_string(&path).map_err(|e| format!("read {}: {e}", path.display()))?;
            let (fm, body) = frontmatter::parse(&content);
            let file = path.file_name().unwrap().to_string_lossy().to_string();
            let mut entries = read_entries(&body);
            for e in &mut entries {
                e.file = file.clone();
            }
            out.push(JournalFile {
                file,
                fm: fm.unwrap_or_default(),
                entries,
            });
        }
    }
    out.sort_by(|a, b| a.file.cmp(&b.file));
    Ok(out)
}

/// 更新单个日志文件的 front matter:读 → 闭包修改 → 写回。
/// 文件原本无 front matter 时,若闭包产生了非空 topics/sources 则创建。
pub fn update_front_matter(
    workdir: &Path,
    file: &str,
    f: impl FnOnce(&mut FrontMatter),
) -> Result<(), String> {
    let path = journal_dir(workdir).join(file);
    let content = fs::read_to_string(&path).map_err(|e| format!("read {}: {e}", path.display()))?;
    let (fm, body) = frontmatter::parse(&content);
    let mut fm = fm.unwrap_or_default();
    f(&mut fm);
    let new_doc = format!("{}{}", frontmatter::render(&fm), body);
    fs::write(&path, new_doc).map_err(|e| format!("write {}: {e}", path.display()))?;
    Ok(())
}

/// 各日志条目 id → 主题(合并所有文件)。
pub fn all_topic_assignments(journals: &[JournalFile]) -> BTreeMap<String, String> {
    let mut out = BTreeMap::new();
    for jf in journals {
        for (k, v) in &jf.fm.topics {
            out.insert(format!("{}#{}", jf.file, k), v.clone());
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_entries() {
        let body = "## 09:30\n宣传册逻辑\n\n## 12:15\n每一篇独立发布\n";
        let entries = read_entries(body);
        assert_eq!(entries.len(), 2);
        assert_eq!(entries[0].id, "09-30");
        assert_eq!(entries[0].text, "宣传册逻辑");
        assert_eq!(entries[1].title, "12:15");
        assert_eq!(entries[1].reference(), "#12-15");
    }

    #[test]
    fn parse_entries_with_sequence_ids() {
        let body = "## 19:53\n第一条\n\n## 19:53-2\n第二条\n\n## 19:53-3\n第三条\n";
        let entries = read_entries(body);
        assert_eq!(entries.len(), 3);
        assert_eq!(entries[0].id, "19-53");
        assert_eq!(entries[1].id, "19-53-2");
        assert_eq!(entries[2].id, "19-53-3");
    }

    #[test]
    fn collect_creates_and_appends() {
        let dir = std::env::temp_dir().join(format!("material-test-{}", std::process::id()));
        let _ = fs::remove_dir_all(&dir);
        let path = collect(&dir, "第一条想法").unwrap();
        assert!(path.exists());
        collect(&dir, "第二条想法").unwrap();
        let content = fs::read_to_string(&path).unwrap();
        assert!(content.contains("第一条想法"));
        assert!(content.contains("第二条想法"));
        let entries = read_entries(&content);
        assert_eq!(entries.len(), 2);
        let _ = fs::remove_dir_all(&dir);
    }
}
