// 写作工作流引擎 (narrative-engineering)
//
// 新模型:material → outline → draft → final(线性四阶段)。
// `Writing` 聚合根见 writing 模块;素材收集与整理(CODE 循环)见
// journal / organize / distill 模块,CLI 入口为 `material` binary。

pub mod distill;
pub mod frontmatter;
pub mod journal;
pub mod organize;
pub mod writing;

pub use writing::{Writing, WritingStatus};
