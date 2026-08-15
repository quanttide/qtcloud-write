//! E-Express(表达):根据写作目标形成定稿(产物 04)。
//!
//! 输入 distill 初稿 materials/<topic>.md + 分组素材 groups/<topic>.md,
//! 输出 materials/<topic>-定稿.md。参考分组素材保证信息不因过滤而丢失。
//! 未提供 --goal 时,由 LLM 根据内容自动判断写作意图作为目标。

use std::fs;
use std::path::{Path, PathBuf};

/// 定稿提示词:以初稿为底稿、素材补全信息,按写作目标重构定稿。
pub fn build_finalize_prompt(topic: &str, goal: &str, draft: &str, material: &str) -> String {
    format!(
        "以下是一篇初稿(主题:{topic})与对应的完整分组素材。\n\
         写作目标:{goal}\n\
         请以初稿为底稿完成定稿:\n\
         - 初稿提供内容骨架与统一基调,在此基础上按写作目标重构结构与语气\n\
         - 分组素材中的有效信息(初稿未采用的细节)应自然融入,不应丢失\n\
         - 定稿是一篇完整、有层次的成品,而不是初稿的简单修补\n\
         只输出定稿,不要解释。\n\n初稿:\n{draft}\n\n分组素材:\n{material}"
    )
}

/// 执行 express:读初稿 + 分组素材 → LLM 按目标定稿 → materials/<topic>-定稿.md。
/// `goal` 为 None 时自动判断写作意图。
pub fn express(workdir: &Path, topic: &str, goal: Option<&str>) -> Result<PathBuf, String> {
    let src = workdir.join("materials").join(format!("{}.md", topic));
    let draft = fs::read_to_string(&src)
        .map_err(|e| format!("读初稿 {}: {e}(先运行 material distill <主题> 生成初稿)", src.display()))?;
    let gsrc = workdir.join("groups").join(format!("{}.md", topic));
    let group = fs::read_to_string(&gsrc)
        .map_err(|e| format!("读分组 {}: {e}(先运行 material organize 生成分组)", gsrc.display()))?;
    let (_, material) = crate::frontmatter::parse(&group);

    let goal = goal.unwrap_or("根据内容自动判断写作意图");
    let prompt = build_finalize_prompt(topic, goal, &draft, &material);
    let final_doc = crate::organize::run_llm(&prompt)?;
    let out = workdir.join("materials").join(format!("{}-定稿.md", topic));
    fs::write(&out, final_doc).map_err(|e| format!("write {}: {e}", out.display()))?;
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn finalize_prompt_contains_goal_and_material() {
        let p = build_finalize_prompt("创作动机", "写一篇品牌故事", "初稿正文", "分组素材");
        assert!(p.contains("品牌故事"));
        assert!(p.contains("初稿正文"));
        assert!(p.contains("分组素材"));
        assert!(p.contains("定稿"));
    }

    #[test]
    fn finalize_prompt_with_auto_goal() {
        let p = build_finalize_prompt("创作动机", "根据内容自动判断写作意图", "初稿正文", "素材");
        assert!(p.contains("自动判断"));
    }
}
