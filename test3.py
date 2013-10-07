latency = {}

def func():
    members = ['node1', 'node2']
    for node in members:
        if node not in latency:
            latency[node] = 5.0
        else:
            latency[node] = 0.9*latency[node] + 0.1*4

print latency
func()
print latency
func()
print latency
