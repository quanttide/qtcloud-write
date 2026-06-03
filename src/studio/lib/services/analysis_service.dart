import '../models/deep_analysis.dart';

abstract class AnalysisService {
  Future<DeepReview> submitReview({
    required String title,
    required List<String> paragraphs,
  });
}
