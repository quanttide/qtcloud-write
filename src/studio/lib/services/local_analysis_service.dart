import '../models/deep_analysis.dart';
import '../models/analysis.dart' as local;
import 'analysis_service.dart';
import 'analysis_engine.dart';

class LocalAnalysisService implements AnalysisService {
  @override
  Future<DeepReview> submitReview({
    required String title,
    required List<String> paragraphs,
    required String author,
    required String tag,
  }) async {
    final text = paragraphs.join('\n');
    final result = AnalysisEngine.analyze(text);

    return DeepReview(
      articleTitle: title,
      author: author,
      tag: tag,
      summary: '本地分析完成 — 共发现 ${result.gaps.length} 处空隙，综合评分 ${result.avgScore.round()}',
      paragraphs: [],
      isStyleAvailable: false,
      suggestions: _buildSuggestions(result),
      isFromRemote: false,
    );
  }

  List<DeepSuggestion> _buildSuggestions(local.AnalysisResult result) {
    final list = <DeepSuggestion>[];
    for (final r in result.rewrites) {
      list.add(DeepSuggestion(
        priority: 1,
        action: r.location,
        detail: r.suggestion,
      ));
    }
    return list;
  }
}
