#include <stdio.h>

int visited[5][4];

void bfs() {
    int queue[100][2], front = 0, rear = 0;
    queue[rear][0] = 0;
    queue[rear][1] = 0;
    rear++;
    visited[0][0] = 1;

    while (front < rear) {
        int x = queue[front][0];
        int y = queue[front][1];
        front++;

        printf("(%d,%d)\n", x, y);

        if (x == 2 || y == 2)
            return;

        int next[6][2] = {
            {4, y},
            {x, 3},
            {0, y},
            {x, 0},
            {x - (3 - y > x ? x : 3 - y), y + (3 - y > x ? x : 3 - y)},
            {x + (4 - x > y ? y : 4 - x), y - (4 - x > y ? y : 4 - x)}
        };

        for (int i = 0; i < 6; i++) {
            int nx = next[i][0];
            int ny = next[i][1];
            if (!visited[nx][ny]) {
                visited[nx][ny] = 1;
                queue[rear][0] = nx;
                queue[rear][1] = ny;
                rear++;
            }
        }
    }
}

int main() {
    bfs();
    return 0;
}
