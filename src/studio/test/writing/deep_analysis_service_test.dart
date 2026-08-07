import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/blocs/writing_review_cubit.dart';

void main() {
  group('WritingReviewCubit', () {
    test('runReview with local service returns result', () async {
      final cubit = WritingReviewCubit.test();
      cubit.textChanged('test text');
      await cubit.runReview();
      expect(cubit.state.reviewResponse, isNotNull);
      cubit.close();
    });

    test('runReview with empty text does nothing', () async {
      final cubit = WritingReviewCubit.test();
      await cubit.runReview();
      expect(cubit.state.reviewResponse, isNull);
      cubit.close();
    });

    test('initial state is empty', () {
      final cubit = WritingReviewCubit.test();
      expect(cubit.state.reviewResponse, isNull);
      cubit.close();
    });
  });
}
