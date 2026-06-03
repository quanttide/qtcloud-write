import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/blocs/writing_review_cubit.dart';


void main() {
  group('WritingReviewCubit deep analysis', () {
    test('runReview with no service falls back to local analysis', () async {
      final cubit = WritingReviewCubit();
      cubit.textChanged('test text');
      await cubit.runReview();
      // No deep service → fallback to local
      expect(cubit.state.isUsingProvider, isFalse);
      expect(cubit.state.analysis, isNotNull);
      cubit.close();
    });

    test('runReview with empty text does nothing', () async {
      final cubit = WritingReviewCubit();
      await cubit.runReview();
      expect(cubit.state.analysis, isNull);
      expect(cubit.state.deepAnalysis, isNull);
      cubit.close();
    });

    test('initial analysis state is null', () {
      final cubit = WritingReviewCubit();
      expect(cubit.state.analysis, isNull);
      expect(cubit.state.deepAnalysis, isNull);
      expect(cubit.state.isUsingProvider, isFalse);
      cubit.close();
    });
  });
}
