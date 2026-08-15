//! 写作 — 写作云的基本单位及其状态模型。
//!
//! 新模型:material → outline → draft → final(线性四阶段,只前进不后退)。
//! 旧模型(范畴论路线,含 review/reflect/rewrite 循环与计数)已废弃,见 git 历史 b47f0b6。

/// 写作状态 — 文本生命周期的线性四阶段。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum WritingStatus {
    /// 素材:灵感碎片、收集的引用与材料
    Material,
    /// 大纲:结构规划
    Outline,
    /// 草稿:正文写作
    Draft,
    /// 定稿:完成
    Final,
}

impl WritingStatus {
    /// 前进到下一阶段;`Final` 之后返回 `None`(不可前进)。
    pub fn advance(self) -> Option<Self> {
        match self {
            Self::Material => Some(Self::Outline),
            Self::Outline => Some(Self::Draft),
            Self::Draft => Some(Self::Final),
            Self::Final => None,
        }
    }
}

/// 写作形态 — 同一生命周期下的不同产物类型。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum WritingKind {
    /// 文章:单篇文本
    Article,
    /// 书:多章节长文本
    Book,
}

/// 写作 — 写作云的基本单位(聚合根)。
///
/// 对应文档云的基本单位 `Document`:写作云的产物是"写作",而非"文档"。
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Writing {
    pub id: String,
    pub kind: WritingKind,
    pub status: WritingStatus,
}

impl Writing {
    /// 新建写作,状态从 `Material` 开始。
    pub fn new(id: impl Into<String>, kind: WritingKind) -> Self {
        Self {
            id: id.into(),
            kind,
            status: WritingStatus::Material,
        }
    }

    /// 推进到下一阶段;已定稿则保持不动并返回 `None`。
    pub fn advance(&mut self) -> Option<WritingStatus> {
        let next = self.status.advance()?;
        self.status = next;
        Some(next)
    }
}
