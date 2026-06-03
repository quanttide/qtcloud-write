import 'package:flutter/material.dart';
import '../blocs/writing_review_cubit.dart';
import '../themes/writing_theme.dart';
import 'guide_card.dart';

class ReflectTab extends StatelessWidget {
  final WritingReviewCubit cubit;

  const ReflectTab({super.key, required this.cubit});

  @override
  Widget build(BuildContext context) {
    final state = cubit.state;

    if (state.deepAnalysis == null) {
      return const Center(
        child: Text('等待评审...', style: TextStyle(fontSize: 12, color: WritingColors.textDim)),
      );
    }

    return const Center(
      child: Text('可写位置功能需对接 Provider 后启用', style: TextStyle(fontSize: 12, color: WritingColors.textDim)),
    );
  }
}
