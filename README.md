# DataFlow
A visual drag-and-drop data pipeline platform with distributed computing, real-time monitoring, and enterprise-grade scalability.

## Worker management
From [worker/](worker/), use the CLI to manage the Python worker process:

- `python cli.py start`
- `python cli.py stop`
- `python cli.py restart`
- `python cli.py status`
- `python cli.py pid`
- `python cli.py logs`
- `python cli.py logs -f`

The worker writes its PID to `worker.pid` and logs to `worker.log` in the same directory.
