/// 极简 YAML front matter 解析/序列化（与 CLI frontmatter.rs 对齐）。
///
/// 仅支持本工具需要的子集：
/// ```yaml
/// ---
/// topic: 宣传册            # 素材文件的主题（可选）
/// topics:                  # 日志文件的条目归属
///   "09-30": 宣传册
/// sources:                 # 素材文件的来源引用（可选）
///   - journal/2026-08-15.md#09-30
/// ---
/// ```
library;

/// front matter 数据。
class FrontMatter {
  /// 日志条目归属：条目 id → 主题
  final Map<String, String> topics;
  /// 素材自身的主题（用于 materials/*.md）
  String? topic;
  /// 来源引用列表（用于 materials/*.md）
  final List<String> sources;

  FrontMatter({
    Map<String, String>? topics,
    this.topic,
    List<String>? sources,
  })  : topics = topics ?? {},
        sources = sources ?? [];

  /// 解析文档，返回 (front matter, 正文)。无 front matter 时返回 (null, 全文)。
  static (FrontMatter?, String) parse(String content) {
    if (!content.startsWith('---\n')) {
      return (null, content);
    }
    final rest = content.substring(4);
    final end = rest.indexOf('\n---');
    if (end < 0) {
      return (null, content);
    }
    final fmText = rest.substring(0, end);
    var body = rest.substring(end + 4);
    body = body.replaceFirst(RegExp(r'^\n+'), '');

    final fm = FrontMatter();
    String? currentKey;
    for (final line in fmText.split('\n')) {
      final trimmed = line.trim();
      if (line.startsWith(' ') || line.startsWith('\t')) {
        // 缩进条目：key: value 或 - item
        if (currentKey != null) {
          if (trimmed.startsWith('- ')) {
            if (currentKey == 'sources') {
              fm.sources.add(trimmed.substring(2).trim());
            }
          } else {
            final idx = trimmed.indexOf(':');
            if (idx > 0) {
              final k = trimmed.substring(0, idx).trim().replaceAll('"', '');
              final v = trimmed.substring(idx + 1).trim().replaceAll('"', '');
              if (currentKey == 'topics') {
                fm.topics[k] = v;
              }
            }
          }
        }
      } else {
        final idx = trimmed.indexOf(':');
        if (idx > 0) {
          final k = trimmed.substring(0, idx).trim();
          final v = trimmed.substring(idx + 1).trim();
          switch (k) {
            case 'topics':
            case 'sources':
              currentKey = k;
              break;
            case 'topic':
              fm.topic = v.isEmpty ? null : v.replaceAll('"', '');
              break;
            default:
              currentKey = k;
          }
        }
      }
    }
    return (fm, body);
  }

  /// 渲染 front matter（带 `---` 包裹）。
  String render() {
    final out = StringBuffer('---\n');
    if (topic != null) {
      out.write('topic: $topic\n');
    }
    if (topics.isNotEmpty) {
      out.write('topics:\n');
      for (final entry in topics.entries) {
        out.write('  "${entry.key}": ${entry.value}\n');
      }
    }
    if (sources.isNotEmpty) {
      out.write('sources:\n');
      for (final s in sources) {
        out.write('  - $s\n');
      }
    }
    out.write('---\n');
    return out.toString();
  }
}
