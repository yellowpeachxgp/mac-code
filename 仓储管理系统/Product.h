// 文件用途: 定义产品信息(名称/类别/价格/库存等)
// 主要知识点: 指针, 动态内存, 基本字符串函数

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