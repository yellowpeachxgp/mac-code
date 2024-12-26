#ifndef SALERECORD_H
#define SALERECORD_H

// 销售记录结构体
typedef struct SaleRecord {
    int productId;
    int quantity;
    char date[100];
    float revenue;  // 新增：销售额
    float profit;   // 新增：利润额
    float margin;   // 新增：利润率(百分比)
    struct SaleRecord* next;
} SaleRecord;

#endif // SALERECORD_H