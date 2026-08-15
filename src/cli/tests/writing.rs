use narrative_engineering::{Writing, WritingStatus};

#[test]
fn new_writing_starts_at_material() {
    let w = Writing::new("w1");
    assert_eq!(w.status, WritingStatus::Material);
}

#[test]
fn status_advances_linearly() {
    assert_eq!(WritingStatus::Material.advance(), Some(WritingStatus::Outline));
    assert_eq!(WritingStatus::Outline.advance(), Some(WritingStatus::Draft));
    assert_eq!(WritingStatus::Draft.advance(), Some(WritingStatus::Final));
    assert_eq!(WritingStatus::Final.advance(), None);
}

#[test]
fn writing_advance_updates_status() {
    let mut w = Writing::new("w2");
    assert_eq!(w.advance(), Some(WritingStatus::Outline));
    assert_eq!(w.status, WritingStatus::Outline);
}

#[test]
fn final_cannot_advance() {
    let mut w = Writing::new("w3");
    for _ in 0..3 {
        w.advance();
    }
    assert_eq!(w.status, WritingStatus::Final);
    assert_eq!(w.advance(), None);
    assert_eq!(w.status, WritingStatus::Final);
}
