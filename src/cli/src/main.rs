//! material — 写作素材收集与整理 CLI(CODE 循环)。
//!
//! 用法:
//!   material collect "想法"      # C-Capture:记录到今日日志
//!   material organize            # O-Organize:LLM 提取主题 → 更新日志 YAML 归属
//!   material distill <主题>       # D-Distill:聚合条目 → materials/<主题>.md
//!   material express <主题>       # E-Express:v2 预留

use std::path::PathBuf;

use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(
    name = "material",
    about = "写作素材收集与整理(CODE:collect → organize → distill → express)",
    version
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// C-Capture:把想法记录到今日日志
    Collect { text: String },
    /// O-Organize:LLM 从日志提取主题,更新日志 YAML 归属(保留人工标注)
    Organize,
    /// D-Distill:按主题聚合日志条目 → materials/<主题>.md
    Distill { topic: String },
    /// E-Express:素材 → 成稿(v2 预留)
    Express { topic: String },
}

fn run(cli: Cli) -> Result<(), String> {
    let workdir = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    match cli.command {
        Commands::Collect { text } => {
            let path = narrative_engineering::journal::collect(&workdir, &text)?;
            println!("已记录:{}", path.display());
            Ok(())
        }
        Commands::Organize => match narrative_engineering::organize::organize(&workdir) {
            Ok(0) => {
                println!("日志中暂无未标注条目");
                Ok(())
            }
            Ok(n) => {
                println!("已更新 {} 条条目归属(建议,可编辑日志 YAML 修正)", n);
                Ok(())
            }
            Err(e) => Err(e),
        },
        Commands::Distill { topic } => {
            let path = narrative_engineering::distill::distill(&workdir, &topic)?;
            println!("已生成:{}", path.display());
            Ok(())
        }
        Commands::Express { topic } => {
            println!("express 为 v2 预留,尚未实现(topic={})", topic);
            Ok(())
        }
    }
}

fn main() {
    let cli = Cli::parse();
    if let Err(e) = run(cli) {
        eprintln!("错误:{e}");
        std::process::exit(1);
    }
}
