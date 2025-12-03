"""Generate command for benchmarking 100 to 500000 with 100 steps"""

start = 100
end = 500000
steps = 100

# Generate evenly spaced sizes
step_size = (end - start) / (steps - 1)
sizes = [int(start + i * step_size) for i in range(steps)]
# Ensure last value is exactly end
sizes[-1] = end

# Create command
sizes_str = ' '.join(map(str, sizes))
command = f"python run_overnight.py {sizes_str}"

print(command)
print(f"\n# Total steps: {len(sizes)}")
print(f"# Range: {min(sizes)} to {max(sizes)}")



