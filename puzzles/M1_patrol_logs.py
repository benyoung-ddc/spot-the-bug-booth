# Each patrol should start with its own empty log.
# Should print:
#   ['Cambridge Bay']
#   ['Inuvik']
def log_stop(stop, log=[]):
    log.append(stop)
    return log

print(log_stop("Cambridge Bay"))
print(log_stop("Inuvik"))
