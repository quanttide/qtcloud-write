import 'package:flutter/material.dart';
import '../blocs/writing_review_cubit.dart';
import '../models/analysis.dart';
import '../models/deep_analysis.dart';
import '../themes/writing_theme.dart';
import 'style_bar.dart';

class ReviewTab extends StatelessWidget {
  final WritingReviewCubit cubit;

  const ReviewTab({super.key, required this.cubit});

  @override
  Widget build(BuildContext context) {
    final state = cubit.state;
    final analysis = state.analysis;
    final deep = state.deepAnalysis;

    // Provider 分析可用时优先展示
    if (state.isUsingProvider && deep != null) {
      return _ProviderReviewContent(deep: deep);
    }

    if (state.isLoading) {
      return const Center(
        child: Text('分析中...', style: TextStyle(fontSize: 12, color: WritingColors.textDim)),
      );
    }

    // 回退到本地分析
    if (analysis == null) {
      return Center(
        child: Text(
          state.isLoading ? '分析中...' : '等待评审...',
          style: const TextStyle(fontSize: 12, color: WritingColors.textDim),
        ),
      );
    }

    return _LocalReviewContent(analysis: analysis, cubit: cubit);
  }
}

class _LocalReviewContent extends StatelessWidget {
  final AnalysisResult analysis;
  final WritingReviewCubit cubit;

  const _LocalReviewContent({required this.analysis, required this.cubit});

  @override
  Widget build(BuildContext context) {
    final gaps = analysis.gaps;
    final styles = analysis.styles;

    return ListView(
      padding: const EdgeInsets.all(10),
      children: [
        if (gaps.isNotEmpty) ...[
          const Text(
            '叙事空隙 — 节奏偏快的位置，可补充细节',
            style: TextStyle(
              fontSize: 11, fontWeight: FontWeight.w600,
              color: WritingColors.textDim, letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 4),
          ...gaps.take(10).map((g) => _GapItem(
                gap: g,
                onTap: () => cubit.jumpToLine(g.line),
              )),
          const SizedBox(height: 8),
        ],
        if (styles.isNotEmpty) ...[
          const Text(
            '风格评分 — 数值越高越好',
            style: TextStyle(
              fontSize: 11, fontWeight: FontWeight.w600,
              color: WritingColors.textDim, letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 4),
          ...styles.map((s) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: StyleBar(name: s.name, score: s.score),
              )),
        ],
        const SizedBox(height: 8),
        Center(
          child: Text.rich(
            TextSpan(
              text: '${analysis.avgScore.round()} ',
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: WritingColors.accent),
              children: const [TextSpan(text: '/100', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w400, color: WritingColors.textDim))],
            ),
          ),
        ),
      ],
    );
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

class _GapItem extends StatelessWidget {
  final Gap gap;
  final VoidCallback onTap;

  const _GapItem({required this.gap, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final dot = gap.score == 3
        ? '🟢'
        : gap.score == 2
            ? '🟡'
            : '🔴';
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        child: Row(
          children: [
            Text(dot, style: const TextStyle(fontSize: 12)),
            const SizedBox(width: 6),
            SizedBox(
              width: 56,
              child: Text(
                gap.label,
                style: const TextStyle(fontSize: 12, color: WritingColors.textDim),
              ),
            ),
            const Spacer(),
            Text(
              'L${gap.line}',
              style: const TextStyle(fontSize: 11, color: WritingColors.textDim),
            ),
          ],
        ),
      ),
    );
  }
}
