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
    final deep = state.deepAnalysis;

    if (state.isLoading) {
      return const Center(child: Text('分析中...', style: TextStyle(fontSize: 12, color: WritingColors.textDim)));
    }
    if (deep == null) {
      return const Center(child: Text('等待评审...', style: TextStyle(fontSize: 12, color: WritingColors.textDim)));
    }

    return _ProviderReviewContent(deep: deep);
  }
}

class _ProviderReviewContent extends StatelessWidget {
  final DeepReview deep;
  const _ProviderReviewContent({required this.deep});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(10),
      children: [
        const Text('AI 分析结果', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: WritingColors.textDim, letterSpacing: 0.8)),
        const SizedBox(height: 6),
        Text(deep.summary, style: const TextStyle(fontSize: 12, color: WritingColors.text, height: 1.5)),
        if (deep.paragraphs.isNotEmpty) ...[
          const SizedBox(height: 8),
          const Text('段落结构', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: WritingColors.textDim, letterSpacing: 0.8)),
          const SizedBox(height: 4),
          ...deep.paragraphs.map((p) => _ParaCard(p: p)),
        ],
        if (deep.suggestions.isNotEmpty) ...[
          const SizedBox(height: 8),
          const Text('改进建议', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: WritingColors.textDim, letterSpacing: 0.8)),
          const SizedBox(height: 4),
          ...deep.suggestions.map((s) => _SugCard(s: s)),
        ],
      ],
    );
  }
}

class _ParaCard extends StatelessWidget {
  final DeepParagraphReview p;
  const _ParaCard({required this.p});

  Color _color(String tag) => switch (tag) { '起' => WritingColors.accent, '承' => WritingColors.accent2, '转' => WritingColors.accent3, '合' => WritingColors.red, _ => WritingColors.textDim };

  @override
  Widget build(BuildContext context) {
    final c = _color(p.tag);
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(color: WritingColors.surface2, borderRadius: BorderRadius.circular(6), border: Border(left: BorderSide(color: c, width: 3))),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1), decoration: BoxDecoration(color: c.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(3)),
            child: Text(p.tag, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: c))),
          const SizedBox(width: 6),
          Expanded(child: Text(p.original.length > 60 ? '${p.original.substring(0, 60)}…' : p.original, style: const TextStyle(fontSize: 11, color: WritingColors.textDim), maxLines: 1, overflow: TextOverflow.ellipsis)),
        ]),
        const SizedBox(height: 4),
        Text(p.analysis, style: const TextStyle(fontSize: 11, color: WritingColors.text, height: 1.5)),
      ]),
    );
  }
}

class _SugCard extends StatelessWidget {
  final DeepSuggestion s;
  const _SugCard({required this.s});
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

