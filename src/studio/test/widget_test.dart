import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/screens/review_screen.dart';
import 'package:qtcloud_write_studio/services/api_service.dart';

void main() {
  testWidgets('app renders review screen', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ReviewScreen(
          api: ApiService('http://localhost:8000'),
        ),
      ),
    );

    expect(find.text('写作云评审'), findsOneWidget);
    expect(find.text('提交评审'), findsOneWidget);
  });
}
