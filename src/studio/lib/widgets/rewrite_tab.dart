import 'package:flutter/material.dart';
import '../blocs/writing_review_cubit.dart';
import '../models/deep_analysis.dart';
import '../themes/writing_theme.dart';

class RewriteTab extends StatelessWidget {
  final WritingReviewCubit cubit;

  const RewriteTab({super.key, required this.cubit});

  @override
  Widget build(BuildContext context) {
    final state = cubit.state;

    if (state.deepAnalysis == null) {
      return const Center(
        child: Text('等待评审...', style: TextStyle(fontSize: 12, color: WritingColors.textDim)),
      );
    }

    if (state.deepAnalysis!.suggestions.isEmpty) {
      return const Center(
        child: Text('暂无改写建议。', style: TextStyle(fontSize: 12, color: WritingColors.textDim)),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(10),
      children: [
        const Text('改进建议', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: WritingColors.textDim, letterSpacing: 0.8)),
        const SizedBox(height: 8),
        ...state.deepAnalysis!.suggestions.map((s) => _SuggestionCard(s: s)),
      ],
    );
  }
}

class _SuggestionCard extends StatelessWidget {
  final DeepSuggestion s;
  const _SuggestionCard({required this.s});
  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      decoration: BoxDecoration(color: WritingColors.surface2, borderRadius: BorderRadius.circular(4)),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Container(padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1), decoration: BoxDecoration(color: WritingColors.accent.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(3)),
          child: Text('P${s.priority}', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: WritingColors.accent))),
        const SizedBox(width: 6),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(s.action, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: WritingColors.text)),
          Text(s.detail, style: const TextStyle(fontSize: 11, color: WritingColors.textDim)),
        ])),
      ]),
    );
  }
}
