import 'package:flutter_test/flutter_test.dart';
import 'package:qtcloud_write_studio/models/deep_analysis.dart';

void main() {
  group('Provider API — fromJson 契约验证', () {
    test('DeepReview.fromJson 解析完整 review 响应', () {
      final json = {
        'article_title': '测试文章',
        'author': 'test',
        'tag': 'bad',
        'summary': '分析结果摘要',
        'paragraphs': [
          {'original': '第一段', 'analysis': '开篇', 'tag': '起'},
          {'original': '第二段', 'analysis': '承接', 'tag': '承'},
          {'original': '第三段', 'analysis': '转折', 'tag': '转'},
          {'original': '第四段', 'analysis': '收束', 'tag': '合'},
        ],
        'is_style_available': true,
        'suggestions': [
          {'priority': 1, 'action': '换起点', 'detail': '从个人困境出发'},
        ],
      };

      final review = DeepReview.fromJson(json);
      expect(review.articleTitle, '测试文章');
      expect(review.paragraphs, hasLength(4));
      expect(review.paragraphs[2].tag, '转');
      expect(review.suggestions, hasLength(1));
      expect(review.suggestions[0].priority, 1);
    });

    test('DeepReview.fromJson 处理段落含 comparison', () {
      final json = {
        'article_title': 't',
        'author': 'a',
        'tag': 'bad',
        'summary': 's',
        'paragraphs': [
          {
            'original': '开头段',
            'analysis': '分析',
            'tag': '起',
            'comparison': {'type': 'bad', 'issue': '风格不一致', 'demo': '应以个人困境出发'},
          },
        ],
        'is_style_available': true,
        'suggestions': [],
      };

      final review = DeepReview.fromJson(json);
      expect(review.paragraphs[0].comparison, isNotNull);
      expect(review.paragraphs[0].comparison!.type, 'bad');
    });

    test('DeepReview.fromJson 处理空 paragraphs', () {
      final json = {
        'article_title': 't',
        'author': 'a',
        'tag': 'bad',
        'summary': 's',
        'paragraphs': [],
        'is_style_available': false,
        'suggestions': [],
      };

      final review = DeepReview.fromJson(json);
      expect(review.paragraphs, isEmpty);
    });

    test('DeepReview.fromJson 处理 null comparison', () {
      final json = {
        'article_title': 't',
        'author': 'a',
        'tag': 'bad',
        'summary': 's',
        'paragraphs': [
          {'original': 'p1', 'analysis': 'a1', 'tag': '起', 'comparison': null},
        ],
        'is_style_available': false,
        'suggestions': [],
      };

      final review = DeepReview.fromJson(json);
      expect(review.paragraphs[0].comparison, isNull);
    });
  });
}
