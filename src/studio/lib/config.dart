/// 数据源配置——通过环境变量指定写作数据根目录（CLI workdir）
///
/// 配置方法（dart-define 注入，编译期常量，跨平台一致）：
/// ```bash
/// flutter run --dart-define=QTCLOUD_WRITE_DATA_PATH=/path/to/workdir \
///             --dart-define=QTCLOUD_WRITE_LLM_API_KEY=sk-xxx
/// ```
/// 未配置时回退默认路径（桌面端：qtcloud-write 的 CLI 示例工作目录）。
library;

import 'dart:io' show Platform;

import 'package:flutter/foundation.dart' show kIsWeb;

/// 写作数据根目录（CLI workdir，含 journal/ groups/ materials/）
String get writeDataPath {
  const fromEnv = String.fromEnvironment('QTCLOUD_WRITE_DATA_PATH');
  if (fromEnv.isNotEmpty) return fromEnv;
  return _defaultRepoPath();
}

/// 桌面端默认路径：qtcloud-write CLI 示例工作目录
/// Web 端无文件系统，返回空（由调用方回退内置数据）
String _defaultRepoPath() {
  if (kIsWeb) return '';
  final home = Platform.environment['HOME'] ?? '';
  if (home.isEmpty) return '';
  return '$home/repos/quanttide/domains/quanttide-write/apps/qtcloud-write/src/cli/examples/fiction-of-founder';
}

/// 数据源是否可用（Web 端无文件系统，不可用）
bool get dataSourceAvailable => writeDataPath.isNotEmpty;
