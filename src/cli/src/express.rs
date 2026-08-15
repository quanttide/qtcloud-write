//! E-Express(表达):根据写作目标形成定稿(产物 04)。
//!
//! 输入 distill 初稿 materials/<topic>.md,输出 materials/<topic>-定稿.md。
//! 未提供 --goal 时,由 LLM 根据内容自动判断写作意图作为目标。

use std::fs;
use std::path::{Path, PathBuf};

/// 定稿提示词:输入初稿,按写作目标形成定稿。
pub fn build_finalize_prompt(topic: &str, goal: &str, draft: &str) -> String {
    format!(
        "以下是一篇初稿(主题:{topic})。\n\
         写作目标:{goal}\n\
         请根据写作目标对初稿进行定稿:调整结构、语气与细节,使其符合目标要求,但保持核心内容不变。\n\
         只输出定稿,不要解释。\n\n初稿:\n{draft}"
    )
}

/// 执行 express:读 distill 初稿 → LLM 按目标定稿 → materials/<topic>-定稿.md。
/// `goal` 为 None 时自动判断写作意图。
pub fn express(workdir: &Path, topic: &str, goal: Option<&str>) -> Result<PathBuf, String> {
    let src = workdir.join("materials").join(format!("{}.md", topic));
    let draft = fs::read_to_string(&src)
        .map_err(|e| format!("读初稿 {}: {e}(先运行 material distill <主题> 生成初稿)", src.display()))?;
    let goal = goal.unwrap_or("根据内容自动判断写作意图");
    let prompt = build_finalize_prompt(topic, goal, &draft);
    let final_doc = crate::organize::run_llm(&prompt)?;
    let out = workdir.join("materials").join(format!("{}-定稿.md", topic));
    fs::write(&out, final_doc).map_err(|e| format!("write {}: {e}", out.display()))?;
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn finalize_prompt_contains_goal() {
        let p = build_finalize_prompt("创作动机", "写一篇品牌故事", "初稿正文");
        assert!(p.contains("品牌故事"));
        assert!(p.contains("初稿正文"));
        assert!(p.contains("定稿"));
    }

    #[test]
    fn finalize_prompt_with_auto_goal() {
        let p = build_finalize_prompt("创作动机", "根据内容自动判断写作意图", "初稿正文");
        assert!(p.contains("自动判断"));
    }
}
