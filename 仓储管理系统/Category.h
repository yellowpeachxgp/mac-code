
#ifndef CATEGORY_H
#define CATEGORY_H

#define MAX_NAME_LEN 100

typedef struct Category {
    char name[MAX_NAME_LEN];  // 类别名称
    struct Product* productList; // 该类别下的产品列表
    struct Category* next;    // 链表的下一个类别
} Category;

#endif // CATEGORY_H