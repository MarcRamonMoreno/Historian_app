import multiprocessing

# Worker configuration - reduce number of workers
workers = multiprocessing.cpu_count() * 2  # Reduced from +1
threads = 4  # Increased from 2
worker_class = 'gthread'
worker_connections = 1000
worker_health_check_interval = 30

# Increase timeouts for long-running processes
timeout = 300
graceful_timeout = 120
keepalive = 5

# Binding
bind = "0.0.0.0:5000"

# Performance tuning
max_requests = 1000
max_requests_jitter = 50
backlog = 2048

# Logging
loglevel = 'info'
accesslog = '-'
errorlog = '-'

# Process naming
proc_name = 'historian_processor'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None

preload_app = True  # Add this to preload the application