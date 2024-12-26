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

// 函数声明
User* login(User* userList); // 修改登录函数的返回类型
void addProduct(Product** productList, int id, const char* name, const char* category, int stock, float purchasePrice, float salePrice); // 修改函数声明
void deleteProduct(Product** productList, int id);
void modifyProduct(Product* productList, int id);
void queryProduct(Product* productList, int id);
void querySales(Product* productList, SaleRecord* saleList, int id);
void queryByCategory(Product* productList, const char* category); // 新增函数声明
void managePurchase(PurchaseRecord** purchaseList, Product* productList, int productId, int quantity, const char* date);
void manageSale(SaleRecord** saleList, Product* productList, int productId, int quantity, const char* date);
void loadFromFile(Product** productList, User** userList, PurchaseRecord** purchaseList, SaleRecord** saleList);
void saveToFile(Product* productList, User* userList, PurchaseRecord* purchaseList, SaleRecord* saleList);
void showAdminMenu();
void showStaffMenu();
void adminOperations(Product** productList, User* userList, PurchaseRecord** purchaseList, SaleRecord** saleList, User* currentUser); // 扩展 adminOperations 函数签名
void staffOperations(Product* productList, SaleRecord* saleList);
void sortAndDisplayBySales(Product* productList); // 新增函数声明
void displayAllProducts(Product* productList); // 添加此行

// 登录功能
User* login(User* userList) { // 修改登录函数的返回类型
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

    User* current = userList;
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

// 增加产品
void addProduct(Product** productList, int id, const char* name, const char* category, int stock, float purchasePrice, float salePrice) { // 修改函数签名
    Product* newProduct = (Product*)malloc(sizeof(Product));
    if (newProduct == NULL) {
        printf("内存分配失败!\n");
        return;
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
    newProduct->next = *productList;
    *productList = newProduct;

    printf("产品'%s'添加成功!\n", name);
}

// 删除产品
void deleteProduct(Product** productList, int id) {
    Product* current = *productList;
    Product* previous = NULL;

    while (current != NULL) {
        if (current->id == id) {
            if (previous == NULL) {
                *productList = current->next;
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

// 修改产品
void modifyProduct(Product* productList, int id) {
    Product* current = productList;

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
void queryProduct(Product* productList, int id) {
    Product* current = productList;
    while (current != NULL) {
        if (current->id == id) {
            printf("产品ID: %d\n", current->id);
            printf("产品名称: %s\n", current->name);
            printf("产品类别: %s\n", current->category);
            printf("库存数量: %d\n", current->stock);
            printf("已售数量: %d\n", current->sales);
            printf("进货总成本: %.2f\n", current->totalPurchaseCost);
            printf("销售总成本: %.2f\n", current->totalSaleCost);
            printf("利润率: %.2f%%\n", current->profitMargin);
            return;
        }
        current = current->next;
    }

    printf("未找到产品ID为%d的产品!\n", id);
}

// 查询产品销售情况
void querySales(Product* productList, SaleRecord* saleList, int id) {
    Product* currentProduct = productList;
    while (currentProduct != NULL) {
        if (currentProduct->id == id) {
            int totalSales = 0;
            SaleRecord* currentSale = saleList;
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
void queryByCategory(Product* productList, const char* category) {
    Product* current = productList;
    int found = 0;
    printf("类别 '%s' 下的所有产品:\n", category);
    printf("---------------------------\n");
    while (current != NULL) {
        if (strcmp(current->category, category) == 0) {
            printf("产品ID: %d\n", current->id);
            printf("产品名称: %s\n", current->name);
            printf("产品类别: %s\n", current->category);
            printf("库存数量: %d\n", current->stock);
            printf("已售数量: %d\n", current->sales);
            printf("进货总成本: %.2f\n", current->totalPurchaseCost);
            printf("销售总成本: %.2f\n", current->totalSaleCost);
            printf("利润率: %.2f%%\n", current->profitMargin);
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
void sortAndDisplayBySales(Product* productList) {
    // 计算产品数量
    int count = 0;
    Product* current = productList;
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
    current = productList;
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
    printf("-----------------------------------------------------------------------\n");
    printf("| %-5s | %-20s | %-8s | %-8s | %-8s | %-10s | %-10s | %-8s |\n",
           "ID", "名称", "库存", "销售", "进货价", "进货总成本", "销售总成本", "利润率");
    printf("-----------------------------------------------------------------------\n");
    for (int i = 0; i < count; i++) {
        printf("| %-5d | %-20s | %-8d | %-8d | %-8.2f | %-10.2f | %-10.2f | %-7.2f%% |\n",
               productArray[i]->id,
               productArray[i]->name,
               productArray[i]->stock,
               productArray[i]->sales,
               productArray[i]->purchasePrice,
               productArray[i]->totalPurchaseCost,
               productArray[i]->totalSaleCost,
               productArray[i]->profitMargin);
    }
    printf("--------------------------------------------------\n");

    free(productArray);
}

// 实现 displayAllProducts 函数
void displayAllProducts(Product* productList) {
    Product* current = productList;
    if (current == NULL) {
        printf("当前没有仓储物品信息。\n");
        return;
    }
    printf("========== 全部仓储物品信息 ==========\n");
    printf("| %-5s | %-20s | %-10s | %-8s | %-8s | %-10s | %-10s | %-8s |\n",
           "ID", "名称", "类别", "库存", "销售", "进货总成本", "销售总成本", "利润率");
    printf("---------------------------------------------------------------\n");
    while (current != NULL) {
        printf("| %-5d | %-20s | %-10s | %-8d | %-8d | %-10.2f | %-10.2f | %-7.2f%% |\n",
               current->id,
               current->name,
               current->category,
               current->stock,
               current->sales,
               current->totalPurchaseCost,
               current->totalSaleCost,
               current->profitMargin);
        current = current->next;
    }
    printf("---------------------------------------------------------------\n");
}

// 进货管理
void managePurchase(PurchaseRecord** purchaseList, Product* productList, int productId, int quantity, const char* date) {
    PurchaseRecord* newPurchase = (PurchaseRecord*)malloc(sizeof(PurchaseRecord));
    if (newPurchase == NULL) {
        printf("内存分配失败!\n");
        return;
    }

    newPurchase->productId = productId;
    newPurchase->quantity = quantity;
    strncpy(newPurchase->date, date, MAX_NAME_LEN - 1);
    newPurchase->date[MAX_NAME_LEN - 1] = '\0';
    newPurchase->next = *purchaseList;
    *purchaseList = newPurchase;

    // 更新库存
    Product* currentProduct = productList;
    while (currentProduct != NULL) {
        if (currentProduct->id == productId) {
            currentProduct->stock += quantity;
            currentProduct->totalPurchaseCost += currentProduct->purchasePrice * quantity; // 新增：累加进货总成本
            printf("进货成功，更新库存：%d\n", currentProduct->stock);
            return;
        }
        currentProduct = currentProduct->next;
    }

    printf("未找到产品ID为%d的产品!\n", productId);
}

// 销售管理
void manageSale(SaleRecord** saleList, Product* productList, int productId, int quantity, const char* date) {
    SaleRecord* newSale = (SaleRecord*)malloc(sizeof(SaleRecord));
    if (newSale == NULL) {
        printf("内存分配失败!\n");
        return;
    }

    newSale->productId = productId;
    newSale->quantity = quantity;
    strncpy(newSale->date, date, MAX_NAME_LEN - 1);
    newSale->date[MAX_NAME_LEN - 1] = '\0';
    newSale->next = *saleList;
    *saleList = newSale;

    // 更新库存
    Product* currentProduct = productList;
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

// 读取数据从文件
void loadFromFile(Product** productList, User** userList, PurchaseRecord** purchaseList, SaleRecord** saleList) {
    FILE* file = fopen("/Users/huangtao/code/仓储管理系统/system_data.txt", "r"); // 修改此行
    if (file == NULL) {
        printf("无法打开文件进行读取，可能是第一次运行程序。\n");
        return;
    }

    char line[256];
    enum Section { NONE, PRODUCTS, USERS, PURCHASES, SALES } currentSection = NONE;

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
                addProduct(productList, id, name, category, stock, pPrice, sPrice);
                // 设置sales
                Product* temp = *productList;
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
                    newUser->next = *userList;
                    *userList = newUser;
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
                    newPurchase->next = *purchaseList;
                    *purchaseList = newPurchase;
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
                    newSale->next = *saleList;
                    *saleList = newSale;
                }
            }
        }
    }

    fclose(file);
    printf("数据读取成功!\n");
}

// 保存数据到文件
void saveToFile(Product* productList, User* userList, PurchaseRecord* purchaseList, SaleRecord* saleList) {
    FILE* file = fopen("/Users/huangtao/code/仓储管理系统/system_data.txt", "w"); // 修改此行
    if (file == NULL) { // 修改此行
        printf("无法打开文件进行保存!\n");
        return;
    }

    // 保存产品列表
    fprintf(file, "Products:\n");
    Product* currentProduct = productList;
    while (currentProduct != NULL) {
        fprintf(file, "%d,%s,%s,%d,%d,%.2f,%.2f,%.2f,%.2f,%.2f\n", currentProduct->id, currentProduct->name, currentProduct->category, currentProduct->stock, currentProduct->sales, currentProduct->purchasePrice, currentProduct->salePrice, currentProduct->totalPurchaseCost, currentProduct->totalSaleCost, currentProduct->profitMargin); // 修改此行
        currentProduct = currentProduct->next;
    }

    // 保存用户列表
    fprintf(file, "Users:\n");
    User* currentUser = userList;
    while (currentUser != NULL) {
        fprintf(file, "%s,%s,%d\n", currentUser->username, currentUser->password, currentUser->role);
        currentUser = currentUser->next;
    }

    // 保存进货记录
    fprintf(file, "Purchases:\n");
    PurchaseRecord* currentPurchase = purchaseList;
    while (currentPurchase != NULL) {
        fprintf(file, "%d,%d,%s\n", currentPurchase->productId, currentPurchase->quantity, currentPurchase->date);
        currentPurchase = currentPurchase->next;
    }

    // 保存销售记录
    fprintf(file, "Sales:\n");
    SaleRecord* currentSale = saleList;
    while (currentSale != NULL) {
        fprintf(file, "%d,%d,%s\n", currentSale->productId, currentSale->quantity, currentSale->date);
        currentSale = currentSale->next;
    }

    fclose(file);
    printf("数据保存成功!\n");
}

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
void showProductMenu() {
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
void showUserMenu() {
    printf("\n===== 用户管理 =====\n");
    printf("1. 管理用户账户\n");
    printf("2. 查看所有用户信息\n"); // 新增此行
    printf("0. 返回上一级\n");
    printf("===================\n");
}

void handleUserModule(User** userList) {
    int choice;
    do {
        showUserMenu();
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
                manageUserAccounts(userList);
                break;
            case 2: {
                // 新增：查看所有用户信息
                displayAllUsers(*userList);
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
void showPurchaseSaleMenu() {
    printf("\n===== 进销管理 =====\n");
    printf("1. 进货操作\n");
    printf("2. 销售操作\n");
    // 移除原有的“9. 保存数据”选项
    printf("0. 返回上一级\n");
    printf("===================\n");
}

void handlePurchaseSaleModule(Product** productList,
                              PurchaseRecord** purchaseList, 
                              SaleRecord** saleList) {
    int choice;
    do {
        showPurchaseSaleMenu();
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
                managePurchase(purchaseList, *productList, id, qty, date);
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
                manageSale(saleList, *productList, id, qty, date);
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
void showSystemMenu() {
    printf("\n===== 系统功能 =====\n");
    printf("1. 保存数据\n");
    printf("2. 修改管理员密码\n");
    printf("0. 返回上一级\n");
    printf("===================\n");
}

// 修改函数签名，增加 User* userList 参数
void handleSystemModule(Product* productList, User* userList,
                        PurchaseRecord* purchaseList, SaleRecord* saleList) {
    int choice;
    do {
        showSystemMenu();
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
                // 将原先传递 NULL 改为 userList，以正确保存用户信息
                saveToFile(productList, userList, purchaseList, saleList);
                break;
            case 2:
                modifyAdminPassword(userList); 
                break;
            case 0:
                break;
            default:
                printf("无效选项，请重新输入!\n");
        }
    } while (choice != 0);
}

// 在 adminOperations 中，调用 handleSystemModule 时，带上 userList
void adminOperations(Product** productList, User* userList,
                     PurchaseRecord** purchaseList, SaleRecord** saleList, User* currentUser) { // 扩展 adminOperations 函数签名
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
                    showProductMenu();
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
                            addProduct(productList, id, name, category, stock, pPrice, sPrice); // 修改此行
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
                            deleteProduct(productList, id);
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
                            modifyProduct(*productList, id);
                            break;
                        }
                        case 4: { // 调整后的查询类别
                            char category[MAX_NAME_LEN] = { 0 };
                            printf("请输入要查询的类别名称: ");
                            if (scanf("%99s", category) != 1) { // 修改此行
                                printf("输入错误!\n");
                                break;
                            }
                            queryByCategory(*productList, category);
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
                            queryProduct(*productList, id);
                            break;
                        }
                        case 6: { // 修改后的第6项: 按销售量排序输出产品
                            sortAndDisplayBySales(*productList);
                            break;
                        }
                        case 7: { // 新增选项: 显示所有仓储物品
                            displayAllProducts(*productList);
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
                handleUserModule(&userList);
                break;
            case 3:
                // 新增调用进销管理模块
                handlePurchaseSaleModule(productList, purchaseList, saleList);
                break;
            case 4:
                // 新增调用系统功能模块
                handleSystemModule(*productList, userList, *purchaseList, *saleList); // 在处理系统功能时，将当前登录用户指针正确传递给 handleSystemModule
                break;
            case 5:
                // 新增：处理保存数据逻辑
                saveToFile(*productList, userList, *purchaseList, *saleList);
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
void staffOperations(Product* productList, SaleRecord* saleList) {
    int choice;
    do {
        showStaffMenu();
        printf("请输入操作选项: ");
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
            int id;
            printf("请输入要查询的产品ID: ");
            if (scanf("%d", &id) != 1) { // 修改此行
                printf("输入错误!\n");
                // 清空输入缓冲区
                int ch;
                while ((ch = getchar()) != '\n' && ch != EOF);
                break;
            }
            queryProduct(productList, id);
            break;
        }
        case 2: {
            int id;
            printf("请输入要查询的产品ID: ");
            if (scanf("%d", &id) != 1) { // 修改此行
                printf("输入错误!\n");
                // 清空输入缓冲区
                int ch;
                while ((ch = getchar()) != '\n' && ch != EOF);
                break;
            }
            querySales(productList, saleList, id);
            break;
        }
        case 0:
            printf("退出系统!\n");
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

void displayAllUsers(User* userList) {
    // 遍历并打印所有用户信息
    if (!userList) {
        printf("当前无用户。\n");
        return;
    }
    printf("系统用户列表:\n");
    User* temp = userList;
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
void manageUserAccounts(User** userList) {
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
                    newUser->next = *userList;
                    *userList = newUser;
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
                User* current = *userList;
                User* previous = NULL;
                while (current != NULL) {
                    if (strcmp(current->username, username) == 0) {
                        if (previous == NULL) {
                            *userList = current->next;
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
                User* current = *userList;
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

// 主函数
int main() {
    // 用户和产品链表
    User* userList = NULL;
    Product* productList = NULL;
    PurchaseRecord* purchaseList = NULL;
    SaleRecord* saleList = NULL;

    // 读取已有的数据
    loadFromFile(&productList, &userList, &purchaseList, &saleList);

    // 如果没有用户数据，则添加测试数据
    if (userList == NULL) {
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
        admin->next = userList;
        userList = admin;

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
        staff->next = userList;
        userList = staff;
    }

    // 登录操作
    User* currentUser = login(userList); // 使用新的登录函数
    if (!currentUser) {
        printf("登录失败，程序退出。\n");
        return 0;  // 登录失败
    }

    // 如果是管理员账户，则自动显示当前管理员信息及所有用户信息
    if (currentUser->role == 0) {
        displayAllUsers(userList);   // 额外显示所有用户信息
        adminOperations(&productList, userList, &purchaseList, &saleList, currentUser); // 将当前用户指针传给 adminOperations
    } else if (currentUser->role == 1) {
        staffOperations(productList, saleList);
    }

    return 0;
}
