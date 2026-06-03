class DeepParagraphReview {
  final int index;
  final String original;
  final String analysis;
  final String tag;
  final DeepComparison? comparison;

  DeepParagraphReview({
    required this.index,
    required this.original,
    required this.analysis,
    required this.tag,
    this.comparison,
  });

  factory DeepParagraphReview.fromJson(Map<String, dynamic> json) {
    return DeepParagraphReview(
      index: json['index'] ?? 0,
      original: json['original'],
      analysis: json['analysis'],
      tag: json['tag'],
      comparison: json['comparison'] != null
          ? DeepComparison.fromJson(json['comparison'])
          : null,
    );
  }
}

class DeepComparison {
  final String type;
  final String? issue;
  final String? demo;

  DeepComparison({required this.type, this.issue, this.demo});

  factory DeepComparison.fromJson(Map<String, dynamic> json) {
    return DeepComparison(
      type: json['type'],
      issue: json['issue'],
      demo: json['demo'],
    );
  }
}

class DeepSuggestion {
  final int priority;
  final String action;
  final String detail;
  final int? paragraphIndex;

  DeepSuggestion({
    required this.priority,
    required this.action,
    required this.detail,
    this.paragraphIndex,
  });

  factory DeepSuggestion.fromJson(Map<String, dynamic> json) {
    return DeepSuggestion(
      priority: json['priority'],
      action: json['action'],
      detail: json['detail'],
      paragraphIndex: json['paragraph_index'],
    );
  }
}

class DeepStyleUsage {
  final List<String> samplesUsed;
  final double confidence;

  DeepStyleUsage({required this.samplesUsed, required this.confidence});

  factory DeepStyleUsage.fromJson(Map<String, dynamic> json) {
    return DeepStyleUsage(
      samplesUsed: (json['samples_used'] as List).cast<String>(),
      confidence: (json['confidence'] as num).toDouble(),
    );
  }
}

class DeepReview {
  final String articleTitle;
  final String summary;
  final List<DeepParagraphReview> paragraphs;
  final List<DeepSuggestion> suggestions;
  final DeepStyleUsage? styleUsage;
  final bool isFromRemote;

  DeepReview({
    required this.articleTitle,
    required this.summary,
    required this.paragraphs,
    required this.suggestions,
    this.styleUsage,
    this.isFromRemote = false,
  });

  factory DeepReview.fromJson(Map<String, dynamic> json) {
    return DeepReview(
      articleTitle: json['article_title'],
      summary: json['summary'],
      paragraphs: (json['paragraphs'] as List)
          .map((p) => DeepParagraphReview.fromJson(p))
          .toList(),
      suggestions: (json['suggestions'] as List)
          .map((s) => DeepSuggestion.fromJson(s))
          .toList(),
      styleUsage: json['style_usage'] != null
          ? DeepStyleUsage.fromJson(json['style_usage'])
          : null,
    );
  }
}
