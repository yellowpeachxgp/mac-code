#ifndef PRODUCT_H
#define PRODUCT_H

#define MAX_NAME_LEN 100

typedef struct Product {
    int id;
    char name[MAX_NAME_LEN];
    char category[MAX_NAME_LEN];
    int stock;
    int sales;
    struct Product* next;
} Product;

#endif // PRODUCT_H