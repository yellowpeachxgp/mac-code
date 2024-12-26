#ifndef PURCHASERECORD_H
#define PURCHASERECORD_H

// 进货记录结构体
typedef struct PurchaseRecord {
    int productId;
    int quantity;
    char date[100];
    struct PurchaseRecord* next;
} PurchaseRecord;

#endif // PURCHASERECORD_H