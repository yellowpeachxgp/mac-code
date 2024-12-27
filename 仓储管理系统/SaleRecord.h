#ifndef SALERECORD_H
#define SALERECORD_H

// 文件用途: 定义销售记录结构体, 记录单次销售相关信息
// 主要知识点: 结构体链表, 指针操作, 基本IO操作

// 销售记录结构体
// 新增注释：
// 1. 用于记录每次销售时的产品 ID、数量和日期等信息。
// 2. 通过 struct SaleRecord* next 将所有销售记录形成单向链表，便于遍历和处理。
// 3. 在销售模块函数中会使用动态内存分配创建 SaleRecord，表现了 C++ 中对堆内存的使用。
typedef struct SaleRecord {
    int productId;
    int quantity;
    char date[100];
    float revenue;  // 新增：销售额
    float profit;   // 新增：利润额
    float margin;   // 新增：利润率(百分比)
    struct SaleRecord* next;
} SaleRecord;

void SaleModule_doSale(SaleRecord** sales, Product* products, int productId, int quantity, const char* date);

#endif // SALERECORD_H