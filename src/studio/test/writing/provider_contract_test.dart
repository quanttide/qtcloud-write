import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:pact_dart/pact_dart.dart';
import 'package:http/http.dart' as http;
import 'package:qtcloud_write_studio/models/deep_analysis.dart';

void main() {
  group('Provider API contract', () {
    late PactMockService pact;

    setUp(() {
      pact = PactMockService('qtcloud_write_studio', 'qtcloud_write_provider');
    });

    tearDown(() {
      pact.reset();
    });

    test('POST /review returns DeepReview-compatible response', () async {
      // 定义期望的请求和响应
      pact
          .newInteraction('a review request')
          .given('provider is running with valid API key')
          .uponReceiving('a request to review an article')
          .withRequest('POST', '/review', headers: {
        'Content-Type': 'application/json',
      }, body: {
        'title': '测试文章',
        'paragraphs': ['第一段内容', '第二段内容'],
        'author': 'test',
        'tag': 'bad',
      }).willRespondWith(200, headers: {
        'Content-Type': 'application/json',
      }, body: {
        'article_title': '测试文章',
        'author': 'test',
        'tag': 'bad',
        'summary': '分析结果摘要',
        'paragraphs': [
          {
            'original': '第一段内容',
            'analysis': '开篇引入场景',
            'tag': '起',
          },
          {
            'original': '第二段内容',
            'analysis': '承接发展',
            'tag': '承',
          },
        ],
        'is_style_available': false,
        'suggestions': [],
      });

      pact.run(secure: false);

      // 发出真实请求
      final uri = Uri.parse('http://localhost:1235/review');
      final res = await http.post(uri,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            'title': '测试文章',
            'paragraphs': ['第一段内容', '第二段内容'],
            'author': 'test',
            'tag': 'bad',
          }));

      // 验证响应能被 Dart 模型解析
      expect(res.statusCode, equals(200));
      final review = DeepReview.fromJson(jsonDecode(res.body));
      expect(review.articleTitle, equals('测试文章'));
      expect(review.paragraphs.length, equals(2));
      expect(review.paragraphs[0].tag, equals('起'));

      // 写入 pact 文件
      expect(pact.hasMatchedInteractions(), isTrue);
      pact.writePactFile(overwrite: true);
    });

    test('POST /reflect returns GapAnalysis-compatible response', () async {
      pact
          .newInteraction('a reflect request')
          .given('provider is running')
          .uponReceiving('a request to reflect on text')
          .withRequest('POST', '/reflect', headers: {
        'Content-Type': 'application/json',
      }, body: {
        'text': '他推开门走了出去。',
      }).willRespondWith(200, headers: {
        'Content-Type': 'application/json',
      });

      pact.run(secure: false);

      final uri = Uri.parse('http://localhost:1235/reflect');
      final res = await http.post(uri,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'text': '他推开门走了出去。'}));

      expect(res.statusCode, equals(200));
      pact.writePactFile(overwrite: true);
    });
  });
}
