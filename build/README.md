# 构建系统说明

本目录包含项目的自动化构建脚本与相关资源。

- `build.py`：主构建脚本（解析文档、提取团队配置、质量检查、打包发布、生成报告）
- 使用方法：`python build/build.py --release`
- 输出产物：`dist/` 下的发布包与 `BUILD_REPORT.md`

后续步骤：
1. 安装依赖：`pip install -r requirements.txt`
2. 运行构建：`python build/build.py --release`
3. 查看报告：`BUILD_REPORT.md`