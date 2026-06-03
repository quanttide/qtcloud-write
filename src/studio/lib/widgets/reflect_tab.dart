import 'package:flutter/material.dart';
import '../blocs/writing_review_cubit.dart';
import '../themes/writing_theme.dart';

class ReflectTab extends StatelessWidget {
  final WritingReviewCubit cubit;

  const ReflectTab({super.key, required this.cubit});

  @override
  Widget build(BuildContext context) {
    final state = cubit.state;
    if (state.reviewResponse == null) {
      return const Center(child: Text('等待评审...', style: TextStyle(fontSize: 12, color: WritingColors.textDim)));
    }
    return const Center(child: Text('Reflect 功能需直接调用 /reflect 端点', style: TextStyle(fontSize: 12, color: WritingColors.textDim)));
  }
}
