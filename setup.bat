@echo off
REM ============================================================
REM  OpenClaw Bot - One-Click FREE Setup (Windows)
REM  Double-click this file. It will:
REM    1. Ask for your GitHub Models token (free AI) + Telegram token
REM    2. Save them as PERMANENT Windows environment variables
REM    3. Download / update the bot, install dependencies
REM    4. Start the bot locally
REM
REM  NOTE: Your bot also runs 24/7 for free on GitHub Actions.
REM        This script is for running it on THIS PC as well.
REM ============================================================

setlocal enabledelayedexpansion
title OpenClaw Bot Setup
color 0A

echo(
echo  ============================================
echo    OpenClaw Bot - FREE Setup (GitHub Models)
echo  ============================================
echo(

REM ---- 1. GitHub Models token (free AI, no credit card) ----
echo  Get a token at: https://github.com/settings/tokens
echo  (Fine-grained token, permission: Account -^> Models -^> Read)
echo(
set /p GH_MODELS_TOKEN=  Paste your GitHub Models token (ghp_...): 
if "!GH_MODELS_TOKEN!"=="" (
  echo  [ERROR] No token entered. Exiting.
  pause
  exit /b 1
)

REM ---- 2. Telegram bot token (from @BotFather) ----
echo(
set /p TG_TOKEN=  Paste your Telegram bot token (or press Enter to skip): 

echo(
echo  Saving permanent environment variables...
setx GH_MODELS_API_KEY "!GH_MODELS_TOKEN!" >nul
if not "!TG_TOKEN!"=="" setx TELEGRAM_BOT_TOKEN "!TG_TOKEN!" >nul
echo  Done. (Open a NEW terminal for them to take effect.)

REM ---- 3. Download / update the bot ----
echo(
set "BOTDIR=%USERPROFILE%\openclaw-bot"
where git >nul 2>nul
if errorlevel 1 (
  echo  [WARN] git is not installed - skipping download/update.
  echo         Install Git from https://git-scm.com/download/win and re-run.
) else (
  if exist "%BOTDIR%\.git" (
    echo  Updating existing bot in %BOTDIR% ...
    git -C "%BOTDIR%" pull
  ) else (
    echo  Downloading bot to %BOTDIR% ...
    git clone https://github.com/gautamrose96-bit/openclaw-bot.git "%BOTDIR%"
  )
)

REM ---- 4. Install dependencies + run ----
where python >nul 2>nul
if errorlevel 1 (
  echo  [WARN] Python not found. Install Python 3.11+ from https://python.org
  echo         then double-click this file again.
  pause
  exit /b 1
)

if exist "%BOTDIR%\requirements.txt" (
  echo(
  echo  Installing dependencies...
  python -m pip install --upgrade pip >nul
  python -m pip install -r "%BOTDIR%\requirements.txt"

  echo(
  echo  ============================================
  echo    Setup complete! Starting OpenClaw Bot...
  echo    (Close this window to stop the bot.)
  echo  ============================================
  echo(
  set "GH_MODELS_API_KEY=!GH_MODELS_TOKEN!"
  if not "!TG_TOKEN!"=="" set "TELEGRAM_BOT_TOKEN=!TG_TOKEN!"
  cd /d "%BOTDIR%"
  python bot.py
) else (
  echo  [WARN] Could not find the bot files. Re-run after installing Git.
)

echo(
pause
endlocal
