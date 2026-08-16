/// distill / express 测试：提示词构建 + 端到端产物（与 CLI 对齐）。
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
    tempDir = Directory.systemTemp.createTempSync('distill_express_test_');
  });

  tearDown(() {
    if (tempDir.existsSync()) tempDir.deleteSync(recursive: true);
  });

  /// 造一条日志 + 归属 + 分组文件
  Future<void> seedGroup(String topic) async {
    final now = DateTime(2026, 8, 15, 9, 30);
    final path = await collect(tempDir.path, '这是分组素材正文', now: now);
    await updateFrontMatter(tempDir.path, p.basename(path), (fm) {
      fm.topics['09-30'] = topic;
    });
    await writeGroups(tempDir.path);
  }

  test('buildDraftPrompt 包含素材与判据', () {
    final prompt = buildDraftPrompt('宣传册', '素材正文');
    expect(prompt, contains('宣传册'));
    expect(prompt, contains('素材正文'));
    expect(prompt, contains('过滤次要信息'));
    expect(prompt, contains('成文'));
  });

  test('distill 端到端：分组 → LLM 初稿 → materials/<主题>.md', () async {
    await seedGroup('宣传册');
    Future<String> fakeLlm(String prompt) async {
      expect(prompt, contains('宣传册'));
      return '这是一篇初稿正文。';
    }

    final out = await distill(tempDir.path, '宣传册', fakeLlm);
    expect(out, p.join(tempDir.path, 'materials', '宣传册.md'));
    final content = File(out).readAsStringSync();
    expect(content, contains('这是一篇初稿正文。'));
    // front matter：topic + sources 沿用分组
    expect(content, startsWith('---\ntopic: 宣传册\n'));
    expect(content, contains('journal/2026-08-15.md#09-30'));
  });

  test('distill 缺分组文件报错', () async {
    Future<String> fakeLlm(String prompt) async => 'x';
    await expectLater(
      distill(tempDir.path, '不存在', fakeLlm),
      throwsException,
    );
  });

  test('buildFinalizePrompt 包含目标与素材', () {
    final prompt = buildFinalizePrompt('创作动机', '写一篇品牌故事', '初稿正文', '分组素材');
    expect(prompt, contains('品牌故事'));
    expect(prompt, contains('初稿正文'));
    expect(prompt, contains('分组素材'));
    expect(prompt, contains('定稿'));
  });

  test('express 端到端：初稿 + 分组 → materials/<主题>-定稿.md', () async {
    await seedGroup('创作动机');
    Future<String> fakeLlm(String prompt) async => '定稿正文。';

    // 先 distill 生成初稿
    await distill(tempDir.path, '创作动机', fakeLlm);
    final out = await express(tempDir.path, '创作动机', llm: fakeLlm);
    expect(out, p.join(tempDir.path, 'materials', '创作动机-定稿.md'));
    expect(File(out).readAsStringSync(), '定稿正文。');
  });

  test('express 缺初稿报错', () async {
    Future<String> fakeLlm(String prompt) async => 'x';
    await expectLater(
      express(tempDir.path, '不存在', llm: fakeLlm),
      throwsException,
    );
  });
}
