#ifndef PURCHASERECORD_H
#define PURCHASERECORD_H

// 文件用途: 定义进货记录结构体, 追踪进货产品ID/数量/时间
// 主要知识点: 动态内存分配, 单向链表结构, 文件读写格式

// 进货记录结构体
// 新增注释：
// 1. 用于存储每次进货时的产品 ID、进货数量以及日期等数据。
// 2. 同样采用链表方式（struct PurchaseRecord* next）来管理所有进货信息。
// 3. 在进货模块函数中使用动态内存分配来创建记录节点。
typedef struct PurchaseRecord {
    int productId;
    int quantity;
    char date[100];
    struct PurchaseRecord* next;
} PurchaseRecord;

void PurchaseModule_doPurchase(PurchaseRecord** purchases, Product* products, int productId, int quantity, const char* date);

#endif // PURCHASERECORD_H