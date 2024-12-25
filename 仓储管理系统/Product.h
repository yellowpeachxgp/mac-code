
#ifndef PRODUCT_H
#define PRODUCT_H

#define MAX_NAME_LEN 100

typedef struct Product {
    int id;                     // 产品ID
    char name[MAX_NAME_LEN];    // 产品名称
    char category[MAX_NAME_LEN];// 产品类别
    int stock;                  // 当前库存
    int sales;                  // 销售数量
    struct Product* next;       // 链表的下一个产品
} Product;

#endif // PRODUCT_H