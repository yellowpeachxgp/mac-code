#ifndef SALERECORD_H
#define SALERECORD_H

// 文件用途: 定义销售记录结构体, 记录单次销售相关信息
// 主要知识点: 结构体链表, 指针操作, 基本IO操作

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