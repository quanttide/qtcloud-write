import 'package:flutter/material.dart';
import 'screens/review_screen.dart';
import 'services/api_service.dart';

void main() {
  const apiUrl = String.fromEnvironment('API_URL', defaultValue: 'http://localhost:8000');
  runApp(ReviewApp(api: ApiService(apiUrl)));
}

class ReviewApp extends StatelessWidget {
  final ApiService api;
  const ReviewApp({super.key, required this.api});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '写作云',
      theme: ThemeData(useMaterial3: true),
      home: ReviewScreen(api: api),
    );
  }
}
