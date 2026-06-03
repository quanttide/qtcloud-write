import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/blocs/writing_review_cubit.dart';
import 'package:qtcloud_write_studio/widgets/rewrite_tab.dart';

Widget _buildApp(WritingReviewCubit cubit) {
  return MaterialApp(
    home: Scaffold(
      body: RewriteTab(cubit: cubit),
    ),
  );
}

void main() {
  group('RewriteTab', () {
    testWidgets('shows placeholder when no analysis', (tester) async {
      final cubit = WritingReviewCubit.test();
      await tester.pumpWidget(_buildApp(cubit));
      expect(find.text('等待评审...'), findsOneWidget);
      cubit.close();
    });

    testWidgets('shows summary when analysis exists', (tester) async {
      final cubit = WritingReviewCubit.test();
      cubit.textChanged('test');
      await cubit.runReview();
      await tester.pumpWidget(_buildApp(cubit));
      await tester.pumpAndSettle();
      expect(find.textContaining('分析结果'), findsWidgets);
      cubit.close();
    });
  });
}
