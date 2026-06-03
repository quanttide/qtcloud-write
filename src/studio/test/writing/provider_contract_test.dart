import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/models/deep_analysis.dart';

void main() {
  group('Provider API — fromJson 契约验证', () {
    test('DeepReview.fromJson 解析完整 review 响应', () {
      final json = {
        'article_title': '测试文章',
        'summary': '分析结果摘要',
        'paragraphs': [
          {'index': 0, 'original': '第一段', 'analysis': '开篇', 'tag': '起'},
          {'index': 1, 'original': '第二段', 'analysis': '承接', 'tag': '承'},
          {'index': 2, 'original': '第三段', 'analysis': '转折', 'tag': '转'},
          {'index': 3, 'original': '第四段', 'analysis': '收束', 'tag': '合'},
        ],
        'suggestions': [
          {'priority': 1, 'action': '换起点', 'detail': '从个人困境出发', 'paragraph_index': 0},
        ],
        'style_usage': {
          'samples_used': ['好风格'],
          'confidence': 0.85,
        },
      };

      final review = DeepReview.fromJson(json);
      expect(review.articleTitle, '测试文章');
      expect(review.paragraphs, hasLength(4));
      expect(review.paragraphs[0].index, 0);
      expect(review.paragraphs[2].tag, '转');
      expect(review.suggestions, hasLength(1));
      expect(review.suggestions[0].paragraphIndex, 0);
      expect(review.styleUsage, isNotNull);
      expect(review.styleUsage!.samplesUsed, ['好风格']);
    });

    test('DeepReview.fromJson 处理段落含 comparison', () {
      final json = {
        'article_title': 't',
        'summary': 's',
        'paragraphs': [
          {
            'index': 0,
            'original': '开头段',
            'analysis': '分析',
            'tag': '起',
            'comparison': {'type': 'bad', 'issue': '风格不一致', 'demo': '应以个人困境出发'},
          },
        ],
        'suggestions': [],
      };

      final review = DeepReview.fromJson(json);
      expect(review.paragraphs[0].comparison, isNotNull);
      expect(review.paragraphs[0].comparison!.type, 'bad');
    });

    test('DeepReview.fromJson 处理空 paragraphs', () {
      final json = {
        'article_title': 't',
        'summary': 's',
        'paragraphs': [],
        'suggestions': [],
      };

      final review = DeepReview.fromJson(json);
      expect(review.paragraphs, isEmpty);
    });

    test('DeepReview.fromJson 处理无 style_usage', () {
      final json = {
        'article_title': 't',
        'summary': 's',
        'paragraphs': [
          {'index': 0, 'original': 'p1', 'analysis': 'a1', 'tag': '起'},
        ],
        'suggestions': [],
      };

      final review = DeepReview.fromJson(json);
      expect(review.styleUsage, isNull);
    });

    test('DeepReview.fromJson 处理含 paragraph_index 的 suggestion', () {
      final json = {
        'article_title': 't',
        'summary': 's',
        'paragraphs': [],
        'suggestions': [
          {'priority': 1, 'action': '改', 'detail': '改这段', 'paragraph_index': 0},
          {'priority': 2, 'action': '全局', 'detail': '总体建议'},
        ],
      };

      final review = DeepReview.fromJson(json);
      expect(review.suggestions[0].paragraphIndex, 0);
      expect(review.suggestions[1].paragraphIndex, isNull);
    });
  });
}
