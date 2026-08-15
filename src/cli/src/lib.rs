// 写作工作流引擎 (narrative-engineering) — 壳
//
// 旧实现(范畴论路线, material → outline → firstDraft → finalDraft
// + review/reflect/rewrite 循环)已移除,完整版本见 git 历史 b47f0b6。
//
// 新模型:material → outline → draft → final(线性四阶段)。
// 当前壳定义了写作云的基本单位 `Writing` 及其状态模型。

pub mod writing;

pub use writing::{Writing, WritingKind, WritingStatus};
