module.exports = {
  apps: [{
    name: "commit-backend",
    script: "/root/commit-backend/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8100",
    interpreter: "none"
  }]
}