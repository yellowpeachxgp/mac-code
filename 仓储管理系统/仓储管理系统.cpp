#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "User.h"        // 添加此行以包含 User 结构体定义
#include "Product.h"     // 新增：包含 Product 结构体定义
#include "PurchaseRecord.h" // 新增：包含 PurchaseRecord 结构体定义
#include "SaleRecord.h"  // 新增：包含 SaleRecord 结构体定义
#include "Category.h"    // 新增：包含 Category 结构体定义

#define MAX_NAME_LEN 100
#define MAX_PASS_LEN 20

// 枚举类型定义
enum Section {
    NONE,
    PRODUCTS,
    USERS,
    PURCHASES,
    SALES
};

// 函数声明
User* login(User* users); // 修改登录函数的返回类型
void ProductModule_add(Product** products, int id, const char* name, const char* category, int stock, float purchasePrice, float salePrice); // 修改函数声明
void ProductModule_delete(Product** products, int id);
void ProductModule_modify(Product* products, int id);
void ProductModule_query(Product* products, int id);
void ProductModule_querySales(Product* products, SaleRecord* sales, int id);
void ProductModule_queryByCategory(Product* products, const char* category); // 新增函数声明
void PurchaseModule_doPurchase(PurchaseRecord** purchases, Product* products, int productId, int quantity, const char* date);
void SaleModule_doSale(SaleRecord** sales, Product* products, int productId, int quantity, const char* date);
void loadFromFile(Product** products, User** users, PurchaseRecord** purchases, SaleRecord** sales);
void saveToFile(Product* products, User* users, PurchaseRecord* purchases, SaleRecord* sales);
void showAdminMenu();
void showStaffMenu();
void adminOperations(Product** products, User* users, PurchaseRecord** purchases, SaleRecord** sales, User* currentUser); // 扩展 adminOperations 函数签名
void staffOperations(Product* products, SaleRecord* sales);
void ProductModule_sortAndDisplayBySales(Product* products); // 新增函数声明
void ProductModule_displayAll(Product* products); // 添加此行
void updateProductCost(Product* product, int quantity, float purchasePrice); // 新增函数声明

// 新增注释：
// ========== 总体说明 ==========
// 1. 本文件为主程序入口及模块功能的集中实现，包含对产品、用户、进货、销售等模块的操作函数。
// 2. 通过 include 对多个头文件进行引用，实现信息的跨文件共享。
// 3. 灵活运用枚举类型 (enum Section) 区分不同数据块，指针用于用户链表、产品链表、进货记录链表、销售记录链表等动态结构。
// 4. 使用了 scanf、fscanf 等 C 语言风格的输入/输出函数，通过字符串处理函数 strncmp、strcmp 等进行对比。
// =============================

// 登录功能
User* login(User* users) { // 修改登录函数的返回类型
    // 知识点: 使用scanf读取字符数组, 进行字符串比较strcmp判断账号密码
    char username[MAX_NAME_LEN] = { 0 }, password[MAX_PASS_LEN] = { 0 };
    printf("请输入账户名: ");
    if (scanf("%99s", username) != 1) { // 修改此行
        printf("用户名输入失败!\n");
        return NULL; // 失败返回 NULL
    }

    printf("请输入密码: ");
    if (scanf("%19s", password) != 1) { // 修改此行
        printf("密码输入失败!\n");
        return NULL; // 失败返回 NULL
    }

    User* current = users;
    while (current != NULL) {
        if (strcmp(current->username, username) == 0 && strcmp(current->password, password) == 0) {
            printf("登录成功!\n");
            displayUserInfo(current);  // 新增：登录成功后立即显示用户信息
            return current; // 登录成功时，改为返回当前用户指针
        }
        current = current->next;
    }

    printf("用户名或密码错误!\n");
    return NULL; // 失败返回 NULL
}

// 在 login 函数处新增注释：
// 1. 该函数使用 User* 遍历用户链表，通过 strcmp 比较账号和密码来验证登录。
// 2. 与空间分配配合，可在系统讨论管理不同用户的权限，如管理员、普通员工等角色。
// 3. 若匹配失败则返回 NULL，匹配成功后返回指向对应用户的指针。

// 增加产品
void ProductModule_add(Product** products, int id, const char* name, const char* category, int stock, float purchasePrice, float salePrice) { // 修改函数签名
    // 知识点: 使用while遍历链表, 动态分配内存后插入头部, 检查ID并防止重复
    Product* newProduct = (Product*)malloc(sizeof(Product));
    if (newProduct == NULL) {
        printf("内存分配失败!\n");
        return;
    }

    // 在创建新产品前，先检查ID是否已存在
    Product* existing = *products;
    while (existing != NULL) {
        if (existing->id == id) {
            printf("ID %d 已存在，无法添加产品!\n", id);
            free(newProduct);
            return;
        }
        existing = existing->next;
    }

    newProduct->id = id;
    strncpy(newProduct->name, name, MAX_NAME_LEN - 1);
    newProduct->name[MAX_NAME_LEN - 1] = '\0';
    strncpy(newProduct->category, category, MAX_NAME_LEN - 1);
    newProduct->category[MAX_NAME_LEN - 1] = '\0';
    newProduct->stock = stock;
    newProduct->sales = 0;
    newProduct->purchasePrice = purchasePrice; // 新增
    newProduct->salePrice = salePrice; // 新增
    newProduct->totalPurchaseCost = 0.0f; // 新增
    newProduct->totalSaleCost = 0.0f; // 新增
    newProduct->profitMargin = 0.0f; // 新增
    newProduct->historicalStock = 0; // 新增
    newProduct->next = *products;
    *products = newProduct;

    printf("产品'%s'添加成功!\n", name);
}

// 在 ProductModule_add 函数处新增注释：
// 1. 该函数通过 malloc 动态分配 Product 结构体，利用指针操作实现以链表形式添加新产品。
// 2. 先检查 ID 是否已存在，再插入头部，以确保数据安全并保持插入顺序可控。
// 3. 同时初始化了一些统计字段，如 totalPurchaseCost、totalSaleCost、historicalStock 等，用于后续各种财务运算。

// 删除产品
void ProductModule_delete(Product** products, int id) {
    Product* current = *products;
    Product* previous = NULL;

    while (current != NULL) {
        if (current->id == id) {
            if (previous == NULL) {
                *products = current->next;
            }
            else {
                previous->next = current->next;
            }
            free(current);
            printf("产品ID %d 删除成功!\n", id);
            return;
        }
        previous = current;
        current = current->next;
    }

    printf("未找到产品ID为 %d 的产品!\n", id);
}

// 在 ProductModule_delete 函数处新增注释：
// 1. 同样使用指针遍历链表并找到待删节点后，通过修改指针来解除该节点的链接，再释放其内存。
// 2. 这体现了链表在 C++ 中对指针操作的灵活性及手动内存管理需求。

// 修改产品
void ProductModule_modify(Product* products, int id) {
    // 知识点: switch-case控制流程, scanf输入处理, 遍历检查新ID防止重复
    Product* current = products;

    while (current != NULL) {
        if (current->id == id) {
            int choice;
            do {
                printf("请选择要修改的属性:\n");
                printf("1. 产品ID\n");
                printf("2. 产品名称\n");
                printf("3. 产品类别\n");
                printf("4. 库存数量\n");
                printf("0. 完成修改\n");
                printf("请输入选项: ");
                if (scanf("%d", &choice) != 1) {
                    printf("输入错误!\n");
                    // 清空输入缓冲区
                    int ch;
                    while ((ch = getchar()) != '\n' && ch != EOF);
                    choice = -1; // 设置为无效选项
                    continue;
                }

                switch (choice) {
                case 1: {
                    int newId;
                    printf("请输入新产品ID: ");
                    if (scanf("%d", &newId) != 1) { // 修改此行
                        printf("输入错误!\n");
                        // 清空输入缓冲区
                        int ch;
                        while ((ch = getchar()) != '\n' && ch != EOF);
                        break;
                    }
                    // 检查新的ID是否已被占用
                    Product* temp = products;
                    while (temp != NULL) {
                        if (temp->id == newId && temp != current) {
                            printf("ID %d 已存在，无法修改!\n", newId);
                            // 清空输入缓冲区或直接返回，避免后续覆盖
                            int ch;
                            while ((ch = getchar()) != '\n' && ch != EOF);
                            break;
                        }
                        temp = temp->next;
                    }
                    current->id = newId;
                    printf("产品ID修改成功!\n");
                    break;
                }
                case 2: {
                    char newName[MAX_NAME_LEN] = { 0 };
                    printf("请输入新产品名称: ");
                    if (scanf("%99s", newName) != 1) { // 修改此行
                        printf("输入错误!\n");
                        break;
                    }
                    strncpy(current->name, newName, MAX_NAME_LEN - 1);
                    current->name[MAX_NAME_LEN - 1] = '\0';
                    printf("产品名称修改成功!\n");
                    break;
                }
                case 3: {
                    char newCategory[MAX_NAME_LEN] = { 0 };
                    printf("请输入新产品类别: ");
                    if (scanf("%99s", newCategory) != 1) { // 修改此行
                        printf("输入错误!\n");
                        break;
                    }
                    strncpy(current->category, newCategory, MAX_NAME_LEN - 1);
                    current->category[MAX_NAME_LEN - 1] = '\0';
                    printf("产品类别修改成功!\n");
                    break;
                }
                case 4: {
                    int newStock;
                    printf("请输入新库存数量: ");
                    if (scanf("%d", &newStock) != 1) { // 修改此行
                        printf("输入错误!\n");
                        // 清空输入缓冲区
                        int ch;
                        while ((ch = getchar()) != '\n' && ch != EOF);
                        break;
                    }
                    current->stock = newStock;
                    printf("库存数量修改成功!\n");
                    break;
                }
                case 0:
                    printf("完成修改!\n");
                    break;
                default:
                    printf("无效选项，请重新输入!\n");
                }
            } while (choice != 0);

            return;
        }
        current = current->next;
    }

    printf("未找到产品ID为 %d 的产品!\n", id);
}

// 查询产品
void ProductModule_query(Product* products, int id) {
    // 知识点: 计算利润率/毛利润率/单次销售利润率等财务数据
    Product* current = products;
    while (current != NULL) {
        if (current->id == id) {
            float currentTotalCost = current->purchasePrice * current->stock;
            float totalRevenue = current->salePrice * current->sales;
            float usedCost = current->purchasePrice * current->sales;
            float totalProfitRate = (totalRevenue != 0.0f)
                ? ((totalRevenue - currentTotalCost) / totalRevenue) * 100.0f : 0.0f;
            float grossMarginRate = (totalRevenue != 0.0f)
                ? ((totalRevenue - usedCost) / totalRevenue) * 100.0f : 0.0f;
            float singleSaleRate = (current->salePrice != 0.0f)
                ? ((current->salePrice - current->purchasePrice) / current->salePrice) * 100.0f : 0.0f;
            float historicalCost = current->historicalStock * current->purchasePrice; // 新增

            printf("产品ID: %d\n", current->id);
            printf("产品名称: %s\n", current->name);
            printf("产品类别: %s\n", current->category);
            printf("库存数量: %d\n", current->stock);
            printf("已售数量: %d\n", current->sales);
            printf("进货总成本: %.2f\n", current->totalPurchaseCost);
            printf("销售总成本: %.2f\n", current->totalSaleCost);
            printf("利润率: %.2f%%\n", current->profitMargin);
            printf("现存总成本(进货价×当前库存): %.2f\n", currentTotalCost);
            printf("总利润率(含未售库存): %.2f%%\n", totalProfitRate);
            printf("毛利润率(仅已售部分): %.2f%%\n", grossMarginRate);
            printf("单次销售利润率(单品): %.2f%%\n", singleSaleRate);
            printf("历史总库存: %d\n", current->historicalStock); // 新增
            printf("历史总成本: %.2f\n", historicalCost); // 新增
            return;
        }
        current = current->next;
    }

    printf("未找到产品ID为%d的产品!\n", id);
}

// 查询产品销售情况
void ProductModule_querySales(Product* products, SaleRecord* sales, int id) {
    Product* currentProduct = products;
    while (currentProduct != NULL) {
        if (currentProduct->id == id) {
            int totalSales = 0;
            SaleRecord* currentSale = sales;
            while (currentSale != NULL) {
                if (currentSale->productId == id) {
                    totalSales += currentSale->quantity;
                }
                currentSale = currentSale->next;
            }

            printf("产品ID: %d\n", currentProduct->id);
            printf("产品名称: %s\n", currentProduct->name);
            printf("销售总量: %d\n", totalSales);
            return;
        }
        currentProduct = currentProduct->next;
    }

    printf("未找到产品ID为%d的产品!\n", id);
}

// 查询类别下所有产品
void ProductModule_queryByCategory(Product* products, const char* category) {
    Product* current = products;
    int found = 0;
    printf("类别 '%s' 下的所有产品:\n", category);
    printf("---------------------------\n");
    while (current != NULL) {
        if (strcmp(current->category, category) == 0) {
            float currentTotalCost = current->purchasePrice * current->stock;
            float totalRevenue = current->salePrice * current->sales;
            float usedCost = current->purchasePrice * current->sales;
            float totalProfitRate = (totalRevenue != 0.0f)
                ? ((totalRevenue - currentTotalCost) / totalRevenue) * 100.0f : 0.0f;
            float grossMarginRate = (totalRevenue != 0.0f)
                ? ((totalRevenue - usedCost) / totalRevenue) * 100.0f : 0.0f;
            float singleSaleRate = (current->salePrice != 0.0f)
                ? ((current->salePrice - current->purchasePrice) / current->salePrice) * 100.0f : 0.0f;
            float historicalCost = current->historicalStock * current->purchasePrice; // 新增

            printf("产品ID: %d\n", current->id);
            printf("产品名称: %s\n", current->name);
            printf("产品类别: %s\n", current->category);
            printf("库存数量: %d\n", current->stock);
            printf("已售数量: %d\n", current->sales);
            printf("进货总成本: %.2f\n", current->totalPurchaseCost);
            printf("销售总成本: %.2f\n", current->totalSaleCost);
            printf("利润率: %.2f%%\n", current->profitMargin);
            printf("现存总成本(进货价×当前库存): %.2f\n", currentTotalCost);
            printf("总利润率(含未售库存): %.2f%%\n", totalProfitRate);
            printf("毛利润率(仅已售部分): %.2f%%\n", grossMarginRate);
            printf("单次销售利润率(单品): %.2f%%\n", singleSaleRate);
            printf("历史总库存: %d\n", current->historicalStock); // 新增
            printf("历史总成本: %.2f\n", historicalCost); // 新增
            printf("---------------------------\n");
            found = 1;
        }
        current = current->next;
    }

    if (!found) {
        printf("未找到类别 '%s' 下的产品!\n", category);
    }
}

// 按销售量排序并输出产品
void ProductModule_sortAndDisplayBySales(Product* products) {
    // 计算产品数量
    int count = 0;
    Product* current = products;
    while (current != NULL) {
        count++;
        current = current->next;
    }

    if (count == 0) {
        printf("没有产品可显示。\n");
        return;
    }

    // 创建数组存储产品指针
    Product** productArray = (Product**)malloc(count * sizeof(Product*));
    if (productArray == NULL) {
        printf("内存分配失败!\n");
        return;
    }

    // 填充数组
    current = products;
    for (int i = 0; i < count; i++) {
        productArray[i] = current;
        current = current->next;
    }

    // 简单的冒泡排序按销售量降序
    for (int i = 0; i < count - 1; i++) {
        for (int j = 0; j < count - i - 1; j++) {
            if (productArray[j]->sales < productArray[j + 1]->sales) {
                Product* temp = productArray[j];
                productArray[j] = productArray[j + 1];
                productArray[j + 1] = temp;
            }
        }
    }

    // 输出排序后的产品
    printf("按销售量排序的产品列表:\n");
    printf("---------------------------------------------------------------------------------\n");
    printf("| %-5s | %-20s | %-8s | %-8s | %-8s | %-10s | %-10s | %-8s | %-10s |\n",
           "ID", "名称", "库存", "销售", "进货价", "进货总成本", "销售总成本", "利润率", "单次销售率");
    printf("---------------------------------------------------------------------------------\n");
    for (int i = 0; i < count; i++) {
        Product* p = productArray[i];
        float singleSaleRate = (p->salePrice != 0.0f)
            ? ((p->salePrice - p->purchasePrice) / p->salePrice) * 100.0f : 0.0f;
        printf("| %-5d | %-20s | %-8d | %-8d | %-8.2f | %-10.2f | %-10.2f | %-7.2f%% | %-9.2f%% |\n",
               p->id, p->name, p->stock, p->sales, p->purchasePrice,
               p->totalPurchaseCost, p->totalSaleCost, p->profitMargin, singleSaleRate);
    }
    printf("--------------------------------------------------\n");

    free(productArray);
}

// 在 ProductModule_sortAndDisplayBySales 函数处新增注释：
// 1. 此处使用了冒泡排序 (Bubble Sort) 将产品按照销售量降序排列，用到了动态分配的指针数组 (Product** productArray)。
// 2. 展示了将链表中所有节点拷贝到数组进行排序的典型做法，也体现了在 C++ 中对内存分配和指针操作的综合应用。

// 实现 displayAllProducts 函数
void ProductModule_displayAll(Product* products) {
    // 知识点: 遍历链表, printf格式化输出产品详细信息
    Product* current = products;
    if (current == NULL) {
        printf("当前没有仓储物品信息。\n");
        return;
    }
    printf("========== 全部仓储物品信息 ==========\n");
    printf("| %-5s | %-20s | %-10s | %-8s | %-8s | %-10s | %-10s | %-8s | %-8s |\n",
           "ID", "名称", "类别", "库存", "销售", "进货总成本", "销售总成本", "利润率", "单次销售率");
    printf("---------------------------------------------------------------\n");
    while (current != NULL) {
        float singleSaleRate = (current->salePrice != 0.0f)
            ? ((current->salePrice - current->purchasePrice) / current->salePrice) * 100.0f : 0.0f;
        printf("| %-5d | %-20s | %-10s | %-8d | %-8d | %-10.2f | %-10.2f | %-7.2f%% | %-8.2f%% |\n",
               current->id,
               current->name,
               current->category,
               current->stock,
               current->sales,
               current->totalPurchaseCost,
               current->totalSaleCost,
               current->profitMargin,
               singleSaleRate);
        current = current->next;
    }
    printf("---------------------------------------------------------------\n");
}

// 进货管理
void PurchaseModule_doPurchase(PurchaseRecord** purchases, Product* products, int productId, int quantity, const char* date) {
    // 知识点: 进货操作影响产品库存, 动态链表插入购买记录
    PurchaseRecord* newPurchase = (PurchaseRecord*)malloc(sizeof(PurchaseRecord));
    if (newPurchase == NULL) {
        printf("内存分配失败!\n");
        return;
    }

    newPurchase->productId = productId;
    newPurchase->quantity = quantity;
    strncpy(newPurchase->date, date, MAX_NAME_LEN - 1);
    newPurchase->date[MAX_NAME_LEN - 1] = '\0';
    newPurchase->next = *purchases;
    *purchases = newPurchase;

    // 更新库存
    Product* currentProduct = products;
    while (currentProduct != NULL) {
        if (currentProduct->id == productId) {
            currentProduct->stock += quantity;
            currentProduct->totalPurchaseCost += currentProduct->purchasePrice * quantity; // 新增：累加进货总成本
            currentProduct->historicalStock += quantity; // 新增
            printf("进货成功，更新库存：%d\n", currentProduct->stock);
            return;
        }
        currentProduct = currentProduct->next;
    }

    printf("未找到产品ID为%d的产品!\n", productId);
}

// 销售管理
void SaleModule_doSale(SaleRecord** sales, Product* products, int productId, int quantity, const char* date) {
    // 知识点: 销售时更新库存/销量, 计算销售额/利润/利润率
    SaleRecord* newSale = (SaleRecord*)malloc(sizeof(SaleRecord));
    if (newSale == NULL) {
        printf("内存分配失败!\n");
        return;
    }

    newSale->productId = productId;
    newSale->quantity = quantity;
    strncpy(newSale->date, date, MAX_NAME_LEN - 1);
    newSale->date[MAX_NAME_LEN - 1] = '\0';
    newSale->next = *sales;
    *sales = newSale;

    // 更新库存
    Product* currentProduct = products;
    while (currentProduct != NULL) {
        if (currentProduct->id == productId) {
            if (currentProduct->stock >= quantity) {
                currentProduct->stock -= quantity;
                currentProduct->sales += quantity;
                currentProduct->totalSaleCost += currentProduct->salePrice * quantity; // 新增：累加总销售成本
                // 计算并记录销售额、利润额、利润率
                newSale->revenue = currentProduct->salePrice * quantity;
                newSale->profit = (currentProduct->salePrice - currentProduct->purchasePrice) * quantity;
                if (newSale->revenue != 0) {
                    newSale->margin = (newSale->profit / newSale->revenue) * 100.0f;
                } else {
                    newSale->margin = 0.0f;
                }
                // 重新计算利润率
                float totalProfit = currentProduct->totalSaleCost - currentProduct->totalPurchaseCost;
                if (currentProduct->totalSaleCost != 0.0f) {
                    currentProduct->profitMargin = (totalProfit / currentProduct->totalSaleCost) * 100.0f;
                } else {
                    currentProduct->profitMargin = 0.0f;
                }
                printf("销售额: %.2f, 利润: %.2f, 利润率: %.2f%%\n",
                       newSale->revenue, newSale->profit, newSale->margin);
                printf("销售成功，更新库存：%d\n", currentProduct->stock);
                return;
            }
            else {
                printf("库存不足，无法完成销售!\n");
                return;
            }
        }
        currentProduct = currentProduct->next;
    }

    printf("未找到产品ID为%d的产品!\n", productId);
}

// 在 PurchaseModule_doPurchase / SaleModule_doSale 函数处新增注释：
// 1. 进货/销售操作同时涉及更新产品库存、进货/销售记录，涉及指针遍历链表、修改某节点内的数据，以及新分配链表节点保存记录。
// 2. 这种多处修改带来的状态数据更新，体现了 C++ 代码在管理业务逻辑时的复杂性与灵活运用指针的重要性。

// 读取数据从文件
void loadFromFile(Product** products, User** users, PurchaseRecord** purchases, SaleRecord** sales) {
    FILE* file = fopen("/Users/huangtao/code/仓储管理系统/system_data.txt", "r"); // 修改此行
    if (file == NULL) {
        printf("无法打开文件进行读取，可能是第一次运行程序。\n");
        return;
    }

    char line[256];
    Section currentSection = NONE; // 新增局部变量

    while (fgets(line, sizeof(line), file)) {
        // 去除行末的换行符
        line[strcspn(line, "\r\n")] = 0;

        if (strcmp(line, "Products:") == 0) {
            currentSection = PRODUCTS;
            continue;
        }
        else if (strcmp(line, "Users:") == 0) {
            currentSection = USERS;
            continue;
        }
        else if (strcmp(line, "Purchases:") == 0) {
            currentSection = PURCHASES;
            continue;
        }
        else if (strcmp(line, "Sales:") == 0) {
            currentSection = SALES;
            continue;
        }

        if (currentSection == PRODUCTS) {
            int id, stock, sales;
            float pPrice, sPrice, tPurchase, tSale, pMargin;
            char name[MAX_NAME_LEN], category[MAX_NAME_LEN];
            if (sscanf(line, "%d,%99[^,],%99[^,],%d,%d,%f,%f,%f,%f,%f", &id, name, category, &stock, &sales, &pPrice, &sPrice, &tPurchase, &tSale, &pMargin) == 10) { // 修改此行
                ProductModule_add(products, id, name, category, stock, pPrice, sPrice);
                // 设置sales
                Product* temp = *products;
                while (temp != NULL) {
                    if (temp->id == id) {
                        temp->sales = sales;
                        temp->totalPurchaseCost = tPurchase;
                        temp->totalSaleCost = tSale;
                        temp->profitMargin = pMargin;
                        break;
                    }
                    temp = temp->next;
                }
            }
        }
        else if (currentSection == USERS) {
            char username[MAX_NAME_LEN], password[MAX_PASS_LEN];
            int role;
            if (sscanf(line, "%99[^,],%19[^,],%d", username, password, &role) == 3) { // 修改此行
                User* newUser = (User*)malloc(sizeof(User));
                if (newUser != NULL) {
                    strncpy(newUser->username, username, MAX_NAME_LEN - 1);
                    newUser->username[MAX_NAME_LEN - 1] = '\0';
                    strncpy(newUser->password, password, MAX_PASS_LEN - 1);
                    newUser->password[MAX_PASS_LEN - 1] = '\0';
                    newUser->role = role;
                    newUser->next = *users;
                    *users = newUser;
                }
            }
        }
        else if (currentSection == PURCHASES) {
            int productId, quantity;
            char date[MAX_NAME_LEN];
            if (sscanf(line, "%d,%d,%99s", &productId, &quantity, date) == 3) { // 修改此行
                PurchaseRecord* newPurchase = (PurchaseRecord*)malloc(sizeof(PurchaseRecord));
                if (newPurchase != NULL) {
                    newPurchase->productId = productId;
                    newPurchase->quantity = quantity;
                    strncpy(newPurchase->date, date, MAX_NAME_LEN - 1);
                    newPurchase->date[MAX_NAME_LEN - 1] = '\0';
                    newPurchase->next = *purchases;
                    *purchases = newPurchase;
                }
            }
        }
        else if (currentSection == SALES) {
            int productId, quantity;
            char date[MAX_NAME_LEN];
            if (sscanf(line, "%d,%d,%99s", &productId, &quantity, date) == 3) { // 修改此行
                SaleRecord* newSale = (SaleRecord*)malloc(sizeof(SaleRecord));
                if (newSale != NULL) {
                    newSale->productId = productId;
                    newSale->quantity = quantity;
                    strncpy(newSale->date, date, MAX_NAME_LEN - 1);
                    newSale->date[MAX_NAME_LEN - 1] = '\0';
                    newSale->next = *sales;
                    *sales = newSale;
                }
            }
        }
    }

    fclose(file);
    printf("数据读取成功!\n");
}

// 保存数据到文件
void saveToFile(Product* products, User* users, PurchaseRecord* purchases, SaleRecord* sales) {
    // 知识点: 使用fprintf格式化输出, 保存产品/用户/进货/销售记录
    FILE* file = fopen("/Users/huangtao/code/仓储管理系统/system_data.txt", "w"); // 修改此行
    if (file == NULL) { // 修改此行
        printf("无法打开文件进行保存!\n");
        return;
    }

    // 保存产品列表
    fprintf(file, "Products:\n");
    Product* currentProduct = products;
    while (currentProduct != NULL) {
        fprintf(file, "%d,%s,%s,%d,%d,%.2f,%.2f,%.2f,%.2f,%.2f\n", currentProduct->id, currentProduct->name, currentProduct->category, currentProduct->stock, currentProduct->sales, currentProduct->purchasePrice, currentProduct->salePrice, currentProduct->totalPurchaseCost, currentProduct->totalSaleCost, currentProduct->profitMargin); // 修改此行
        currentProduct = currentProduct->next;
    }

    // 保存用户列表
    fprintf(file, "Users:\n");
    User* currentUser = users;
    while (currentUser != NULL) {
        fprintf(file, "%s,%s,%d\n", currentUser->username, currentUser->password, currentUser->role);
        currentUser = currentUser->next;
    }

    // 保存进货记录
    fprintf(file, "Purchases:\n");
    PurchaseRecord* currentPurchase = purchases;
    while (currentPurchase != NULL) {
        fprintf(file, "%d,%d,%s\n", currentPurchase->productId, currentPurchase->quantity, currentPurchase->date);
        currentPurchase = currentPurchase->next;
    }

    // 保存销售记录
    fprintf(file, "Sales:\n");
    SaleRecord* currentSale = sales;
    while (currentSale != NULL) {
        fprintf(file, "%d,%d,%s\n", currentSale->productId, currentSale->quantity, currentSale->date);
        currentSale = currentSale->next;
    }

    fclose(file);
    printf("数据保存成功!\n");
}

// 在 loadFromFile/saveToFile 函数处新增注释：
// 1. 使用文件指针 FILE* 以及 fopen/fclose 函数进行文件读写操作，围绕产品、用户、进货、销售进行持久化保存。
// 2. 通过 fprintf/fscanf（或 sscanf）来进行格式化字符串读写，使得系统可以在下次运行时还原数据。

// 显示仓库工作人员菜单
void showStaffMenu() {
    printf("\n仓库工作人员菜单:\n");
    printf("1. 查询产品\n");
    printf("2. 查询产品销售情况\n");
    printf("0. 退出\n");
}

// 主菜单
void showMainModuleMenu() {
    printf("\n========== 管理员主菜单 ==========\n");
    printf("1. 产品管理\n");
    printf("2. 用户管理\n");
    printf("3. 进销管理\n");
    printf("4. 系统功能\n");
    printf("5. 保存数据\n"); // 新增：将保存数据选项独立到主菜单
    printf("0. 退出\n");
    printf("=================================\n");
}

// 二级菜单示例：产品管理
void ProductModule_showMenu() {
    printf("\n===== 产品管理 =====\n");
    printf("1. 添加产品\n");
    printf("2. 删除产品\n");
    printf("3. 修改产品\n");
    printf("4. 查询类别下的所有产品\n");
    printf("5. 查询产品\n");
    printf("6. 按销售量排序输出产品\n");
    printf("7. 显示所有仓储物品\n"); // 新增此行
    printf("0. 返回上一级\n");
    printf("===================\n");
}

// 新增用于用户管理的二级菜单示例
void UserModule_showMenu() {
    printf("\n===== 用户管理 =====\n");
    printf("1. 管理用户账户\n");
    printf("2. 查看所有用户信息\n"); // 新增此行
    printf("0. 返回上一级\n");
    printf("===================\n");
}

void UserModule_handle(User** users) {
    int choice;
    do {
        UserModule_showMenu();
        printf("请选择操作: ");
        if (scanf("%d", &choice) != 1) {
            printf("输入错误!\n");
            // 清空输入缓冲区
            int ch;
            while ((ch = getchar()) != '\n' && ch != EOF);
            continue;
        }
        switch (choice) {
            case 1:
                manageUserAccounts(users);
                break;
            case 2: {
                // 新增：查看所有用户信息
                displayAllUsers(*users);
                break;
            }
            case 0:
                break;
            default:
                printf("无效选项，请重新输入!\n");
        }
    } while (choice != 0);
}

// 新增用于进销管理的二级菜单示例
void PurchaseSaleModule_showMenu() {
    printf("\n===== 进销管理 =====\n");
    printf("1. 进货操作\n");
    printf("2. 销售操作\n");
    // 移除原有的“9. 保存数据”选项
    printf("0. 返回上一级\n");
    printf("===================\n");
}

void PurchaseSaleModule_handle(Product** products,
                              PurchaseRecord** purchases, 
                              SaleRecord** sales) {
    int choice;
    do {
        PurchaseSaleModule_showMenu();
        printf("请选择操作: ");
        if (scanf("%d", &choice) != 1) {
            printf("输入错误!\n");
            // 清空输入缓冲区
            int ch;
            while ((ch = getchar()) != '\n' && ch != EOF);
            continue;
        }
        switch (choice) {
            case 1: {
                int id, qty;
                char date[MAX_NAME_LEN] = {0};
                printf("请输入进货的产品ID和数量: ");
                // 清空输入缓冲区
                int ch;
                while ((ch = getchar()) != '\n' && ch != EOF);
                if (scanf("%d %d", &id, &qty) != 2) {
                    printf("输入错误!\n");
                    // 清空输入缓冲区
                    while ((ch = getchar()) != '\n' && ch != EOF);
                    break;
                }
                printf("请输入进货日期: ");
                if (scanf("%99s", date) != 1) {
                    printf("输入错误!\n");
                    // 清空输入缓冲区
                    while ((ch = getchar()) != '\n' && ch != EOF);
                    break;
                }
                PurchaseModule_doPurchase(purchases, *products, id, qty, date);
                break;
            }
            case 2: {
                int id, qty;
                char date[MAX_NAME_LEN] = {0};
                printf("请输入销售的产品ID和数量: ");
                // 清空输入缓冲区
                int ch;
                while ((ch = getchar()) != '\n' && ch != EOF);
                if (scanf("%d %d", &id, &qty) != 2) {
                    printf("输入错误!\n");
                    // 清空输入缓冲区
                    while ((ch = getchar()) != '\n' && ch != EOF);
                    break;
                }
                printf("请输入销售日期: ");
                if (scanf("%99s", date) != 1) {
                    printf("输入错误!\n");
                    // 清空输入缓冲区
                    while ((ch = getchar()) != '\n' && ch != EOF);
                    break;
                }
                SaleModule_doSale(sales, *products, id, qty, date);
                break;
            }
            case 0:
                break;
            default:
                printf("无效选项，请重新输入!\n");
        }
    } while (choice != 0);
}

// 新增用于系统功能的二级菜单示例
void SystemModule_showMenu() {
    printf("\n===== 系统功能 =====\n");
    printf("1. 保存数据\n");
    printf("2. 修改管理员密码\n");
    printf("0. 返回上一级\n");
    printf("===================\n");
}

// 修改函数签名，增加 User* users 参数
void SystemModule_handle(Product* products, User* users,
                        PurchaseRecord* purchases, SaleRecord* sales) {
    int choice;
    do {
        SystemModule_showMenu();
        printf("请选择操作: ");
        if (scanf("%d", &choice) != 1) {
            printf("输入错误!\n");
            // 清空输入缓冲区
            int ch;
            while ((ch = getchar()) != '\n' && ch != EOF);
            continue;
        }
        switch (choice) {
            case 1:
                // 将原先传递 NULL 改为 users，以正确保存用户信息
                saveToFile(products, users, purchases, sales);
                break;
            case 2:
                modifyAdminPassword(users); 
                break;
            case 0:
                break;
            default:
                printf("无效选项，请重新输入!\n");
        }
    } while (choice != 0);
}

// 在 adminOperations 中，调用 SystemModule_handle 时，带上 users
void adminOperations(Product** products, User* users,
                     PurchaseRecord** purchases, SaleRecord** sales, User* currentUser) { // 扩展 adminOperations 函数签名
    int choice;
    do {
        showMainModuleMenu();
        printf("请选择模块: ");
        if (scanf("%d", &choice) != 1) {
            printf("输入错误!\n");
            // 清空输入缓冲区
            int ch;
            while ((ch = getchar()) != '\n' && ch != EOF);
            choice = -1; // 设置为无效选项
            continue;
        }
        switch (choice) {
            case 1: {
                // 进入产品管理二级菜单
                int productChoice;
                do {
                    ProductModule_showMenu();
                    printf("请选择操作: ");
                    if (scanf("%d", &productChoice) != 1) {
                        printf("输入错误!\n");
                        // 清空输入缓冲区
                        int ch;
                        while ((ch = getchar()) != '\n' && ch != EOF);
                        continue;
                    }
                    switch (productChoice) {
                        case 1: {
                            int id, stock;
                            char name[MAX_NAME_LEN] = { 0 }, category[MAX_NAME_LEN] = { 0 };
                            float pPrice, sPrice; // 新增
                            printf("请输入产品ID: ");
                            if (scanf("%d", &id) != 1) { // 修改此行
                                printf("输入错误!\n");
                                // 清空输入缓冲区
                                int ch;
                                while ((ch = getchar()) != '\n' && ch != EOF);
                                break;
                            }
                            printf("请输入产品名称: ");
                            if (scanf("%99s", name) != 1) { // 修改此行
                                printf("输入错误!\n");
                                break;
                            }
                            printf("请输入产品类别: ");
                            if (scanf("%99s", category) != 1) { // 修改此行
                                printf("输入错误!\n");
                                break;
                            }
                            printf("请输入库存数量: ");
                            if (scanf("%d", &stock) != 1) { // 修改此行
                                printf("输入错误!\n");
                                // 清空输入缓冲区
                                int ch;
                                while ((ch = getchar()) != '\n' && ch != EOF);
                                break;
                            }
                            printf("请输入进货价: "); // 新增
                            if (scanf("%f", &pPrice) != 1) { // 新增
                                printf("输入错误!\n");
                                // 清空输入缓冲区
                                int ch;
                                while ((ch = getchar()) != '\n' && ch != EOF);
                                break;
                            }
                            printf("请输入销售价: "); // 新增
                            if (scanf("%f", &sPrice) != 1) { // 新增
                                printf("输入错误!\n");
                                // 清空输入缓冲区
                                int ch;
                                while ((ch = getchar()) != '\n' && ch != EOF);
                                break;
                            }
                            ProductModule_add(products, id, name, category, stock, pPrice, sPrice); // 修改此行
                            break;
                        }
                        case 2: {
                            int id;
                            printf("请输入要删除的产品ID: ");
                            if (scanf("%d", &id) != 1) { // 修改此行
                                printf("输入错误!\n");
                                // 清空输入缓冲区
                                int ch;
                                while ((ch = getchar()) != '\n' && ch != EOF);
                                break;
                            }
                            ProductModule_delete(products, id);
                            break;
                        }
                        case 3: {
                            int id;
                            printf("请输入要修改的产品ID: ");
                            if (scanf("%d", &id) != 1) { // 修改此行
                                printf("输入错误!\n");
                                // 清空输入缓冲区
                                int ch;
                                while ((ch = getchar()) != '\n' && ch != EOF);
                                break;
                            }
                            ProductModule_modify(*products, id);
                            break;
                        }
                        case 4: { // 调整后的查询类别
                            char category[MAX_NAME_LEN] = { 0 };
                            printf("请输入要查询的类别名称: ");
                            if (scanf("%99s", category) != 1) { // 修改此行
                                printf("输入错误!\n");
                                break;
                            }
                            ProductModule_queryByCategory(*products, category);
                            break;
                        }
                        case 5: { // 原4号查询产品
                            int id;
                            printf("请输入要查询的产品ID: ");
                            if (scanf("%d", &id) != 1) { // 修改此行
                                printf("输入错误!\n");
                                // 清空输入缓冲区
                                int ch;
                                while ((ch = getchar()) != '\n' && ch != EOF);
                                break;
                            }
                            ProductModule_query(*products, id);
                            break;
                        }
                        case 6: { // 修改后的第6项: 按销售量排序输出产品
                            ProductModule_sortAndDisplayBySales(*products);
                            break;
                        }
                        case 7: { // 新增选项: 显示所有仓储物品
                            ProductModule_displayAll(*products);
                            break;
                        }
                        case 0:
                            break;
                        default:
                            printf("无效选项，请重新输入!\n");
                    }
                } while (productChoice != 0);
                break;
            }
            case 2:
                // 新增调用用户管理模块
                UserModule_handle(&users);
                break;
            case 3:
                // 新增调用进销管理模块
                PurchaseSaleModule_handle(products, purchases, sales);
                break;
            case 4:
                // 新增调用系统功能模块
                SystemModule_handle(*products, users, *purchases, *sales); // 在处理系统功能时，将当前登录用户指针正确传递给 SystemModule_handle
                break;
            case 5:
                // 新增：处理保存数据逻辑
                saveToFile(*products, users, *purchases, *sales);
                break;
            case 0:
                printf("退出系统!\n");
                break;
            default:
                printf("无效选项，请重新输入!\n");
        }
    } while (choice != 0);
}

// 仓库工作人员操作
void staffOperations(Product* products, SaleRecord* sales) {
    int choice, id;
    int ch; // 用于清空输入缓冲
    do {
        printf("\n仓库工作人员菜单:\n");
        printf("1. 查询产品\n");
        printf("2. 查询产品销售情况\n");
        printf("0. 退出\n");
        printf("请选择操作: ");
        if (scanf("%d", &choice) != 1) {
            while ((ch = getchar()) != '\n' && ch != EOF);
            continue;
        }
        switch (choice) {
            case 1: {
                printf("请输入要查询的产品ID: ");
                while ((ch = getchar()) != '\n' && ch != EOF);
                if (scanf("%d", &id) != 1) {
                    while ((ch = getchar()) != '\n' && ch != EOF);
                    break;
                }
                ProductModule_query(products, id);
                break;
            }
            case 2: {
                printf("请输入要查询销售情况的产品ID: ");
                while ((ch = getchar()) != '\n' && ch != EOF);
                if (scanf("%d", &id) != 1) {
                    while ((ch = getchar()) != '\n' && ch != EOF);
                    break;
                }
                ProductModule_querySales(products, sales, id);
                break;
            }
            case 0:
                printf("退出仓库工作人员操作.\n");
                break;
            default:
                printf("无效选项，请重新输入!\n");
        }
    } while (choice != 0);
}

// 将原 UserControl.cpp 中的函数合并至此处
// ====================== UserControl Functions Start ======================

void displayAdminInfo(User* currentUser) {
    // 如果是管理员，则输出其关键信息
    if (!currentUser || currentUser->role != 0) {
        printf("当前用户不是管理员或无效。\n");
        return;
    }
    printf("管理员账户信息:\n");
    printf("用户名: %s\n", currentUser->username);
    printf("角色: 管理员\n");
    // ...existing code if needed...
}

void displayUserInfo(User* currentUser) {
    // 显示当前登录用户的基本信息
    if (!currentUser) {
        printf("用户信息无效。\n");
        return;
    }
    printf("当前登录用户信息:\n");
    printf("用户名: %s\n", currentUser->username);
    if (currentUser->role == 0) {
        printf("角色: 管理员\n");
    } else {
        printf("角色: 仓库工作人员\n");
    }
    // ...existing code if needed...
}

void displayAllUsers(User* users) {
    // 遍历并打印所有用户信息
    if (!users) {
        printf("当前无用户。\n");
        return;
    }
    printf("系统用户列表:\n");
    User* temp = users;
    while (temp) {
        printf("用户名: %s | 角色: %s\n", 
               temp->username, 
               temp->role == 0 ? "管理员" : "仓库工作人员");
        temp = temp->next;
    }
    // ...existing code if needed...
}

// 示例：修改管理员密码
void modifyAdminPassword(User* currentUser) {
    char newPass[MAX_PASS_LEN];
    printf("请输入新密码: ");
    if (scanf("%19s", newPass) != 1) {
        printf("输入错误!\n");
        // 清空输入缓冲区
        int ch;
        while ((ch = getchar()) != '\n' && ch != EOF);
        return;
    }
    strncpy(currentUser->password, newPass, MAX_PASS_LEN - 1);
    currentUser->password[MAX_PASS_LEN - 1] = '\0';
    printf("管理员密码修改成功!\n");
}

// 示例：管理用户账户
void manageUserAccounts(User** users) {
    int choice = 0;
    do {
        printf("\n===== 管理用户账户 =====\n");
        printf("1. 添加用户\n");
        printf("2. 删除用户\n");
        printf("3. 修改用户密码\n");
        printf("0. 返回上一级\n");
        printf("请选择操作: ");

        if (scanf("%d", &choice) != 1) {
            printf("输入错误!\n");
            // 清空输入缓冲区
            int ch;
            while ((ch = getchar()) != '\n' && ch != EOF);
            continue;
        }

        switch (choice) {
            case 1: {
                // 交互式添加新用户
                char username[MAX_NAME_LEN], password[MAX_PASS_LEN];
                int role;
                printf("请输入用户名: ");
                if (scanf("%99s", username) != 1) {
                    printf("输入错误!\n");
                    break;
                }
                printf("请输入密码: ");
                if (scanf("%19s", password) != 1) {
                    printf("输入错误!\n");
                    break;
                }
                printf("请输入角色 (0-管理员, 1-仓库工作人员): ");
                if (scanf("%d", &role) != 1) {
                    printf("输入错误!\n");
                    break;
                }
                User* newUser = (User*)malloc(sizeof(User));
                if (newUser != NULL) {
                    strncpy(newUser->username, username, MAX_NAME_LEN - 1);
                    newUser->username[MAX_NAME_LEN - 1] = '\0';
                    strncpy(newUser->password, password, MAX_PASS_LEN - 1);
                    newUser->password[MAX_PASS_LEN - 1] = '\0';
                    newUser->role = role;
                    newUser->next = *users;
                    *users = newUser;
                    printf("成功添加新用户!\n");
                } else {
                    printf("内存分配失败!\n");
                }
                break;
            }
            case 2: {
                // 交互式删除用户
                char username[MAX_NAME_LEN];
                printf("请输入要删除的用户名: ");
                if (scanf("%99s", username) != 1) {
                    printf("输入错误!\n");
                    break;
                }
                User* current = *users;
                User* previous = NULL;
                while (current != NULL) {
                    if (strcmp(current->username, username) == 0) {
                        if (previous == NULL) {
                            *users = current->next;
                        } else {
                            previous->next = current->next;
                        }
                        free(current);
                        printf("成功删除指定用户!\n");
                        break;
                    }
                    previous = current;
                    current = current->next;
                }
                if (current == NULL) {
                    printf("未找到指定用户!\n");
                }
                break;
            }
            case 3: {
                // 交互式修改用户密码
                char username[MAX_NAME_LEN], newPassword[MAX_PASS_LEN];
                printf("请输入要修改密码的用户名: ");
                if (scanf("%99s", username) != 1) {
                    printf("输入错误!\n");
                    break;
                }
                printf("请输入新密码: ");
                if (scanf("%19s", newPassword) != 1) {
                    printf("输入错误!\n");
                    break;
                }
                User* current = *users;
                while (current != NULL) {
                    if (strcmp(current->username, username) == 0) {
                        strncpy(current->password, newPassword, MAX_PASS_LEN - 1);
                        current->password[MAX_PASS_LEN - 1] = '\0';
                        printf("成功修改用户密码!\n");
                        break;
                    }
                    current = current->next;
                }
                if (current == NULL) {
                    printf("未找到指定用户!\n");
                }
                break;
            }
            case 0:
                break;
            default:
                printf("无效选项，请重新输入!\n");
        }
    } while (choice != 0);
}

// ====================== UserControl Functions End ========================

void updateProductCost(Product* product, int quantity, float purchasePrice) {
    product->stock += quantity;
    product->totalPurchaseCost += purchasePrice * quantity;
}

// 主函数
int main() {
    // 用户和产品链表
    User* users = NULL;
    Product* products = NULL;
    PurchaseRecord* purchases = NULL;
    SaleRecord* sales = NULL;

    // 读取已有的数据
    loadFromFile(&products, &users, &purchases, &sales);

    // 如果没有用户数据，则添加测试数据
    if (users == NULL) {
        // 添加测试数据（可以根据实际需求添加用户和产品数据）
        User* admin = (User*)malloc(sizeof(User));
        if (admin == NULL) {
            printf("内存分配失败!\n");
            return -1;
        }
        strncpy(admin->username, "admin", MAX_NAME_LEN - 1);
        admin->username[MAX_NAME_LEN - 1] = '\0';
        strncpy(admin->password, "admin123", MAX_PASS_LEN - 1);
        admin->password[MAX_PASS_LEN - 1] = '\0';
        admin->role = 0;  // 管理员
        admin->next = users;
        users = admin;

        User* staff = (User*)malloc(sizeof(User));
        if (staff == NULL) {
            printf("内存分配失败!\n");
            return -1;
        }
        strncpy(staff->username, "staff", MAX_NAME_LEN - 1);
        staff->username[MAX_NAME_LEN - 1] = '\0';
        strncpy(staff->password, "staff123", MAX_PASS_LEN - 1);
        staff->password[MAX_PASS_LEN - 1] = '\0';
        staff->role = 1;  // 仓库工作人员
        staff->next = users;
        users = staff;
    }

    // 登录操作
    User* currentUser = login(users); // 使用新的登录函数
    if (!currentUser) {
        printf("登录失败，程序退出。\n");
        return 0;  // 登录失败
    }

    // 如果是管理员账户，则自动显示当前管理员信息及所有用户信息
    if (currentUser->role == 0) {
        displayAllUsers(users);   // 额外显示所有用户信息
        adminOperations(&products, users, &purchases, &sales, currentUser); // 将当前用户指针传给 adminOperations
    } else if (currentUser->role == 1) {
        staffOperations(products, sales);
    }

    return 0;
}
