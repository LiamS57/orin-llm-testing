import statlog

# run a 15 second log and print the log entries
log = statlog.run_blocking(15)
log.print()