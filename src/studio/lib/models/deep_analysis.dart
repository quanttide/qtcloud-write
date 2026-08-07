class DimensionAlignment {
  final String dimensionTitle;
  final double alignmentScore;
  final List<Deviation> deviations;

  DimensionAlignment({
    required this.dimensionTitle,
    required this.alignmentScore,
    required this.deviations,
  });

  factory DimensionAlignment.fromJson(Map<String, dynamic> json) {
    return DimensionAlignment(
      dimensionTitle: json['dimension_title'],
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
  final List<DimensionAlignment> dimensionAlignments;
  final String overallSummary;

  ReviewResponse({
    required this.dimensionAlignments,
    required this.overallSummary,
  });

  factory ReviewResponse.fromJson(Map<String, dynamic> json) {
    return ReviewResponse(
      dimensionAlignments: (json['dimension_alignments'] as List)
          .map((a) => DimensionAlignment.fromJson(a))
          .toList(),
      overallSummary: json['overall_summary'] ?? '',
    );
  }
}
