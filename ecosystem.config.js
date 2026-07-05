module.exports = {
  apps: [
    {
      name: "openclaw-bot",
      script: "bot.py",
      interpreter: "python3",
      cwd: __dirname,
      watch: false,
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 50,
      min_uptime: "10s",
      exp_backoff_restart_delay: 100,
      env: {
        NODE_ENV: "production",
      },
      error_file: "logs/pm2-error.log",
      out_file: "logs/pm2-out.log",
      merge_logs: true,
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
    },
  ],
};
