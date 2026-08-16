/// E-Express（表达）：根据写作目标形成定稿（产物 04，与 CLI express.rs 对齐）。
///
/// 输入 distill 初稿 materials/<主题>.md + 分组素材 groups/<主题>.md，
/// 输出 materials/<主题>-定稿.md。参考分组素材保证信息不因过滤而丢失。
/// 未提供 goal 时，由 LLM 根据内容自动判断写作意图作为目标。
library;

import 'dart:io';

import 'package:path/path.dart' as p;

import 'frontmatter.dart';

/// 定稿提示词：以初稿为底稿、素材为原材料，按写作目标重新构思定稿。
String buildFinalizePrompt(String topic, String goal, String draft, String material) {
  return '以下是一篇初稿(主题:$topic)与对应的完整分组素材。\n'
      '写作目标:$goal\n'
      '请以初稿为内容底稿、分组素材为原材料,按写作目标重新构思一篇定稿:\n'
      '- 定稿是面向目标读者的完整作品,不是素材汇编或信息清单\n'
      '- 按写作目标确定视角与结构:例如品牌故事采用面向读者的对话视角与单一叙事线,而非主题章节清单\n'
      '- 素材细节服务于叙事主线:保留有感染力的细节(场景、金句、情感),舍弃事务性说明(发布渠道、流程安排、收益),除非能转化为理念表达\n'
      '- 语言有节奏:短句、金句独立成段、层层推进,结尾收束有力\n'
      '只输出定稿,不要解释。\n\n初稿:\n$draft\n\n分组素材:\n$material';
}

/// 执行 express：读初稿 + 分组素材 → LLM 按目标定稿 → materials/<主题>-定稿.md。
/// [goal] 为 null 时自动判断写作意图；返回产物路径。
/// [llm] 为 LLM 回调（接收 prompt 返回文本），便于测试注入。
Future<String> express(
  String workdir,
  String topic, {
  String? goal,
  required Future<String> Function(String prompt) llm,
}) async {
  final src = p.join(workdir, 'materials', '$topic.md');
  final draftFile = File(src);
  if (!draftFile.existsSync()) {
    throw Exception('读初稿 $src: 不存在(先运行 distill 生成初稿)');
  }
  final draft = draftFile.readAsStringSync();
  final gsrc = p.join(workdir, 'groups', '$topic.md');
  final groupFile = File(gsrc);
  if (!groupFile.existsSync()) {
    throw Exception('读分组 $gsrc: 不存在(先运行 organize 生成分组)');
  }
  final (_, material) = FrontMatter.parse(groupFile.readAsStringSync());

  final g = goal ?? '根据内容自动判断写作意图';
  final prompt = buildFinalizePrompt(topic, g, draft, material);
  final finalDoc = await llm(prompt);

  final out = p.join(workdir, 'materials', '$topic-定稿.md');
  File(out).writeAsStringSync(finalDoc);
  return out;
}
