import decimal

# Set decimal precision
# WARNING: Keep in mind this also affects the precision of very large numbers
decimal.getcontext().prec = 10
