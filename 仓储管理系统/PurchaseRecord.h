
#ifndef PURCHASERECORD_H
#define PURCHASERECORD_H

#define MAX_NAME_LEN 100

typedef struct PurchaseRecord {
    int productId;                // 产品ID
    int quantity;                 // 进货数量
    char date[MAX_NAME_LEN];      // 进货日期
    struct PurchaseRecord* next;  // 链表的下一个进货记录
} PurchaseRecord;

#endif // PURCHASERECORD_H