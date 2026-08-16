import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../config.dart';
import '../repositories/analysis_repository.dart';
import '../repositories/chapter_repository.dart';
import '../repositories/file_chapter_repository.dart';
import '../services/llm_client.dart';
import 'analyze/analyze_bloc.dart';
import 'editor/editor_bloc.dart';
import 'workflow/workflow_bloc.dart';

/// 应用级 Bloc Provider（写作编辑器所需的最小闭包）
class AppBlocProvider extends StatelessWidget {
  final Widget child;
  final ChapterRepository? chapterRepository;

  const AppBlocProvider({
    super.key,
    required this.child,
    this.chapterRepository,
  });

  @override
  Widget build(BuildContext context) {
    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider<ChapterRepository>(
          create: (context) => chapterRepository ?? _createDefaultRepository(),
        ),
        RepositoryProvider<ChapterAnalysisRepository>(
          create: (context) => FileAnalysisRepository(),
        ),
        RepositoryProvider<LLMClient>(
          create: (context) => LLMClient(config: LLMConfig.defaults()),
        ),
      ],
      child: MultiBlocProvider(
        providers: [
          BlocProvider<WorkflowBloc>(
            create: (context) => WorkflowBloc(
              repository: context.read<ChapterRepository>(),
            )..add(const LoadWorkflow()),
          ),
          BlocProvider<EditorBloc>(
            create: (context) => EditorBloc(
              repository: context.read<ChapterRepository>(),
            ),
          ),
          BlocProvider<AnalyzeBloc>(
            create: (context) => AnalyzeBloc(
              chapterRepository: context.read<ChapterRepository>(),
              analysisRepository: context.read<ChapterAnalysisRepository>(),
              llm: context.read<LLMClient>(),
              onInspirationApplied: () =>
                  context.read<WorkflowBloc>().add(const LoadWorkflow()),
            ),
          ),
        ],
        child: child,
      ),
    );
  }

  ChapterRepository _createDefaultRepository() {
    return FileChapterRepository(basePath: writeDataPath);
  }
}

/// 页面级 Bloc Provider（用于测试或独立页面）
class PageBlocProvider extends StatelessWidget {
  final Widget child;
  final ChapterRepository repository;

  const PageBlocProvider({
    super.key,
    required this.child,
    required this.repository,
  });

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider<WorkflowBloc>(
          create: (context) => WorkflowBloc(
            repository: repository,
          )..add(const LoadWorkflow()),
        ),
        BlocProvider<EditorBloc>(
          create: (context) => EditorBloc(
            repository: repository,
          ),
        ),
      ],
      child: child,
    );
  }
}
