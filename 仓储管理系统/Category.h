// 文件用途: 定义产品类别列表
// 主要知识点: 结构体链接, 定长字符数组, typedef的使用

// 新增注释：
// 1. Category 结构体使用 next 指针，将多个类别串成单向链表，方便在添加或删除类别时只需操作指针。
// 2. 使用 typedef struct Category { ... } Category; 简化后续对 Category 类型的使用。
// 3. MAX_CATEGORY_LEN 定义了类别名称的最大长度，为数组编译时分配固定大小。

#ifndef CATEGORY_H
#define CATEGORY_H

#define MAX_CATEGORY_LEN 100

typedef struct Category {
    char categoryName[MAX_CATEGORY_LEN];
    struct Category* next;
} Category;

// 保持结构定义不变，仅在仓储管理系统.cpp中以统一命名方式调用

#endif // CATEGORY_H