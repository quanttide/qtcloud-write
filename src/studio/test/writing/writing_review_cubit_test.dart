import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/blocs/writing_review_cubit.dart';

void main() {
  group('WritingReviewCubit', () {
    test('initial state is correct', () {
      final cubit = WritingReviewCubit.test();
      expect(cubit.state.text, isEmpty);
      expect(cubit.state.reviewResponse, isNull);
      expect(cubit.state.currentTab, ReviewPanelTab.review);
      expect(cubit.state.round, 1);
      expect(cubit.state.isLoading, isFalse);
      expect(cubit.state.charCount, 0);
      cubit.close();
    });

    test('textChanged updates text', () {
      final cubit = WritingReviewCubit.test();
      cubit.textChanged('hello world');
      expect(cubit.state.text, 'hello world');
      expect(cubit.state.charCount, 11);
      cubit.close();
    });

    test('textChanged preserves analysis', () async {
      final cubit = WritingReviewCubit.test();
      await cubit.loadSample();
      expect(cubit.state.reviewResponse, isNotNull);
      final originalSummary = cubit.state.reviewResponse!.overallSummary;
      cubit.textChanged('modified text');
      expect(cubit.state.reviewResponse, isNotNull);
      expect(cubit.state.reviewResponse!.overallSummary, originalSummary);
      cubit.close();
    });

    test('runReview with empty text does nothing', () async {
      final cubit = WritingReviewCubit.test();
      await cubit.runReview();
      expect(cubit.state.reviewResponse, isNull);
      cubit.close();
    });

    test('runReview analyzes text', () async {
      final cubit = WritingReviewCubit.test();
      cubit.textChanged('test content');
      await cubit.runReview();
      expect(cubit.state.reviewResponse, isNotNull);
      expect(cubit.state.isLoading, isFalse);
      cubit.close();
    });

    test('loadSample loads and analyzes sample text', () async {
      final cubit = WritingReviewCubit.test();
      await cubit.loadSample();
      expect(cubit.state.text, isNotEmpty);
      expect(cubit.state.reviewResponse, isNotNull);
      cubit.close();
    });

    test('switchTab changes current tab', () {
      final cubit = WritingReviewCubit.test();
      expect(cubit.state.currentTab, ReviewPanelTab.review);
      cubit.switchTab(ReviewPanelTab.reflect);
      expect(cubit.state.currentTab, ReviewPanelTab.reflect);
      cubit.switchTab(ReviewPanelTab.rewrite);
      expect(cubit.state.currentTab, ReviewPanelTab.rewrite);
      cubit.switchTab(ReviewPanelTab.review);
      expect(cubit.state.currentTab, ReviewPanelTab.review);
      cubit.close();
    });

    test('jumpToLine sets pendingJumpLine', () async {
      final cubit = WritingReviewCubit.test();
      await cubit.loadSample();
      cubit.jumpToLine(5);
      expect(cubit.state.pendingJumpLine, 5);
      cubit.close();
    });

    test('clearPendingJump resets pendingJumpLine', () async {
      final cubit = WritingReviewCubit.test();
      await cubit.loadSample();
      cubit.jumpToLine(5);
      expect(cubit.state.pendingJumpLine, 5);
      cubit.clearPendingJump();
      expect(cubit.state.pendingJumpLine, isNull);
      cubit.close();
    });

    test('multiple text changes work sequentially', () {
      final cubit = WritingReviewCubit.test();
      cubit.textChanged('a');
      expect(cubit.state.text, 'a');
      cubit.textChanged('ab');
      expect(cubit.state.text, 'ab');
      cubit.textChanged('abc');
      expect(cubit.state.text, 'abc');
      expect(cubit.state.charCount, 3);
      cubit.close();
    });

    test('loadSample can be called multiple times', () async {
      final cubit = WritingReviewCubit.test();
      await cubit.loadSample();
      expect(cubit.state.reviewResponse, isNotNull);
      cubit.textChanged('modified');
      await cubit.loadSample();
      expect(cubit.state.reviewResponse, isNotNull);
      cubit.close();
    });
  });
}
