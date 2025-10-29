Param(
  [switch]$Release
)

Write-Host "启动构建..."
if ($Release) {
  python build/build.py --release
} else {
  python build/build.py
}
Write-Host "构建结束。"