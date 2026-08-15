//! E-Express:素材 → 成稿。
//!
//! 根据写作目标判断表达方式;未提供目标时,默认由 LLM 根据素材内容
//! 自动判断写作意图。输出 `materials/<topic>-成稿.md`。

use std::fs;
use std::path::{Path, PathBuf};

/// 执行 express:读聚合素材 → LLM 生成成稿。
/// `goal` 为 None 时自动根据内容判断写作意图。
pub fn express(workdir: &Path, topic: &str, goal: Option<&str>) -> Result<PathBuf, String> {
    let src = workdir.join("materials").join(format!("{}.md", topic));
    let material = fs::read_to_string(&src).map_err(|e| format!("读素材 {}: {e}", src.display()))?;
    let goal_line = match goal {
        Some(g) => g.to_string(),
        None => "根据素材内容自动判断写作意图".to_string(),
    };
    let prompt = format!(
        "以下是一份写作素材(主题:{})。\n\
         写作目标:{}\n\
         请根据写作目标生成成稿(markdown,与素材同语言)。只输出成稿,不要解释。\n\n素材:\n{}",
        topic, goal_line, material
    );
    let draft = crate::organize::run_llm(&prompt)?;
    let out = workdir.join("materials").join(format!("{}-成稿.md", topic));
    fs::write(&out, draft).map_err(|e| format!("write {}: {e}", out.display()))?;
    Ok(out)
}
