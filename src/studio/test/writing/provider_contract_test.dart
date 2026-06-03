import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/models/deep_analysis.dart';

void main() {
  group('ReviewResponse fromJson', () {
    test('解析完整响应', () {
      final json = {
        'criteria_analysis': [
          {
            'criterion_id': 'c1',
            'alignment_score': 0.35,
            'deviations': [
              {
                'location': '他推开门走了出去。',
                'explanation': '缺少环境反馈',
                'suggested_alignment': '他推开门，冷风扑面。',
              },
            ],
          },
        ],
        'overall_summary': '文本偏离正面范例。',
      };

      final resp = ReviewResponse.fromJson(json);
      expect(resp.criteriaAnalysis, hasLength(1));
      expect(resp.criteriaAnalysis[0].criterionId, 'c1');
      expect(resp.criteriaAnalysis[0].alignmentScore, 0.35);
      expect(resp.criteriaAnalysis[0].deviations, hasLength(1));
      expect(resp.criteriaAnalysis[0].deviations[0].explanation, '缺少环境反馈');
      expect(resp.overallSummary, '文本偏离正面范例。');
    });

    test('解析空分析', () {
      final json = {
        'criteria_analysis': [],
        'overall_summary': '',
      };
      final resp = ReviewResponse.fromJson(json);
      expect(resp.criteriaAnalysis, isEmpty);
    });
  });
}
