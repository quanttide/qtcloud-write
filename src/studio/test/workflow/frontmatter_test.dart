/// front matter 解析/渲染测试（与 CLI frontmatter.rs 行为对齐）。
library;

import 'package:flutter_test/flutter_test.dart';

import 'package:qtcloud_write_studio/workflow/frontmatter.dart';

void main() {
  test('解析 topics 归属', () {
    const doc = '---\ntopics:\n  "09-30": 宣传册\n  "12-15": 内容策略\n---\n\n## 09-30\n正文';
    final (fm, body) = FrontMatter.parse(doc);
    final f = fm!;
    expect(f.topics['09-30'], '宣传册');
    expect(f.topics['12-15'], '内容策略');
    expect(body.startsWith('## 09-30'), isTrue);
  });

  test('解析 topic 与 sources', () {
    const doc =
        '---\ntopic: 宣传册\ntopics:\n  "09-30": 宣传册\nsources:\n  - journal/2026-08-15.md#09-30\n---\n\n正文';
    final (fm, _) = FrontMatter.parse(doc);
    final f = fm!;
    expect(f.topic, '宣传册');
    expect(f.sources, ['journal/2026-08-15.md#09-30']);
  });

  test('无 front matter 返回 null 与全文', () {
    const doc = '## 09:30\n纯正文';
    final (fm, body) = FrontMatter.parse(doc);
    expect(fm, isNull);
    expect(body, doc);
  });

  test('render 往返一致', () {
    final fm = FrontMatter(topic: '宣传册');
    fm.topics['09-30'] = '宣传册';
    fm.sources.add('journal/2026-08-15.md#09-30');
    final doc = fm.render();
    final (parsed, _) = FrontMatter.parse(doc);
    final p = parsed!;
    expect(p.topic, '宣传册');
    expect(p.topics['09-30'], '宣传册');
    expect(p.sources, ['journal/2026-08-15.md#09-30']);
  });
}
