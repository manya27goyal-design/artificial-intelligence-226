#include <stdio.h>
#define MAX 100

int adj[MAX][MAX];
int visited[MAX];
int n;

void dfs(int start) {
    int i;
    visited[start] = 1;
    printf("%d ", start);

    for (i = 0; i < n; i++) {
        if (adj[start][i] == 1 && visited[i] == 0)
            dfs(i);
    }
}

int main() {
    int i, j, start;
    scanf("%d", &n);

    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            scanf("%d", &adj[i][j]);

    scanf("%d", &start);

    for (i = 0; i < n; i++)
        visited[i] = 0;

    dfs(start);

    return 0;
}
