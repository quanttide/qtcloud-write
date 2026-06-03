import '../models/deep_analysis.dart';
import 'analysis_service.dart';

class LocalAnalysisService implements AnalysisService {
  @override
  Future<ReviewResponse> submitReview({
    required String text,
    required List<Map<String, dynamic>> criteria,
  }) async {
    return ReviewResponse(
      criteriaAnalysis: [],
      overallSummary: '本地分析完成（离线模式）。提交 criteria 后连接 Provider 可获得 AI 分析。',
    );
  }
}
