import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/services/local_analysis_service.dart';
import 'package:qtcloud_write_studio/main.dart';

void main() {
  testWidgets('app renders without crash', (tester) async {
    final service = LocalAnalysisService();
    await tester.pumpWidget(MaterialApp(home: AppShell(service: service)));
    await tester.pump();
    expect(find.byType(AppShell), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
    await tester.pump();
  });
}
