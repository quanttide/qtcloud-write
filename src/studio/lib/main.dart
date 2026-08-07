import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'blocs/writing_review_cubit.dart';
import 'services/analysis_service.dart';
import 'services/local_analysis_service.dart';
import 'services/remote_analysis_service.dart';
import 'themes/writing_theme.dart';
import 'widgets/writing_workbench.dart';

void main() {
  final providerUrl =
      const String.fromEnvironment('PROVIDER_URL', defaultValue: 'http://localhost:9000');
  final service = providerUrl.isNotEmpty
      ? RemoteAnalysisService(providerUrl) as AnalysisService
      : LocalAnalysisService() as AnalysisService;
  runApp(LabApp(service: service));
}

class LabApp extends StatelessWidget {
  final AnalysisService service;
  const LabApp({super.key, required this.service});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '写作云 Lab',
      debugShowCheckedModeBanner: false,
      theme: WritingTheme.dark,
      home: AppShell(service: service),
    );
  }
}

class AppShell extends StatefulWidget {
  final AnalysisService service;
  const AppShell({super.key, required this.service});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  late final WritingReviewCubit _writingCubit;

  @override
  void initState() {
    super.initState();
    _writingCubit = WritingReviewCubit(service: widget.service);
    _writingCubit.loadSample();
  }

  @override
  void dispose() {
    _writingCubit.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider.value(
      value: _writingCubit,
      child: const WritingWorkbench(),
    );
  }
}
