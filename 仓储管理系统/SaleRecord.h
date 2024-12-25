
#ifndef SALERECORD_H
#define SALERECORD_H

#define MAX_NAME_LEN 100

typedef struct SaleRecord {
    int productId;                // 产品ID
    int quantity;                 // 销售数量
    char date[MAX_NAME_LEN];      // 销售日期
    struct SaleRecord* next;      // 链表的下一个销售记录
} SaleRecord;

#endif // SALERECORD_H