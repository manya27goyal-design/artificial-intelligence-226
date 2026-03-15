graph = {
    "Delhi": {"Jaipur": 281, "Agra": 233, "Chandigarh": 244},
    "Jaipur": {"Delhi": 281, "Ahmedabad": 657, "Udaipur": 394},
    "Agra": {"Delhi": 233, "Lucknow": 335, "Gwalior": 121},
    "Lucknow": {"Agra": 335, "Varanasi": 320},
    "Ahmedabad": {"Jaipur": 657, "Mumbai": 524},
    "Mumbai": {"Ahmedabad": 524, "Pune": 148},
    "Pune": {"Mumbai": 148, "Hyderabad": 560},
    "Hyderabad": {"Pune": 560, "Bangalore": 570},
    "Bangalore": {"Hyderabad": 570, "Chennai": 346},
    "Chennai": {"Bangalore": 346},
    "Chandigarh": {"Delhi": 244},
    "Udaipur": {"Jaipur": 394},
    "Gwalior": {"Agra": 121},
    "Varanasi": {"Lucknow": 320}
}
def dijkstra(graph, start):
    dist = {city: float('inf') for city in graph}
    visited = set()
    dist[start] = 0
    while len(visited) < len(graph):
        currcity = None
        mindis = float('inf')
        for city in graph:
            if city not in visited and dist[city] < mindis:
                mindis = dist[city]
                currcity = city
        visited.add(currcity)
        for neighbor, weight in graph[currcity].items():
            newdis = dist[currcity] + weight
            if newdis < dist[neighbor]:
                dist[neighbor] = newdis
    return dist

print("Shortest distances from Pune:")
print(dijkstra(graph, "Pune"))
