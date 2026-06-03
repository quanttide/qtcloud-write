import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:qtcloud_write_studio/blocs/writing_review_cubit.dart';
import 'package:qtcloud_write_studio/widgets/review_tab.dart';

Widget _buildApp(WritingReviewCubit cubit) {
  return BlocProvider<WritingReviewCubit>.value(
    value: cubit,
    child: MaterialApp(
      home: Scaffold(
        body: ReviewTab(cubit: cubit),
      ),
    ),
  );
}

void main() {
  group('ReviewTab', () {
    testWidgets('shows placeholder when no analysis', (tester) async {
      final cubit = WritingReviewCubit.test();
      await tester.pumpWidget(_buildApp(cubit));
      expect(find.text('等待评审...'), findsOneWidget);
      cubit.close();
    });

    testWidgets('shows analysis result', (tester) async {
      final cubit = WritingReviewCubit.test();
      cubit.textChanged('test content');
      await cubit.runReview();
      await tester.pumpWidget(_buildApp(cubit));
      expect(cubit.state.reviewResponse, isNotNull);
      cubit.close();
    });

    testWidgets('shows summary text when analysis exists', (tester) async {
      final cubit = WritingReviewCubit.test();
      cubit.textChanged('test content');
      await cubit.runReview();
      await tester.pumpWidget(_buildApp(cubit));
      await tester.pump();
      expect(find.textContaining('测试分析结果'), findsOneWidget);
      cubit.close();
    });
  });
}
