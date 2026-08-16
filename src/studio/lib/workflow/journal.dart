/// 日志（journal）读写：collect 记录 + 条目解析（与 CLI journal.rs 对齐）。
///
/// 布局：workdir/journal/YYYY-MM-DD.md，条目格式：
/// ```markdown
/// ## 09:30
/// 想法文本
/// ```
library;

import 'dart:io';

import 'package:path/path.dart' as p;

import 'frontmatter.dart';

/// 一条日志条目。
class Entry {
  /// 来源文件名，如 `2026-08-15.md`
  final String file;
  /// 条目 id，时间戳连字符形式，如 `09-30`
  final String id;
  /// 条目标题，如 `09:30`
  final String title;
  /// 条目正文
  final String text;

  const Entry({
    required this.file,
    required this.id,
    required this.title,
    required this.text,
  });

  /// 引用形式：`2026-08-15.md#09-30`
  String reference() => '$file#$id';
}

/// 一个日志文件：文件名 + front matter + 条目列表。
class JournalFile {
  final String file;
  final FrontMatter fm;
  final List<Entry> entries;

  const JournalFile({
    required this.file,
    required this.fm,
    required this.entries,
  });
}

String journalDir(String workdir) => p.join(workdir, 'journal');

/// C-Capture：把一条想法追加到今日日志（自动 ## HH:MM 条目）。
Future<String> collect(String workdir, String text, {DateTime? now}) async {
  final t = now ?? DateTime.now();
  final title = '${t.hour.toString().padLeft(2, '0')}:${t.minute.toString().padLeft(2, '0')}';
  return appendEntry(workdir, title, text, now: t);
}

/// 追加一条条目到今日日志；同标题多条时标题追加序号（`## 09:30-2`）。
Future<String> appendEntry(
  String workdir,
  String title,
  String text, {
  DateTime? now,
}) async {
  final t = now ?? DateTime.now();
  final dir = journalDir(workdir);
  Directory(dir).createSync(recursive: true);
  final dateStr = '${t.year.toString().padLeft(4, '0')}-'
      '${t.month.toString().padLeft(2, '0')}-'
      '${t.day.toString().padLeft(2, '0')}';
  final path = p.join(dir, '$dateStr.md');

  final buffer = StringBuffer();
  final existingIds = <String>[];
  final file = File(path);
  if (file.existsSync()) {
    final prev = file.readAsStringSync();
    existingIds.addAll(readEntries(prev).map((e) => e.id));
    buffer.write(prev);
    if (!prev.endsWith('\n')) buffer.write('\n');
    buffer.write('\n');
  }
  final baseId = title.replaceAll(':', '-');
  final same = existingIds
      .where((id) => id == baseId || id.startsWith('$baseId-'))
      .length;
  final finalTitle = same == 0 ? title : '$title-${same + 1}';
  buffer.write('## $finalTitle\n${text.trim()}\n');
  file.writeAsStringSync(buffer.toString());
  return path;
}

/// 解析日志正文为条目列表（识别 `## ` 小节）。
/// id 直接由标题生成：`## 19:53` → `19-53`；`## 19:53-2` → `19-53-2`。
List<Entry> readEntries(String body) {
  final out = <Entry>[];
  String? curTitle;
  String? curId;
  final lines = <String>[];

  void flush() {
    if (curTitle != null) {
      out.add(Entry(
        file: '',
        id: curId!,
        title: curTitle,
        text: lines.join('\n').trim(),
      ));
    }
    lines.clear();
  }

  for (final line in body.split('\n')) {
    if (line.startsWith('## ')) {
      flush();
      curTitle = line.substring(3).trim();
      curId = curTitle.replaceAll(':', '-');
    } else if (curTitle != null) {
      lines.add(line);
    }
  }
  flush();
  return out;
}

/// 读取全部日志文件（按文件名排序），解析 front matter 与条目。
Future<List<JournalFile>> readAll(String workdir) async {
  final dir = Directory(journalDir(workdir));
  final out = <JournalFile>[];
  if (!dir.existsSync()) return out;
  final files = dir
      .listSync()
      .whereType<File>()
      .where((f) => p.extension(f.path) == '.md')
      .toList()
    ..sort((a, b) => p.basename(a.path).compareTo(p.basename(b.path)));
  for (final f in files) {
    final content = f.readAsStringSync();
    final (fm, body) = FrontMatter.parse(content);
    final file = p.basename(f.path);
    final entries = readEntries(body).map((e) => Entry(
          file: file,
          id: e.id,
          title: e.title,
          text: e.text,
        )).toList();
    out.add(JournalFile(file: file, fm: fm ?? FrontMatter(), entries: entries));
  }
  return out;
}

/// 更新单个日志文件的 front matter：读 → 闭包修改 → 写回。
Future<void> updateFrontMatter(
  String workdir,
  String file,
  void Function(FrontMatter fm) update,
) async {
  final path = p.join(journalDir(workdir), file);
  final content = File(path).readAsStringSync();
  final (fm, body) = FrontMatter.parse(content);
  final f = fm ?? FrontMatter();
  update(f);
  File(path).writeAsStringSync('${f.render()}$body');
}

/// 收集归属 `topic` 的全部日志条目（按文件 + 时间排序）。
/// 无归属条目时返回空列表。
Future<List<Entry>> collectForTopic(String workdir, String topic) async {
  final journals = await readAll(workdir);
  final collected = <Entry>[];
  for (final jf in journals) {
    for (final entry in jf.fm.topics.entries) {
      if (entry.value == topic) {
        final e = jf.entries.where((e) => e.id == entry.key).firstOrNull;
        if (e != null) collected.add(e);
      }
    }
  }
  collected.sort((a, b) {
    final byFile = a.file.compareTo(b.file);
    return byFile != 0 ? byFile : a.id.compareTo(b.id);
  });
  return collected;
}

/// 各日志条目 id → 主题（合并所有文件）。
Map<String, String> allTopicAssignments(List<JournalFile> journals) {
  final out = <String, String>{};
  for (final jf in journals) {
    for (final entry in jf.fm.topics.entries) {
      out['${jf.file}#${entry.key}'] = entry.value;
    }
  }
  return out;
}
