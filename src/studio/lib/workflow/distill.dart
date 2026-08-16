/// D-Distill（提取）：读分组产物，过滤次要信息并统一表达，
/// 形成初稿 materials/<主题>.md（产物 03，与 CLI distill.rs 对齐）。
///
/// 产物链：01 收集（collect）→ 02 分组（organize）→ 03 初稿（distill）→ 04 定稿（express）。
library;

import 'dart:io';

import 'package:path/path.dart' as p;

import 'frontmatter.dart';

/// 初稿提示词：过滤次要信息 + 成文（通用判据，不针对特定文本）。
String buildDraftPrompt(String topic, String aggregate) {
  return '以下是从日志中按主题聚合的写作素材(主题:$topic)。请基于素材形成一篇初稿:\n'
      '1. 过滤次要信息——从严删除,仅限以下四类杂质:\n'
      '- 过程性叙述:记录"正在做/打算做"的过程性语句(如"我打算""我在尝试""最近"),只保留其中的结论或洞察\n'
      '- 用途信息:关于素材将被用于什么、发布到哪里的说明(如发布渠道、宣传用途、收益安排、目标账号),除非该用途本身是主题的核心问题\n'
      '- 重复表述:同一观点多次出现时只保留最完整的一次\n'
      '- 即时情绪宣泄:直接的情绪感叹与自我对话;若其中包含可迁移的洞察则保留洞察\n'
      '2. 保留从宽:与主题相关的信息细节(人物、事件、设定、场景、动机、洞察、金句)全部保留,信息宁可完整不可削减\n'
      '3. 成文——不是素材的顺述或改写,而是基于素材的完整作品:\n'
      '- 提炼立意:这篇文章想表达什么(素材里反复出现、最能打动人心的内核)\n'
      '- 组织结构:按立意层层推进,有开头、发展、收束,主题分层展开\n'
      '- 统一视角与语气,语言有节奏,金句自然浮现\n'
      '输出一篇结构完整、可独立阅读的初稿(markdown,与素材同语言)。只输出初稿,不要解释。\n\n素材:\n$aggregate';
}

/// 执行 distill：读分组产物 groups/<主题>.md → LLM 过滤次要信息并统一表达
/// → 初稿 materials/<主题>.md（产物 03）。返回产物路径。
/// [llm] 为 LLM 回调（接收 prompt 返回文本），便于测试注入。
Future<String> distill(
  String workdir,
  String topic,
  Future<String> Function(String prompt) llm,
) async {
  final src = p.join(workdir, 'groups', '$topic.md');
  final groupFile = File(src);
  if (!groupFile.existsSync()) {
    throw Exception('读分组 $src: 不存在(先运行 organize 生成分组)');
  }
  final group = groupFile.readAsStringSync();
  final (fm, body) = FrontMatter.parse(group);

  final prompt = buildDraftPrompt(topic, body);
  final draft = await llm(prompt);

  // front matter：沿用分组的 sources
  final f = fm ?? FrontMatter();
  f.topic = topic;

  final dir = p.join(workdir, 'materials');
  Directory(dir).createSync(recursive: true);
  final path = p.join(dir, '$topic.md');
  File(path).writeAsStringSync('${f.render()}$draft');
  return path;
}
