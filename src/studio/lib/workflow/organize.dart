/// O-Organize：LLM 从日志提取主题，更新各日志文件 YAML 归属（与 CLI organize.rs 对齐）。
///
/// 流程：读全部日志 → 收集未标注条目 → LLM 建议主题 → 合并写入
/// 各文件 front matter（仅写入未标注条目，保留人工标注）→ 生成 groups/<主题>.md。
library;

import 'dart:io';

import 'package:path/path.dart' as p;

import 'frontmatter.dart';
import 'journal.dart';

/// 构建 prompt：列出所有未标注条目，要求 LLM 输出 YAML 归属。
String buildPrompt(List<JournalFile> journals) {
  final lines = <String>[];
  for (final jf in journals) {
    for (final e in jf.entries) {
      if (!jf.fm.topics.containsKey(e.id)) {
        lines.add('${e.file}#${e.id}: ${e.text}');
      }
    }
  }
  if (lines.isEmpty) return '';
  return '以下是一批日志条目(来源文件名#条目ID: 内容):\n${lines.join('\n')}\n\n'
      '为每条条目分配一个简短主题名(可复用、中文,2-6 字)。只输出 YAML:\n'
      '---\ntopics:\n  "来源文件名#条目ID": 主题名\n---';
}

/// 解析 LLM 输出的归属映射（容忍 ```yaml 围栏与缺失的 ---）。
Map<String, String> parseLlmOutput(String text) {
  var t = text.trim();
  t = t.replaceAll(RegExp(r'^`+'), '').replaceAll(RegExp(r'`+$'), '');
  if (t.startsWith('yaml\n')) {
    t = t.substring(5);
  }
  final doc = t.startsWith('---') ? t : '---\n$t\n---';
  final (fm, _) = FrontMatter.parse(doc);
  return fm?.topics ?? {};
}

/// 执行 organize：返回更新的条目数。
/// [llm] 为 LLM 回调（接收 prompt 返回文本），便于测试注入。
Future<int> organize(
  String workdir,
  Future<String> Function(String prompt) llm,
) async {
  final journals = await readAll(workdir);
  final prompt = buildPrompt(journals);
  if (prompt.isEmpty) return 0;
  final output = await llm(prompt);
  final suggestions = parseLlmOutput(output);
  if (suggestions.isEmpty) {
    throw Exception('LLM 输出无法解析为主题归属: $output');
  }

  var updated = 0;
  for (final jf in journals) {
    // 收集本文件内未标注条目的建议（支持 "文件#id" 与纯 "id" 两种 key）
    final changes = <String, String>{};
    for (final entry in suggestions.entries) {
      final key = entry.key;
      final (file, id) = key.contains('#')
          ? (key.substring(0, key.indexOf('#')), key.substring(key.indexOf('#') + 1))
          : ('', key);
      if (file.isNotEmpty && file != jf.file) continue;
      final exists = jf.entries.any((e) => e.id == id);
      if (exists && !jf.fm.topics.containsKey(id)) {
        changes[id] = entry.value;
      }
    }
    if (changes.isNotEmpty) {
      await updateFrontMatter(workdir, jf.file, (fm) {
        fm.topics.addAll(changes);
      });
      updated += changes.length;
    }
  }
  return updated;
}

/// 生成分组产物：按主题聚合日志条目 → groups/<主题>.md（02 分组）。
/// 读取最新 YAML 归属（含人工修改），幂等重建。返回生成的文件路径列表。
Future<List<String>> writeGroups(String workdir) async {
  // 所有出现过的主题（保持顺序）
  final journals = await readAll(workdir);
  final topics = <String>[];
  for (final jf in journals) {
    for (final t in jf.fm.topics.values) {
      if (!topics.contains(t)) topics.add(t);
    }
  }

  final dir = p.join(workdir, 'groups');
  Directory(dir).createSync(recursive: true);
  final out = <String>[];
  for (final topic in topics) {
    final entries = await collectForTopic(workdir, topic);
    final fm = FrontMatter(topic: topic);
    for (final e in entries) {
      fm.sources.add('journal/${e.reference()}');
    }
    final body = StringBuffer();
    for (final e in entries) {
      if (body.isNotEmpty) body.write('\n');
      body.write(e.text);
      body.write('\n\n> 来源:journal/${e.reference()}\n');
    }
    final path = p.join(dir, '$topic.md');
    File(path).writeAsStringSync('${fm.render()}$body');
    out.add(path);
  }
  return out;
}
