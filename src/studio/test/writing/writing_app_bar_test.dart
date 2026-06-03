import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/blocs/writing_review_cubit.dart';
import 'package:qtcloud_write_studio/widgets/writing_app_bar.dart';

Widget _buildApp(WritingReviewCubit cubit) {
  return MaterialApp(
    home: Scaffold(
      body: WritingAppBar(cubit: cubit),
    ),
  );
}

void main() {
  group('WritingAppBar', () {
    testWidgets('renders logo and buttons', (tester) async {
      final cubit = WritingReviewCubit();
      await tester.pumpWidget(_buildApp(cubit));
      expect(find.text('✎ 写作云'), findsOneWidget);
      expect(find.text('合成工作台'), findsOneWidget);
      expect(find.text('▶ 评审'), findsOneWidget);
      // 无 deep service 时不显示深度分析按钮
      expect(find.text('🧠 深度分析'), findsNothing);
      expect(find.text('加载样本'), findsOneWidget);
      cubit.close();
    });

    testWidgets('review button triggers runReview', (tester) async {
      final cubit = WritingReviewCubit();
      cubit.textChanged('test content');
      await tester.pumpWidget(_buildApp(cubit));
      await tester.tap(find.text('▶ 评审'));
      expect(cubit.state.analysis, isNotNull);
      cubit.close();
    });

    testWidgets('load sample button triggers loadSample', (tester) async {
      final cubit = WritingReviewCubit();
      await tester.pumpWidget(_buildApp(cubit));
      await tester.tap(find.text('加载样本'));
      expect(cubit.state.text, isNotEmpty);
      cubit.close();
    });
  });
}
