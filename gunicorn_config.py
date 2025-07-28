import multiprocessing
import os

# Server socket - Use port from environment variable or default to 10000
bind = '0.0.0.0:' + str(int(os.environ.get('PORT', 10000)))

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gthread'
threads = 2

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'info'

# Timeout
keepalive = 5
timeout = 120

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
