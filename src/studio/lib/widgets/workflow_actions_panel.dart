/// 流程操作面板——复现 CLI 四命令：收集 → 分组 → 初稿 → 定稿。
///
/// 挂在章节导航底部：想法输入 + 收集；LLM 分组；按当前选中章节
/// 提供"生成初稿 / 生成定稿"。
library;

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../blocs/editor/editor_bloc.dart';
import '../blocs/workflow/workflow_bloc.dart';
import '../services/llm_client.dart';
import '../workflow/distill.dart' as distill_mod;
import '../workflow/express.dart' as express_mod;
import '../workflow/journal.dart' as journal_mod;
import '../workflow/organize.dart' as organize_mod;

/// 流程操作面板
class WorkflowActionsPanel extends StatefulWidget {
  final String workdir;

  const WorkflowActionsPanel({super.key, required this.workdir});

  @override
  State<WorkflowActionsPanel> createState() => _WorkflowActionsPanelState();
}

class _WorkflowActionsPanelState extends State<WorkflowActionsPanel> {
  final TextEditingController _inputController = TextEditingController();
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _inputController.dispose();
    super.dispose();
  }

  void _showMessage(String msg, {bool isError = false}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(
        content: Text(msg, maxLines: 3, overflow: TextOverflow.ellipsis),
        backgroundColor: isError ? Colors.red.shade400 : null,
        duration: const Duration(seconds: 4),
      ));
  }

  Future<String> Function(String) get _llm {
    final llm = context.read<LLMClient>();
    return llm.completeText;
  }

  Future<void> _collect() async {
    final text = _inputController.text.trim();
    if (text.isEmpty) {
      _showMessage('先输入一条想法', isError: true);
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final path = await journal_mod.collect(widget.workdir, text);
      _inputController.clear();
      if (mounted) context.read<WorkflowBloc>().add(const LoadWorkflow());
      _showMessage('已记录:$path');
    } catch (e) {
      _showMessage('收集失败: $e', isError: true);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _organize() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final updated = await organize_mod.organize(widget.workdir, _llm);
      if (updated == 0) {
        _showMessage('没有新的未分组条目');
      } else {
        final groups = await organize_mod.writeGroups(widget.workdir);
        if (mounted) context.read<WorkflowBloc>().add(const LoadWorkflow());
        _showMessage('已更新 $updated 条归属,生成 ${groups.length} 个分组');
      }
    } catch (e) {
      _showMessage('分组失败: $e', isError: true);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _distill(String topic) async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final path = await distill_mod.distill(widget.workdir, topic, _llm);
      if (mounted) context.read<WorkflowBloc>().add(const LoadWorkflow());
      _showMessage('已生成初稿:$path');
    } catch (e) {
      _showMessage('生成初稿失败: $e', isError: true);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _express(String topic) async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final path =
          await express_mod.express(widget.workdir, topic, llm: _llm);
      if (mounted) context.read<WorkflowBloc>().add(const LoadWorkflow());
      _showMessage('已生成定稿:$path');
    } catch (e) {
      _showMessage('生成定稿失败: $e', isError: true);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  /// 当前选中章节的阶段 id 与主题（文件名即主题）
  (String?, String?) get _selection {
    final editor = context.read<EditorBloc>().state;
    if (editor.chapterId == null) return (null, null);
    final stageId = context.read<WorkflowBloc>().state is WorkflowLoaded
        ? (context.read<WorkflowBloc>().state as WorkflowLoaded)
            .workflow
            .stages
            .expand((s) => s.chapters)
            .where((c) => c.id == editor.chapterId)
            .firstOrNull
            ?.stageId
        : null;
    return (stageId, editor.chapterId);
  }

  @override
  Widget build(BuildContext context) {
    final (stageId, topic) = _selection;
    final isGroup = stageId == '02_分组';
    final isDraft = stageId == '03_初稿';

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        border: Border(top: BorderSide(color: Colors.grey.shade200)),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            '流程操作',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _inputController,
                  enabled: !_busy,
                  decoration: const InputDecoration(
                    hintText: '记录一条想法...',
                    isDense: true,
                    border: OutlineInputBorder(),
                  ),
                  style: const TextStyle(fontSize: 12),
                  onSubmitted: (_) => _collect(),
                ),
              ),
              const SizedBox(width: 8),
              FilledButton.tonal(
                onPressed: _busy ? null : _collect,
                style: FilledButton.styleFrom(
                  visualDensity: VisualDensity.compact,
                ),
                child: const Text('收集', style: TextStyle(fontSize: 12)),
              ),
            ],
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: _busy ? null : _organize,
            icon: _busy
                ? const SizedBox(
                    width: 14,
                    height: 14,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.group_work_outlined, size: 16),
            label: const Text('LLM 分组', style: TextStyle(fontSize: 12)),
            style: OutlinedButton.styleFrom(
              visualDensity: VisualDensity.compact,
            ),
          ),
          if (isGroup) ...[
            const SizedBox(height: 8),
            FilledButton.icon(
              onPressed: _busy ? null : () => _distill(topic!),
              icon: _busy
                  ? const SizedBox(
                      width: 14,
                      height: 14,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.auto_awesome, size: 16),
              label: Text('生成初稿: $topic', style: const TextStyle(fontSize: 12)),
              style: FilledButton.styleFrom(
                visualDensity: VisualDensity.compact,
              ),
            ),
          ],
          if (isDraft) ...[
            const SizedBox(height: 8),
            FilledButton.icon(
              onPressed: _busy ? null : () => _express(topic!),
              icon: _busy
                  ? const SizedBox(
                      width: 14,
                      height: 14,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.flag_outlined, size: 16),
              label: Text('生成定稿: $topic', style: const TextStyle(fontSize: 12)),
              style: FilledButton.styleFrom(
                visualDensity: VisualDensity.compact,
              ),
            ),
          ],
          if (_error != null) ...[
            const SizedBox(height: 8),
            Text(
              _error!,
              style: TextStyle(fontSize: 11, color: Colors.red.shade400),
            ),
          ],
        ],
      ),
    );
  }
}
