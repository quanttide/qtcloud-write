import '../models/deep_analysis.dart';
import 'analysis_service.dart';

class LocalAnalysisService implements AnalysisService {
  @override
  Future<ReviewResponse> submitReview({
    required String text,
    required Map<String, dynamic> style,
  }) async {
    return ReviewResponse(
      dimensionAlignments: [],
      overallSummary: '本地分析完成（离线模式）。连接 Provider 后可获得 AI 分析。',
    );
  }
}
