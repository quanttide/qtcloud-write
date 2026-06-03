import 'package:flutter/material.dart';
import '../blocs/writing_review_cubit.dart';
import '../models/deep_analysis.dart';
import '../themes/writing_theme.dart';

class ReviewTab extends StatelessWidget {
  final WritingReviewCubit cubit;

  const ReviewTab({super.key, required this.cubit});

  @override
  Widget build(BuildContext context) {
    final state = cubit.state;
    final resp = state.reviewResponse;

    if (state.isLoading) {
      return const Center(child: Text('分析中...', style: TextStyle(fontSize: 12, color: WritingColors.textDim)));
    }
    if (resp == null) {
      return const Center(child: Text('等待评审...', style: TextStyle(fontSize: 12, color: WritingColors.textDim)));
    }

    return ListView(
      padding: const EdgeInsets.all(10),
      children: [
        if (resp.overallSummary.isNotEmpty) ...[
          const Text('评审摘要', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: WritingColors.textDim, letterSpacing: 0.8)),
          const SizedBox(height: 4),
          Text(resp.overallSummary, style: const TextStyle(fontSize: 12, color: WritingColors.text, height: 1.5)),
          const SizedBox(height: 12),
        ],
        if (resp.criteriaAnalysis.isNotEmpty) ...[
          const Text('准则分析', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: WritingColors.textDim, letterSpacing: 0.8)),
          const SizedBox(height: 4),
          ...resp.criteriaAnalysis.map((a) => _CriterionCard(analysis: a)),
        ],
      ],
    );
  }
}

class _CriterionCard extends StatelessWidget {
  final CriterionAnalysis analysis;
  const _CriterionCard({required this.analysis});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(color: WritingColors.surface2, borderRadius: BorderRadius.circular(8), border: Border(left: BorderSide(color: analysis.alignmentScore > 0.6 ? WritingColors.accent2 : WritingColors.accent3, width: 3))),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Text('准则 ${analysis.criterionId}', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: WritingColors.text)),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: analysis.alignmentScore > 0.6 ? WritingColors.accent2.withValues(alpha: 0.2) : WritingColors.accent3.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text('${(analysis.alignmentScore * 100).round()}%', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: analysis.alignmentScore > 0.6 ? WritingColors.accent2 : WritingColors.accent3)),
          ),
        ]),
        if (analysis.deviations.isNotEmpty) ...[
          const SizedBox(height: 6),
          ...analysis.deviations.map((d) => Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(d.explanation, style: const TextStyle(fontSize: 11, color: WritingColors.text, height: 1.4)),
              if (d.suggestedAlignment.isNotEmpty)
                Text('建议: ${d.suggestedAlignment}', style: const TextStyle(fontSize: 10, color: WritingColors.accent, height: 1.4)),
            ]),
          )),
        ],
      ]),
    );
  }
}
