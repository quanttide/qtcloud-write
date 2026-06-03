import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/blocs/writing_review_cubit.dart';

void main() {
  group('WritingReviewCubit deep analysis', () {
    test('runReview without remote service uses local', () async {
      final cubit = WritingReviewCubit.test();
      cubit.textChanged('test text');
      await cubit.runReview();
      expect(cubit.state.isUsingProvider, isFalse);
      expect(cubit.state.deepAnalysis, isNotNull);
      cubit.close();
    });

    test('runReview with empty text does nothing', () async {
      final cubit = WritingReviewCubit.test();
      await cubit.runReview();
      expect(cubit.state.deepAnalysis, isNull);
      cubit.close();
    });

    test('initial state is empty', () {
      final cubit = WritingReviewCubit.test();
      expect(cubit.state.deepAnalysis, isNull);
      expect(cubit.state.isUsingProvider, isFalse);
      cubit.close();
    });
  });
}
