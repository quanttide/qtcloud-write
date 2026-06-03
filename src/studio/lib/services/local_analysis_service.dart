import '../models/deep_analysis.dart';
import '../models/analysis.dart' as local;
import 'analysis_service.dart';
import 'analysis_engine.dart';

class LocalAnalysisService implements AnalysisService {
  @override
  Future<DeepReview> submitReview({
    required String title,
    required List<String> paragraphs,
  }) async {
    final text = paragraphs.join('\n');
    final result = AnalysisEngine.analyze(text);

    return DeepReview(
      articleTitle: title,
      summary: '本地分析完成',
      paragraphs: [],
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
