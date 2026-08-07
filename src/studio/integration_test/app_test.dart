import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:qtcloud_write_studio/blocs/writing_review_cubit.dart';
import 'package:qtcloud_write_studio/widgets/draggable_divider.dart';
import 'package:qtcloud_write_studio/widgets/writing_workbench.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  late WritingReviewCubit cubit;

  setUp(() {
    cubit = WritingReviewCubit.test();
  });

  tearDown(() {
    cubit.close();
  });

  Widget buildApp() {
    return MultiBlocProvider(
      providers: [
        BlocProvider<WritingReviewCubit>.value(value: cubit),
      ],
      child: const MaterialApp(
        home: WritingWorkbench(),
      ),
    );
  }

  group('WritingWorkbench integration', () {
    testWidgets('加载样本后编辑器显示文字', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();

      await tester.tap(find.text('加载样本'));
      await tester.pump();

      final editorField = find.byType(TextField);
      expect(editorField, findsOneWidget);
      final textField = tester.widget<TextField>(editorField);
      expect(textField.controller?.text, isNotEmpty);
    });

    testWidgets('评审后显示分析结果', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();

      await tester.enterText(find.byType(TextField), '测试文本');
      await tester.pump();
      await tester.tap(find.text('▶ 评审'));
      await tester.pumpAndSettle();

      expect(cubit.state.reviewResponse, isNotNull);
    });

    testWidgets('加载样本后评审显示分析结果', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();

      await tester.tap(find.text('加载样本'));
      await tester.pump();
      await tester.tap(find.text('▶ 评审'));
      await tester.pumpAndSettle();

      expect(cubit.state.reviewResponse, isNotNull);
      expect(find.textContaining('字数'), findsWidgets);
    });

    testWidgets('情境标签页显示暂不可用提示', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();

      cubit.textChanged('测试文本');
      await tester.pump();
      await tester.tap(find.text('▶ 评审'));
      await tester.pumpAndSettle();

      await tester.tap(find.text('🎯 情境'));
      await tester.pumpAndSettle();

      expect(find.textContaining('Reflect'), findsWidgets);
    });

    testWidgets('改写标签页在无建议时显示占位', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();

      cubit.textChanged('测试文本');
      await cubit.runReview();
      await tester.pump();

      await tester.tap(find.text('✏️ 改写'));
      await tester.pumpAndSettle();

      expect(find.textContaining('分析结果'), findsWidgets);
    });

    testWidgets('拖拽分隔条渲染正确', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();

      expect(find.byType(DraggableDivider), findsNWidgets(2));
      expect(find.text('📄 底稿'), findsOneWidget);
      expect(find.byType(TextField), findsOneWidget);
      expect(find.text('Review'), findsOneWidget);
    });
  });
}
