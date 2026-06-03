import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/blocs/writing_review_cubit.dart';
import 'package:qtcloud_write_studio/widgets/editor_panel.dart';

Widget _buildApp(WritingReviewCubit cubit) {
  return MaterialApp(
    home: Scaffold(
      body: EditorPanel(cubit: cubit),
    ),
  );
}

void main() {
  group('EditorPanel', () {
    testWidgets('shows text field and toolbar', (tester) async {
      final cubit = WritingReviewCubit.test();
      await tester.pumpWidget(_buildApp(cubit));
      expect(find.byType(TextField), findsOneWidget);
      expect(find.text('编辑'), findsOneWidget);
      expect(find.text('预览'), findsOneWidget);
      cubit.close();
    });

    testWidgets('switches to preview mode', (tester) async {
      final cubit = WritingReviewCubit.test();
      await cubit.loadSample();
      await tester.pumpWidget(_buildApp(cubit));
      await tester.tap(find.text('预览'));
      await tester.pump();
      expect(find.byType(TextField), findsNothing);
      cubit.close();
    });

    testWidgets('switches back to edit mode', (tester) async {
      final cubit = WritingReviewCubit.test();
      await cubit.loadSample();
      await tester.pumpWidget(_buildApp(cubit));
      await tester.tap(find.text('预览'));
      await tester.pump();
      await tester.tap(find.text('编辑'));
      await tester.pump();
      expect(find.byType(TextField), findsOneWidget);
      cubit.close();
    });

    testWidgets('typing text updates cubit', (tester) async {
      final cubit = WritingReviewCubit.test();
      await tester.pumpWidget(_buildApp(cubit));
      await tester.enterText(find.byType(TextField), 'hello');
      expect(cubit.state.text, 'hello');
      cubit.close();
    });
  });
}
