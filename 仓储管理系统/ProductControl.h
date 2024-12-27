#ifndef PRODUCTCONTROL_H
#define PRODUCTCONTROL_H

// 文件用途: 声明对产品增删改查等控制函数
// 主要知识点: 函数原型, 封装, 链表增删操作

// 新增注释：
// 1. 此头文件声明了对产品增删改查等操作的原型，方便在实现文件中完成逻辑。
// 2. 使用了指针参数 (Product**) 操作链表头部，实现增删产品的灵活性。
// 3. 通过函数拆分，将产品的各类操作聚合到同一个模块中。

void updateProductCost(Product* product, int quantity, float purchasePrice);

void ProductModule_addProduct(Product** products, int id, const char* name, const char* category, int stock, float pPrice, float sPrice);
void ProductModule_deleteProduct(Product** products, int id);
void ProductModule_modifyProduct(Product* products, int id);
void ProductModule_displayAll(Product* products);

void ReportModule_sortBySales(Product* products);
void QueryModule_product(Product* products, int id);
void QueryModule_sales(Product* products, SaleRecord* sales, int id);
void QueryModule_byCategory(Product* products, const char* category);

#endif // PRODUCTCONTROL_H
