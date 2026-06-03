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
    cubit = WritingReviewCubit();
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

      // 点击"加载样本"按钮
      await tester.tap(find.text('加载样本'));
      await tester.pump();

      // 验证编辑器 TextField 确实显示了样本文字
      final editorField = find.byType(TextField);
      expect(editorField, findsOneWidget);
      final textField = tester.widget<TextField>(editorField);
      expect(textField.controller?.text, isNotEmpty);
    });

    testWidgets('评审结果显示空隙列表和风格评分', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();

      // 输入文本 → 评审
      await tester.enterText(find.byType(TextField), '他推开门走了出去。\n第二天，他又来了。\n');
      await tester.pump();
      await tester.tap(find.text('▶ 评审'));
      await tester.pumpAndSettle();

      // Review 标签页必须显示：空隙列表标题 + 风格标题 + 综合评分
      expect(find.textContaining('空隙'), findsWidgets);
      expect(find.textContaining('风格'), findsWidgets);
      expect(find.textContaining('/100'), findsOneWidget);
      // 必须显示三条风格评分中的至少一条名称
      expect(
        find.text('对话→动作').evaluate().isNotEmpty ||
        find.text('状态句结尾').evaluate().isNotEmpty ||
        find.text('半秒钟密度').evaluate().isNotEmpty,
        isTrue,
      );
    });

    testWidgets('加载样本后评审显示空隙', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();

      // 加载样本
      await tester.tap(find.text('加载样本'));
      await tester.pump();

      // 评审
      await tester.tap(find.text('▶ 评审'));
      await tester.pumpAndSettle();

      // 评审标签页显示空隙列表
      expect(find.textContaining('空隙'), findsWidgets);

      // 底部状态栏显示空隙数
      expect(find.textContaining('空隙'), findsWidgets);
      expect(find.textContaining('字数'), findsWidgets);
    });

    testWidgets('情境标签页显示可写位置卡片', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();

      // 加载样本 + 评审 → 产生空隙
      cubit.loadSample();
      await tester.pump();
      await tester.tap(find.text('▶ 评审'));
      await tester.pumpAndSettle();

      // 切到情境标签
      await tester.tap(find.text('🎯 情境'));
      await tester.pumpAndSettle();

      // 必须显示"可写位置"标题
      expect(find.textContaining('可写位置'), findsOneWidget);

      // 必须至少有一个 "写在这里" 按钮
      final writeButton = find.text('✎ 写在这里');
      expect(writeButton, findsWidgets);
    });

    testWidgets('改写标签页显示改写建议', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();

      // 输入触发情绪标签建议的文本
      cubit.textChanged('他悲伤地看着她。\n她开心地笑了。\n他走了过去。\n他们都沉默了。\n');
      cubit.runReview();
      await tester.pump();

      // 切到改写标签
      await tester.tap(find.text('✏️ 改写'));
      await tester.pumpAndSettle();

      // 必须显示"改写建议"标题
      expect(find.textContaining('改写建议'), findsOneWidget);

      // 必须显示"定位到此处"按钮
      final jumpButton = find.text('✎ 定位到此处');
      expect(jumpButton, findsWidgets);
    });

    testWidgets('3R 循环：评审 → 情境 → 改写 → 再评审', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();
      final editorField = find.byType(TextField);

      // 1. 写一段有空隙的文本
      await tester.enterText(editorField, '他推开门走了出去。\n第二天，他又回来了。\n她悲伤地看着他。\n');
      await tester.pump();

      // 2. 评审 → 看到空隙
      await tester.tap(find.text('▶ 评审'));
      await tester.pumpAndSettle();
      expect(cubit.state.gapCount, greaterThan(0));
      expect(find.textContaining('空隙'), findsWidgets);

      // 3. 切到情境 → 看到可写位置
      await tester.tap(find.text('🎯 情境'));
      await tester.pumpAndSettle();
      expect(find.textContaining('可写位置'), findsOneWidget);

      // 4. 切到改写 → 看到改写建议
      await tester.tap(find.text('✏️ 改写'));
      await tester.pumpAndSettle();
      expect(find.textContaining('改写建议'), findsOneWidget);

      // 5. 回到评审 → 再次评审确认分析可更新
      await tester.tap(find.text('📋 评审'));
      await tester.pump();
      await tester.tap(find.text('▶ 评审'));
      await tester.pumpAndSettle();
      expect(cubit.state.analysis, isNotNull);
    });

    testWidgets('深度分析按钮在无 Provider 时不显示', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();

      // 未配置 Provider 时按钮不可见
      expect(find.text('🧠 深度分析'), findsNothing);
    });

    testWidgets('多轮迭代：文本变化后空隙数变化', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();
      final editorField = find.byType(TextField);

      // 第1轮：有空隙的文本
      await tester.enterText(editorField, '他走了出去。第二天，他又来了。她悲伤地看着他。');
      await tester.pump();
      await tester.tap(find.text('▶ 评审'));
      await tester.pumpAndSettle();
      expect(cubit.state.gapCount, greaterThan(0));

      // 第2轮：改写成无触发词文本
      cubit.textChanged('他走在街上。冷风扑面而来。他裹紧了外套。');
      cubit.runReview();
      await tester.pump();
      expect(cubit.state.gapCount, lessThanOrEqualTo(1));
    });

    testWidgets('结尾建议出现在结尾不合状态句的文本中', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpWidget(buildApp());
      await tester.pump();
      final editorField = find.byType(TextField);

      await tester.enterText(editorField, '他推开门走了出去。\n她跟在他身后。\n他们一起走进了咖啡厅。');
      await tester.pump();
      await tester.tap(find.text('▶ 评审'));
      await tester.pumpAndSettle();

      await tester.tap(find.text('✏️ 改写'));
      await tester.pumpAndSettle();
      expect(find.textContaining('结尾'), findsWidgets);
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
