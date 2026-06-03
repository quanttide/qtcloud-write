import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/deep_analysis.dart';
import 'analysis_service.dart';

class RemoteAnalysisService implements AnalysisService {
  final String baseUrl;

  RemoteAnalysisService(this.baseUrl);

  @override
  Future<DeepReview> submitReview({
    required String title,
    required List<String> paragraphs,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/review'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'title': title,
        'paragraphs': paragraphs,
      }),
    );

    if (response.statusCode == 200) {
      return DeepReview.fromJson(jsonDecode(response.body));
    }

    String detail = '';
    try {
      final body = jsonDecode(response.body);
      detail = body['detail']?.toString() ?? '';
    } catch (_) {}

    throw Exception('分析请求失败 ($response.statusCode)${detail.isNotEmpty ? ': $detail' : ''}');
  }
}
