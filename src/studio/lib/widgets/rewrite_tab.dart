import 'package:flutter/material.dart';
import '../blocs/writing_review_cubit.dart';
import '../themes/writing_theme.dart';
import 'guide_card.dart';

class RewriteTab extends StatelessWidget {
  final WritingReviewCubit cubit;

  const RewriteTab({super.key, required this.cubit});

  @override
  Widget build(BuildContext context) {
    final state = cubit.state;
    final rewrites = state.analysis?.rewrites ?? [];

    // Provider has rewrite text
    if (state.isUsingProvider && state.deepAnalysis != null) {
      return ListView(
        padding: const EdgeInsets.all(10),
        children: [
          const Text('AI 改写建议', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: WritingColors.textDim, letterSpacing: 0.8)),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: WritingColors.surface2, borderRadius: BorderRadius.circular(8), border: Border(left: BorderSide(color: WritingColors.accent3, width: 3))),
            child: const Text('改写功能需要通过 /cycle 端点获取', style: TextStyle(fontSize: 12, color: WritingColors.textDim)),
          ),
        ],
      );
    }

    if (rewrites.isEmpty) {
      return const Center(
        child: Text('暂无改写建议。', style: TextStyle(fontSize: 12, color: WritingColors.textDim)),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(10),
      children: [
        const Text('改写建议 — 点击「定位到此处」跳转到对应位置修改', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: WritingColors.textDim, letterSpacing: 0.8)),
        const SizedBox(height: 8),
        ...rewrites.map((r) => Padding(padding: const EdgeInsets.only(bottom: 8), child: GuideCard.rewrite(r, onJumpTo: () => cubit.jumpToLine(r.line)))),
      ],
    );
  }
}
