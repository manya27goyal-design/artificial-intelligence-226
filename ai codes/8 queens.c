#include <stdio.h>
#include <stdlib.h>
#define N 8

int board[N];

int safe(int row, int col) {
    for (int i = 0; i < row; i++)
        if (board[i] == col || abs(board[i] - col) == row - i)
            return 0;
    return 1;
}

int solve(int row) {
    if (row == N)
        return 1;
    for (int col = 0; col < N; col++) {
        if (safe(row, col)) {
            board[row] = col;
            if (solve(row + 1))
                return 1;
        }
    }
    return 0;
}

int main() {
    if (solve(0)) {
        for (int i = 0; i < N; i++)
            printf("%d ", board[i]);
    }
    return 0;
}
