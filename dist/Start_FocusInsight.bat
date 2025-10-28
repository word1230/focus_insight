@echo off
echo Starting Focus-Insight...
echo.
echo 1. Monitor - 启动监控程序 (记录应用使用情况)
echo 2. Report - 查看报告 (可视化分析)
echo.
set /p choice="请选择功能 (1/2): "

if "%choice%"=="1" (
    start "" "%~dp0FocusInsight-Monitor\FocusInsight-Monitor.exe"
) else if "%choice%"=="2" (
    start "" "%~dp0FocusInsight-Report\FocusInsight-Report.exe"
) else (
    echo 无效选择
    pause
)