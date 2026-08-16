/// journal 读写测试（与 CLI journal.rs 行为对齐）。
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;

import 'package:qtcloud_write_studio/workflow/journal.dart';

void main() {
  late Directory tempDir;

  setUp(() {
    tempDir = Directory.systemTemp.createTempSync('journal_test_');
  });

  tearDown(() {
    if (tempDir.existsSync()) tempDir.deleteSync(recursive: true);
  });

  test('readEntries 解析条目与 id', () {
    const body = '## 09:30\n宣传册逻辑\n\n## 12:15\n每一篇独立发布\n';
    final entries = readEntries(body);
    expect(entries.length, 2);
    expect(entries[0].id, '09-30');
    expect(entries[0].text, '宣传册逻辑');
    expect(entries[1].title, '12:15');
    expect(entries[1].reference(), '#12-15');
  });

  test('readEntries 解析序号 id（同分钟多条）', () {
    const body = '## 19:53\n第一条\n\n## 19:53-2\n第二条\n\n## 19:53-3\n第三条\n';
    final entries = readEntries(body);
    expect(entries.length, 3);
    expect(entries[0].id, '19-53');
    expect(entries[1].id, '19-53-2');
    expect(entries[2].id, '19-53-3');
  });

  test('collect 创建并追加条目（同标题自动序号）', () async {
    final now = DateTime(2026, 8, 16, 9, 30);
    final path = await collect(tempDir.path, '第一条想法', now: now);
    expect(File(path).existsSync(), isTrue);
    await collect(tempDir.path, '第二条想法', now: now);
    final content = File(path).readAsStringSync();
    expect(content, contains('第一条想法'));
    expect(content, contains('第二条想法'));
    final entries = readEntries(content);
    expect(entries.length, 2);
    // 同分钟第二条带 -2 序号
    expect(entries[1].title, '09:30-2');
    expect(entries[1].id, '09-30-2');
    // 文件名为今日日期
    expect(p.basename(path), '2026-08-16.md');
  });

  test('readAll 读取 front matter 与条目', () async {
    final now = DateTime(2026, 8, 15, 9, 30);
    final path = await collect(tempDir.path, '已记录想法', now: now);
    await updateFrontMatter(tempDir.path, p.basename(path), (fm) {
      fm.topics['09-30'] = '宣传册';
    });
    final journals = await readAll(tempDir.path);
    expect(journals.length, 1);
    expect(journals[0].fm.topics['09-30'], '宣传册');
    expect(journals[0].entries.single.text, '已记录想法');
    expect(journals[0].entries.single.file, '2026-08-15.md');
  });
}
