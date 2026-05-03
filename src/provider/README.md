# qtcloud-write-provider

写作云后端 API 服务，提供文章叙事结构分析和风格对比能力。

## 启动

```bash
uv run uvicorn app.main:app --reload
```

## 开发

```bash
uv run pytest -v
```

## API

- `POST /review` — 提交文章，返回叙事结构分析和风格对比结果
