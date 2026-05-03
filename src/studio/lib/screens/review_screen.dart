import 'package:flutter/material.dart';
import '../models/review.dart';
import '../services/api_service.dart';

class ReviewScreen extends StatefulWidget {
  final ApiService api;
  const ReviewScreen({super.key, required this.api});

  @override
  State<ReviewScreen> createState() => _ReviewScreenState();
}

class _ReviewScreenState extends State<ReviewScreen> {
  Review? _review;
  bool _loading = false;
  String? _error;

  final _titleCtrl = TextEditingController();
  final _authorCtrl = TextEditingController(text: 'test');
  final _tagCtrl = TextEditingController(text: 'bad');
  final _bodyCtrl = TextEditingController();

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final paragraphs = _bodyCtrl.text
          .split('\n')
          .where((l) => l.trim().isNotEmpty)
          .toList();

      final review = await widget.api.submitReview(
        title: _titleCtrl.text,
        paragraphs: paragraphs,
        author: _authorCtrl.text,
        tag: _tagCtrl.text,
      );
      setState(() => _review = review);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('写作云评审')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TextField(controller: _titleCtrl, decoration: const InputDecoration(labelText: '标题')),
            TextField(controller: _authorCtrl, decoration: const InputDecoration(labelText: '作者')),
            TextField(controller: _tagCtrl, decoration: const InputDecoration(labelText: '标签 (good/bad)')),
            TextField(
              controller: _bodyCtrl,
              maxLines: 8,
              decoration: const InputDecoration(labelText: '正文（每行一段）'),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: _loading ? null : _submit,
              child: _loading ? const CircularProgressIndicator() : const Text('提交评审'),
            ),
            if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
            if (_review != null) ...[
              const Divider(height: 32),
              Text('总结：${_review!.summary}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 8),
              if (_review!.suggestions.isNotEmpty) ...[
                const Text('修改建议：', style: TextStyle(fontWeight: FontWeight.bold)),
                ..._review!.suggestions.map((s) => Text('${s.priority}. ${s.action}：${s.detail}')),
                const SizedBox(height: 12),
              ],
              const Divider(),
              ..._review!.paragraphs.map((p) => _buildPara(p)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildPara(ParagraphReview p) {
    final isBad = p.comparison?.type == 'bad';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(border: Border.all(color: Colors.grey.shade300)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: _tagColor(p.tag),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(p.tag, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white)),
            ),
            const SizedBox(width: 8),
            Expanded(child: Text(p.analysis, style: const TextStyle(fontSize: 13, fontStyle: FontStyle.italic))),
          ]),
          const SizedBox(height: 6),
          Text(p.original, style: const TextStyle(fontSize: 13)),
          if (isBad) ...[
            const SizedBox(height: 6),
            Container(
              padding: const EdgeInsets.all(8),
              color: Colors.red.shade50,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('坏：${p.comparison!.issue}', style: const TextStyle(fontSize: 13, color: Colors.red)),
                  if (p.comparison!.demo != null)
                    Text('好：${p.comparison!.demo}', style: const TextStyle(fontSize: 13, color: Colors.blue)),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Color _tagColor(String tag) {
    switch (tag) {
      case '起': return Colors.green;
      case '承': return Colors.blue;
      case '转': return Colors.orange;
      case '合': return Colors.purple;
      default: return Colors.grey;
    }
  }
}
