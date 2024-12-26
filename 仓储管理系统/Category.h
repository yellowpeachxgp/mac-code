#ifndef CATEGORY_H
#define CATEGORY_H

#define MAX_CATEGORY_LEN 100

typedef struct Category {
    char categoryName[MAX_CATEGORY_LEN];
    struct Category* next;
} Category;

#endif // CATEGORY_H