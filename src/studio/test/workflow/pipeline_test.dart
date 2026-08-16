/// 四命令全链路端到端测试：collect → organize → distill → express，
/// 产物链与 CLI 完全一致（journal → groups → materials → materials/-定稿）。
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;

import 'package:qtcloud_write_studio/workflow/distill.dart';
import 'package:qtcloud_write_studio/workflow/express.dart';
import 'package:qtcloud_write_studio/workflow/journal.dart';
import 'package:qtcloud_write_studio/workflow/organize.dart';

void main() {
  late Directory tempDir;

  setUp(() {
    tempDir = Directory.systemTemp.createTempSync('pipeline_test_');
  });

  tearDown(() {
    if (tempDir.existsSync()) tempDir.deleteSync(recursive: true);
  });

  test('完整流程：收集两条想法 → 分组 → 初稿 → 定稿', () async {
    // 01 收集：两条想法（同一天）
    final now1 = DateTime(2026, 8, 15, 9, 30);
    final now2 = DateTime(2026, 8, 15, 12, 15);
    await collect(tempDir.path, '关于写作动机的思考', now: now1);
    await collect(tempDir.path, '想写一篇品牌故事', now: now2);

    // 02 分组：fake LLM 把两条归到同一主题
    Future<String> fakeLlm(String prompt) async {
      if (prompt.contains('来源文件名#条目ID')) {
        return '---\ntopics:\n'
            '  "2026-08-15.md#09-30": 创作动机\n'
            '  "2026-08-15.md#12-15": 创作动机\n'
            '---';
      }
      if (prompt.contains('形成一篇初稿')) return '这是初稿。';
      return '这是定稿。';
    }

    final updated = await organize(tempDir.path, fakeLlm);
    expect(updated, 2);
    final groups = await writeGroups(tempDir.path);
    expect(groups.single, p.join(tempDir.path, 'groups', '创作动机.md'));

    // 03 初稿
    final draft = await distill(tempDir.path, '创作动机', fakeLlm);
    expect(draft, p.join(tempDir.path, 'materials', '创作动机.md'));
    expect(File(draft).readAsStringSync(), contains('这是初稿。'));

    // 04 定稿
    final finalDoc = await express(tempDir.path, '创作动机', llm: fakeLlm);
    expect(finalDoc, p.join(tempDir.path, 'materials', '创作动机-定稿.md'));
    expect(File(finalDoc).readAsStringSync(), '这是定稿。');

    // 产物链完整：4 个产物目录/文件齐备
    expect(Directory(p.join(tempDir.path, 'journal')).existsSync(), isTrue);
    expect(Directory(p.join(tempDir.path, 'groups')).existsSync(), isTrue);
    expect(Directory(p.join(tempDir.path, 'materials')).existsSync(), isTrue);
    expect(File(p.join(tempDir.path, 'journal', '2026-08-15.md')).existsSync(), isTrue);
    expect(File(p.join(tempDir.path, 'groups', '创作动机.md')).existsSync(), isTrue);
    expect(File(p.join(tempDir.path, 'materials', '创作动机.md')).existsSync(), isTrue);
    expect(File(p.join(tempDir.path, 'materials', '创作动机-定稿.md')).existsSync(), isTrue);
  });

  test('organize 无新条目时返回 0（幂等）', () async {
    Future<String> fakeLlm(String prompt) async => '---\ntopics: {}\n---';
    final updated = await organize(tempDir.path, fakeLlm);
    expect(updated, 0);
  });
}
