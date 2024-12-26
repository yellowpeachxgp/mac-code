#ifndef PRODUCT_H
#define PRODUCT_H

#define MAX_NAME_LEN 100

typedef struct Product {
    int id;
    char name[MAX_NAME_LEN];
    char category[MAX_NAME_LEN];
    int stock;
    int sales;
    float purchasePrice;  // 新增：进货价
    float salePrice;      // 新增：销售价
    // 新增字段
    float totalPurchaseCost; 
    float totalSaleCost;
    float profitMargin;
    struct Product* next;
} Product;

#endif // PRODUCT_H