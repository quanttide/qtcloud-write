class ParagraphReview {
  final String original;
  final String analysis;
  final String tag;
  final Comparison? comparison;

  ParagraphReview({
    required this.original,
    required this.analysis,
    required this.tag,
    this.comparison,
  });

  factory ParagraphReview.fromJson(Map<String, dynamic> json) {
    return ParagraphReview(
      original: json['original'],
      analysis: json['analysis'],
      tag: json['tag'],
      comparison: json['comparison'] != null
          ? Comparison.fromJson(json['comparison'])
          : null,
    );
  }
}

class Comparison {
  final String type;
  final String? issue;
  final String? demo;

  Comparison({required this.type, this.issue, this.demo});

  factory Comparison.fromJson(Map<String, dynamic> json) {
    return Comparison(
      type: json['type'],
      issue: json['issue'],
      demo: json['demo'],
    );
  }
}

class Suggestion {
  final int priority;
  final String action;
  final String detail;

  Suggestion({required this.priority, required this.action, required this.detail});

  factory Suggestion.fromJson(Map<String, dynamic> json) {
    return Suggestion(
      priority: json['priority'],
      action: json['action'],
      detail: json['detail'],
    );
  }
}

class Review {
  final String articleTitle;
  final String author;
  final String tag;
  final String summary;
  final List<ParagraphReview> paragraphs;
  final bool isStyleAvailable;
  final List<Suggestion> suggestions;

  Review({
    required this.articleTitle,
    required this.author,
    required this.tag,
    required this.summary,
    required this.paragraphs,
    required this.isStyleAvailable,
    required this.suggestions,
  });

  factory Review.fromJson(Map<String, dynamic> json) {
    return Review(
      articleTitle: json['article_title'],
      author: json['author'],
      tag: json['tag'],
      summary: json['summary'],
      paragraphs: (json['paragraphs'] as List)
          .map((p) => ParagraphReview.fromJson(p))
          .toList(),
      isStyleAvailable: json['is_style_available'],
      suggestions: (json['suggestions'] as List)
          .map((s) => Suggestion.fromJson(s))
          .toList(),
    );
  }
}
