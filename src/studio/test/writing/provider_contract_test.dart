import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/models/deep_analysis.dart';

void main() {
  group('ReviewResponse fromJson', () {
    test('解析完整响应', () {
      final json = {
        'dimension_alignments': [
          {
            'dimension_title': '情感表达',
            'alignment_score': 0.35,
            'deviations': [
              {
                'location': '他推开门走了出去。',
                'explanation': '缺少欲说还休',
                'suggested_alignment': '他犹豫了一下才推开门',
              },
            ],
          },
        ],
        'overall_summary': '文本偏离风格。',
      };

      final resp = ReviewResponse.fromJson(json);
      expect(resp.dimensionAlignments, hasLength(1));
      expect(resp.dimensionAlignments[0].dimensionTitle, '情感表达');
      expect(resp.dimensionAlignments[0].alignmentScore, 0.35);
      expect(resp.dimensionAlignments[0].deviations, hasLength(1));
      expect(resp.overallSummary, '文本偏离风格。');
    });

    test('解析空分析', () {
      final json = {'dimension_alignments': [], 'overall_summary': ''};
      final resp = ReviewResponse.fromJson(json);
      expect(resp.dimensionAlignments, isEmpty);
    });
  });
}
