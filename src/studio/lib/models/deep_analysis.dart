class CriterionAnalysis {
  final String criterionId;
  final double alignmentScore;
  final List<Deviation> deviations;

  CriterionAnalysis({
    required this.criterionId,
    required this.alignmentScore,
    required this.deviations,
  });

  factory CriterionAnalysis.fromJson(Map<String, dynamic> json) {
    return CriterionAnalysis(
      criterionId: json['criterion_id'],
      alignmentScore: (json['alignment_score'] as num).toDouble(),
      deviations: (json['deviations'] as List)
          .map((d) => Deviation.fromJson(d))
          .toList(),
    );
  }
}

class Deviation {
  final String location;
  final String explanation;
  final String suggestedAlignment;

  Deviation({
    required this.location,
    required this.explanation,
    required this.suggestedAlignment,
  });

  factory Deviation.fromJson(Map<String, dynamic> json) {
    return Deviation(
      location: json['location'] ?? '',
      explanation: json['explanation'] ?? '',
      suggestedAlignment: json['suggested_alignment'] ?? '',
    );
  }
}

class ReviewResponse {
  final List<CriterionAnalysis> criteriaAnalysis;
  final String overallSummary;

  ReviewResponse({
    required this.criteriaAnalysis,
    required this.overallSummary,
  });

  factory ReviewResponse.fromJson(Map<String, dynamic> json) {
    return ReviewResponse(
      criteriaAnalysis: (json['criteria_analysis'] as List)
          .map((a) => CriterionAnalysis.fromJson(a))
          .toList(),
      overallSummary: json['overall_summary'] ?? '',
    );
  }
}
