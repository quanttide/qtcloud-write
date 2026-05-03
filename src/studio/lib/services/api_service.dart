import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/review.dart';

class ApiService {
  final String baseUrl;

  ApiService(this.baseUrl);

  Future<Review> submitReview({
    required String title,
    required List<String> paragraphs,
    required String author,
    required String tag,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/review'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'title': title,
        'paragraphs': paragraphs,
        'author': author,
        'tag': tag,
      }),
    );

    if (response.statusCode == 200) {
      return Review.fromJson(jsonDecode(response.body));
    }
    throw Exception('Review failed: ${response.statusCode}');
  }
}
