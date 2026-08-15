//! material — 写作素材收集与整理 CLI(CODE 循环)。
//!
//! 用法:
//!   material collect "想法"                     # C-Capture:记录到今日日志
//!   material collect --url <链接> [--title 标题]  # C-Capture:从链接获得内容
//!   material organize                           # O-Organize:LLM 提取主题 → 更新日志 YAML 归属
//!   material distill <主题> [--refine]           # D-Distill:聚合条目;--refine 删除次要信息
//!   material express <主题> [--goal 写作目标]      # E-Express:素材 → 成稿(默认自动判断意图)

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
    /// C-Capture:把想法记录到今日日志(文本或 --url 链接)
    Collect {
        /// 想法文本(与 --url 二选一)
        text: Option<String>,
        /// 从链接获得内容作为条目
        #[arg(long)]
        url: Option<String>,
        /// 条目标题(默认:URL 文件名 / 当前时间)
        #[arg(long)]
        title: Option<String>,
    },
    /// O-Organize:LLM 从日志提取主题,更新日志 YAML 归属(分组,保留人工标注)
    Organize,
    /// D-Distill:过滤次要信息并统一表达 → 初稿 materials/<主题>.md
    Distill { topic: String },
    /// E-Express:根据写作目标形成定稿 → <主题>-定稿.md(缺省自动判断意图)
    Express {
        topic: String,
        /// 写作目标(如"写一篇品牌故事");缺省自动根据内容判断
        #[arg(long)]
        goal: Option<String>,
    },
}

fn run(cli: Cli) -> Result<(), String> {
    let workdir = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    match cli.command {
        Commands::Collect { text, url, title } => match (text, url) {
            (Some(text), None) => {
                let path = narrative_engineering::journal::collect(&workdir, &text)?;
                println!("已记录:{}", path.display());
                Ok(())
            }
            (None, Some(url)) => {
                let (path, title) =
                    narrative_engineering::journal::collect_from_url(&workdir, &url, title.as_deref())?;
                println!("已从链接获得并记录:{} (条目: {})", path.display(), title);
                Ok(())
            }
            _ => Err("collect 需要提供想法文本,或 --url 链接(二选一)".into()),
        },
        Commands::Organize => {
            let updated = narrative_engineering::organize::organize(&workdir)?;
            let groups = narrative_engineering::organize::write_groups(&workdir)?;
            println!("已更新 {} 条条目归属(建议,可编辑日志 YAML 修正)", updated);
            println!("已生成 {} 个分组:", groups.len());
            for g in &groups {
                println!("  {}", g.display());
            }
            Ok(())
        }
        Commands::Distill { topic } => {
            let path = narrative_engineering::distill::distill(&workdir, &topic)?;
            println!("已组织:{}", path.display());
            Ok(())
        }
        Commands::Express { topic, goal } => {
            let path = narrative_engineering::express::express(&workdir, &topic, goal.as_deref())?;
            println!("已生成:{}", path.display());
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
