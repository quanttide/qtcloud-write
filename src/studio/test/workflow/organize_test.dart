/// organize 测试：prompt 构建、LLM 输出解析、端到端分组（与 CLI organize.rs 对齐）。
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;

import 'package:qtcloud_write_studio/workflow/frontmatter.dart';
import 'package:qtcloud_write_studio/workflow/journal.dart';
import 'package:qtcloud_write_studio/workflow/organize.dart';

void main() {
  late Directory tempDir;

  setUp(() {
    tempDir = Directory.systemTemp.createTempSync('organize_test_');
  });

  tearDown(() {
    if (tempDir.existsSync()) tempDir.deleteSync(recursive: true);
  });

  test('parseLlmOutput 容忍 yaml 围栏', () {
    const out =
        '```yaml\n---\ntopics:\n  "2026-08-15.md#09-30": 宣传册\n---\n```';
    final m = parseLlmOutput(out);
    expect(m['2026-08-15.md#09-30'], '宣传册');
  });

  test('parseLlmOutput 容忍裸 YAML', () {
    const out = 'topics:\n  "09-30": 内容策略';
    final m = parseLlmOutput(out);
    expect(m['09-30'], '内容策略');
  });

  test('buildPrompt 跳过已标注条目', () {
    final fm = FrontMatter();
    fm.topics['09-30'] = '宣传册';
    final jf = JournalFile(
      file: '2026-08-15.md',
      fm: fm,
      entries: const [
        Entry(file: '2026-08-15.md', id: '09-30', title: '09:30', text: '已标注'),
        Entry(file: '2026-08-15.md', id: '12-15', title: '12:15', text: '未标注'),
      ],
    );
    final prompt = buildPrompt([jf]);
    expect(prompt, contains('2026-08-15.md#12-15'));
    expect(prompt, isNot(contains('#09-30')));
  });

  test('organize 端到端：LLM 建议 → 写入归属 → writeGroups 生成分组', () async {
    // 造两条未标注条目
    final now = DateTime(2026, 8, 15, 9, 30);
    await collect(tempDir.path, '宣传册逻辑', now: now);
    final now2 = DateTime(2026, 8, 15, 12, 15);
    await collect(tempDir.path, '每一篇独立发布', now: now2);

    // fake LLM：返回归属建议
    Future<String> fakeLlm(String prompt) async {
      return '---\ntopics:\n'
          '  "2026-08-15.md#09-30": 宣传册\n'
          '  "2026-08-15.md#12-15": 内容策略\n'
          '---';
    }

    final updated = await organize(tempDir.path, fakeLlm);
    expect(updated, 2);

    // 归属已写入日志 front matter
    final journals = await readAll(tempDir.path);
    expect(journals.single.fm.topics['09-30'], '宣传册');
    expect(journals.single.fm.topics['12-15'], '内容策略');

    // writeGroups 生成 groups/<主题>.md
    final groups = await writeGroups(tempDir.path);
    expect(groups.length, 2);
    final groupFile = File(p.join(tempDir.path, 'groups', '宣传册.md'));
    expect(groupFile.existsSync(), isTrue);
    final content = groupFile.readAsStringSync();
    expect(content, contains('宣传册逻辑'));
    expect(content, contains('> 来源:journal/2026-08-15.md#09-30'));
    expect(content, startsWith('---\ntopic: 宣传册\n'));
  });
}
