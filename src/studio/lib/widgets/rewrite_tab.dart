import 'package:flutter/material.dart';
import '../blocs/writing_review_cubit.dart';
import '../themes/writing_theme.dart';

class RewriteTab extends StatelessWidget {
  final WritingReviewCubit cubit;

  const RewriteTab({super.key, required this.cubit});

  @override
  Widget build(BuildContext context) {
    final state = cubit.state;
    if (state.reviewResponse == null) {
      return const Center(child: Text('等待评审...', style: TextStyle(fontSize: 12, color: WritingColors.textDim)));
    }
    return ListView(
      padding: const EdgeInsets.all(10),
      children: [
        const Text('分析结果', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: WritingColors.textDim, letterSpacing: 0.8)),
        const SizedBox(height: 8),
        if (state.reviewResponse!.overallSummary.isNotEmpty)
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: WritingColors.surface2, borderRadius: BorderRadius.circular(8)),
            child: Text(state.reviewResponse!.overallSummary, style: const TextStyle(fontSize: 12, color: WritingColors.text, height: 1.5)),
          ),
        if (state.reviewResponse!.criteriaAnalysis.isEmpty)
          const Padding(padding: EdgeInsets.only(top: 16), child: Text('暂无分析数据。添加 criteria 后重新评审可获得 AI 分析。', style: TextStyle(fontSize: 12, color: WritingColors.textDim))),
      ],
    );
  }
}
