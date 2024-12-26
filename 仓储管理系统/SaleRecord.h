#ifndef SALERECORD_H
#define SALERECORD_H

// 销售记录结构体
typedef struct SaleRecord {
    int productId;
    int quantity;
    char date[100];
    struct SaleRecord* next;
} SaleRecord;

#endif // SALERECORD_H