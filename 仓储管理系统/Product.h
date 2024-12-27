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
    int historicalStock; // 新增：用于记录历史总库存
    struct Product* next;
} Product;

// 新增注释：
// 1. 这里定义了 Product 结构体，记录产品的 ID、名称、类别、库存量等信息。
// 2. struct Product* next 用于将产品以单向链表的形式相连，方便添加、删除与遍历。
// 3. totalPurchaseCost、totalSaleCost 等字段用于财务计算，historicalStock 用于记录历史累计库存量。
// 4. 通过 float purchasePrice、float salePrice 实现对单价的存储，可以结合数量计算各项成本和利润。

// 建议保持 Product 结构及其字段不变，仅在函数中引用时使用 "products"

#endif // PRODUCT_H