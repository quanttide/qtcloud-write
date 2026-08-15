//! E-Express:初稿与定稿。
//!
//! 产物链:express <主题> 基于提炼稿生成**初稿**(04);
//! express <主题> --goal 基于初稿生成**定稿**(05,按写作目标)。
//! 未提供目标时,初稿由 LLM 根据素材内容自动判断写作意图。

use std::fs;
use std::path::{Path, PathBuf};

/// 初稿提示词:输入提炼稿,自动判断写作意图,生成初稿。
pub fn build_draft_prompt(topic: &str, material: &str) -> String {
    format!(
        "以下是一份提炼后的写作素材(主题:{topic})。\n\
         请根据素材内容自动判断写作意图,生成一篇初稿(markdown,与素材同语言)。\n\
         要求:忠实于素材的核心内容,结构完整,语言自然。只输出初稿,不要解释。\n\n素材:\n{material}"
    )
}

/// 定稿提示词:输入初稿,按写作目标定稿。
pub fn build_finalize_prompt(topic: &str, goal: &str, draft: &str) -> String {
    format!(
        "以下是一篇初稿(主题:{topic})。\n\
         写作目标:{goal}\n\
         请对初稿进行定稿:按写作目标调整结构、语气与细节,保持核心内容不变。\n\
         只输出定稿,不要解释。\n\n初稿:\n{draft}"
    )
}

/// 执行 express。
/// - `goal` 为 None:04 初稿,输入 materials/<topic>.md → materials/<topic>-初稿.md
/// - `goal` 为 Some:05 定稿,输入 materials/<topic>-初稿.md → materials/<topic>-定稿.md
pub fn express(workdir: &Path, topic: &str, goal: Option<&str>) -> Result<PathBuf, String> {
    match goal {
        None => {
            let src = workdir.join("materials").join(format!("{}.md", topic));
            let material =
                fs::read_to_string(&src).map_err(|e| format!("读提炼稿 {}: {e}", src.display()))?;
            let prompt = build_draft_prompt(topic, &material);
            let draft = crate::organize::run_llm(&prompt)?;
            let out = workdir.join("materials").join(format!("{}-初稿.md", topic));
            fs::write(&out, draft).map_err(|e| format!("write {}: {e}", out.display()))?;
            Ok(out)
        }
        Some(goal) => {
            let src = workdir.join("materials").join(format!("{}-初稿.md", topic));
            let draft = fs::read_to_string(&src)
                .map_err(|e| format!("读初稿 {}: {e}(先运行 material express <主题> 生成初稿)", src.display()))?;
            let prompt = build_finalize_prompt(topic, goal, &draft);
            let final_doc = crate::organize::run_llm(&prompt)?;
            let out = workdir.join("materials").join(format!("{}-定稿.md", topic));
            fs::write(&out, final_doc).map_err(|e| format!("write {}: {e}", out.display()))?;
            Ok(out)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn draft_prompt_contains_material() {
        let p = build_draft_prompt("创作心路", "提炼素材");
        assert!(p.contains("创作心路"));
        assert!(p.contains("提炼素材"));
        assert!(p.contains("自动判断写作意图"));
    }

    #[test]
    fn finalize_prompt_contains_goal() {
        let p = build_finalize_prompt("创作心路", "写一篇品牌故事", "初稿正文");
        assert!(p.contains("品牌故事"));
        assert!(p.contains("初稿正文"));
        assert!(p.contains("定稿"));
    }
}
