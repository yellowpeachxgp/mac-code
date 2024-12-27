// 文件用途: 定义产品类别列表
// 主要知识点: 结构体链接, 定长字符数组, typedef的使用

#ifndef CATEGORY_H
#define CATEGORY_H

#define MAX_CATEGORY_LEN 100

typedef struct Category {
    char categoryName[MAX_CATEGORY_LEN];
    struct Category* next;
} Category;

#endif // CATEGORY_H