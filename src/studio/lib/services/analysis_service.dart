import '../models/deep_analysis.dart';

abstract class AnalysisService {
  Future<ReviewResponse> submitReview({
    required String text,
    required Map<String, dynamic> style,
  });
}
