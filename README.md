# AI Short Drama Factory (MVP-0)

可部署的短剧生成流水线：上传剧本 → 规则拆集 → 全剧公共资产 → 分镜 → Mock 视频 → FFmpeg 合成。MVP-0 默认使用 Mock Provider，不产生付费 API 调用。

## 架构

FastAPI + SQLAlchemy/PostgreSQL + Redis/Celery + local/S3-ready storage + React/Vite + FFmpeg。`app/services/pipeline.py` 编排阶段，Provider 与 SkillLoader 分离。

## 本地启动

```powershell
Copy-Item .env.example .env
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

打开 http://localhost:8000/docs；前端开发服务器为 http://localhost:5173。也可以直接使用 API：创建项目、上传 `.txt/.md/.docx`，然后调用 `/api/projects/{id}/start`。

## Mock 模式

`.env` 中保持 `LLM_PROVIDER=mock`, `IMAGE_PROVIDER=mock`, `VIDEO_PROVIDER=mock`。Mock Video Provider 用 FFmpeg 生成带 Shot 编号的竖屏 MP4，再拼接为 `storage/projects/{project_id}/episodes/EP01/EP01_final.mp4`。

## Docker

```bash
cp .env.example .env
docker compose up -d --build
```

API: http://localhost:8000，Swagger: http://localhost:8000/docs，前端: http://localhost:5173。当前环境若没有 Docker daemon，标记为 NOT VERIFIED。生产环境将 `DATABASE_URL`、`STORAGE_ROOT`、Redis 指向容器服务，并运行 `alembic upgrade head`。

## Skill

代码只读取 `third_party/manju-laoli-skill/short-drama-director`。本离线工作区无法从 GitHub 拉取原仓库时提供了兼容的最小 Skill 包；网络恢复后执行：

```bash
git submodule add https://github.com/lixiaoxiao9888-create/manju-laoli-skill.git third_party/manju-laoli-skill
git submodule update --remote --merge
```

SkillLoader 按阶段加载并记录文件列表、字符数和 prompt hash，不会每次加载全部 reference。

## 测试与命令

`pytest -q`, `ruff check app tests`, `make up`, `make down`, `make logs`, `make test`, `make lint`, `make skill-check`。

真实 LLM/图片/视频 Provider 的配置字段已预留，`ENABLE_PAID_GENERATION=false` 是安全默认值。Seedance、MiniMax Provider 接口可在下一阶段加入，业务层只使用 CanonicalVideoRequest。
