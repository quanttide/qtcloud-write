import 'package:flutter/material.dart';

import 'blocs/app_bloc_provider.dart';
import 'screens/create_screen_new.dart';

void main() {
  runApp(const WriteStudioApp());
}

/// 写作云 AI 原生写作编辑器（四命令工作流：收集 → 分组 → 初稿 → 定稿）
class WriteStudioApp extends StatelessWidget {
  const WriteStudioApp({super.key});

  @override
  Widget build(BuildContext context) {
    return AppBlocProvider(
      child: MaterialApp(
        title: '写作云 Studio',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF4F46E5),
            surface: Colors.white,
            brightness: Brightness.light,
          ),
          scaffoldBackgroundColor: const Color(0xFFF1F5F9),
          useMaterial3: true,
        ),
        home: const CreateScreenNew(),
      ),
    );
  }
}
