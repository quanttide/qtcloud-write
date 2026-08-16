/// 真实 LLM 端到端集成测试：客户端复现 CLI 四命令流程。
///
/// 需要环境变量 DEEPSEEK_API_KEY（与 CLI 相同）；未设置时跳过。
/// 用法：DEEPSEEK_API_KEY=sk-xxx flutter test test/workflow/real_pipeline_test.dart
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:qtcloud_write_studio/services/llm_client.dart';
import 'package:qtcloud_write_studio/workflow/distill.dart' as distill_mod;
import 'package:qtcloud_write_studio/workflow/express.dart' as express_mod;
import 'package:qtcloud_write_studio/workflow/journal.dart' as journal_mod;
import 'package:qtcloud_write_studio/workflow/organize.dart' as organize_mod;

void main() {
  final hasKey = Platform.environment['DEEPSEEK_API_KEY']?.isNotEmpty ?? false;

  test(
    '客户端复现 CLI 四命令流程(真实 LLM):collect → organize → distill → express',
    () async {
      if (!hasKey) {
        markTestSkipped('DEEPSEEK_API_KEY 未设置，跳过真实 LLM 集成测试');
        return;
      }
      final llm = LLMClient(config: LLMConfig.defaults());
      final workdir = Directory.systemTemp.createTempSync('studio_pipeline_').path;
      try {
        // 01 收集
        final now1 = DateTime(2026, 8, 16, 9, 30);
        final now2 = DateTime(2026, 8, 16, 10, 5);
        final j1 = await journal_mod.collect(workdir, '最近在思考写作这件事对我的意义,好像不只是副业。', now: now1);
        final j2 = await journal_mod.collect(workdir, '想写一篇关于"敢不敢说出心里话"的文章,从写作经历出发。', now: now2);
        expect(File(j1).existsSync(), isTrue);
        expect(File(j2).existsSync(), isTrue);

        // 02 分组（真实 LLM 提取主题 + 生成分组文件）
        final updated = await organize_mod.organize(workdir, llm.completeText);
        expect(updated, greaterThan(0));
        final groups = await organize_mod.writeGroups(workdir);
        expect(groups, isNotEmpty);

        // 03 初稿（每个分组主题 → materials/<主题>.md）
        final drafts = <String>[];
        for (final g in groups) {
          final topic = g.split(Platform.pathSeparator).last.replaceAll('.md', '');
          final path = await distill_mod.distill(workdir, topic, llm.completeText);
          expect(File(path).existsSync(), isTrue);
          expect(File(path).lengthSync(), greaterThan(50));
          drafts.add(path);
        }

        // 04 定稿（每个主题 → materials/<主题>-定稿.md）
        for (final d in drafts) {
          final topic = d.split(Platform.pathSeparator).last.replaceAll('.md', '');
          final path = await express_mod.express(workdir, topic, llm: llm.completeText);
          expect(File(path).existsSync(), isTrue);
          expect(File(path).lengthSync(), greaterThan(50));
        }

        // 产物链核对：journal / groups / materials 齐备
        expect(File('$workdir/journal/2026-08-16.md').existsSync(), isTrue);
        expect(Directory('$workdir/groups').existsSync(), isTrue);
        expect(Directory('$workdir/materials').existsSync(), isTrue);
      } finally {
        llm.close();
        Directory(workdir).deleteSync(recursive: true);
      }
    },
    timeout: const Timeout(Duration(minutes: 8)),
  );
}
