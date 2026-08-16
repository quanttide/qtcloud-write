import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:qtcloud_write_studio/blocs/app_bloc_provider.dart';
import 'package:qtcloud_write_studio/screens/create_screen_new.dart';

import 'bloc/mock_chapter_repository.dart';

void main() {
  testWidgets('写作云 Studio 可渲染写作编辑器（搜索框 + 章节树 + AI 整理按钮）', (tester) async {
    await tester.pumpWidget(
      AppBlocProvider(
        chapterRepository: MockChapterRepository(),
        child: const MaterialApp(home: CreateScreenNew()),
      ),
    );
    await tester.pumpAndSettle();

    // 编辑器界面元素
    expect(find.text('搜索章节...'), findsOneWidget);
    // 阶段树（01_收集 / 02_分组 有测试章节）
    expect(find.text('01_收集'), findsOneWidget);
    expect(find.text('02_分组'), findsOneWidget);
    // 空状态（未选择章节）
    expect(find.text('选择一个章节开始写作'), findsOneWidget);

    // 选择章节后出现工具栏（AI 整理按钮）
    await tester.tap(find.text('测试章节1'));
    await tester.pumpAndSettle();
    expect(find.byTooltip('AI 整理'), findsOneWidget);
  });
}
