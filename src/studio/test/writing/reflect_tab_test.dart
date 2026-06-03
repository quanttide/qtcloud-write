import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/blocs/writing_review_cubit.dart';
import 'package:qtcloud_write_studio/widgets/reflect_tab.dart';

Widget _buildApp(WritingReviewCubit cubit) {
  return MaterialApp(
    home: Scaffold(
      body: ReflectTab(cubit: cubit),
    ),
  );
}

void main() {
  group('ReflectTab', () {
    testWidgets('shows placeholder when no analysis', (tester) async {
      final cubit = WritingReviewCubit.test();
      await tester.pumpWidget(_buildApp(cubit));
      expect(find.text('等待评审...'), findsOneWidget);
      cubit.close();
    });

    testWidgets('shows reflect placeholder after analysis', (tester) async {
      final cubit = WritingReviewCubit.test();
      cubit.textChanged('test');
      await cubit.runReview();
      await tester.pumpWidget(_buildApp(cubit));
      await tester.pump();
      expect(find.textContaining('Reflect'), findsOneWidget);
      cubit.close();
    });
  });
}
