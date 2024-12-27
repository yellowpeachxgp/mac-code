#ifndef PURCHASERECORD_H
#define PURCHASERECORD_H

// 文件用途: 定义进货记录结构体, 追踪进货产品ID/数量/时间
// 主要知识点: 动态内存分配, 单向链表结构, 文件读写格式

// 进货记录结构体
typedef struct PurchaseRecord {
    int productId;
    int quantity;
    char date[100];
    struct PurchaseRecord* next;
} PurchaseRecord;

#endif // PURCHASERECORD_H