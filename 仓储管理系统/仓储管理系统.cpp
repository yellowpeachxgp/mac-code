#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_NAME_LEN 100
#define MAX_PASS_LEN 20

// 产品信息结构体
typedef struct Product {
    int id;                     // 产品ID
    char name[MAX_NAME_LEN];     // 产品名称
    char category[MAX_NAME_LEN]; // 产品类别
    int stock;                  // 当前库存
    int sales;                  // 销售数量
    struct Product* next;       // 链表的下一个产品
} Product;

// 用户信息结构体
typedef struct User {
    char username[MAX_NAME_LEN];  // 用户名
    char password[MAX_PASS_LEN];  // 密码
    int role;                     // 0:管理员, 1:仓库工作人员
    struct User* next;            // 链表的下一个用户
} User;

// 进货记录结构体
typedef struct PurchaseRecord {
    int productId;                // 产品ID
    int quantity;                 // 进货数量
    char date[MAX_NAME_LEN];      // 进货日期
    struct PurchaseRecord* next;  // 链表的下一个进货记录
} PurchaseRecord;

// 销售记录结构体
typedef struct SaleRecord {
    int productId;                // 产品ID
    int quantity;                 // 销售数量
    char date[MAX_NAME_LEN];      // 销售日期
    struct SaleRecord* next;      // 链表的下一个销售记录
} SaleRecord;

// 产品类别信息结构体
typedef struct Category {
    char name[MAX_NAME_LEN];  // 类别名称
    Product* productList;     // 该类别下的产品列表
    struct Category* next;    // 链表的下一个类别
} Category;

// 函数声明
int login(User* userList);
void addProduct(Product** productList, int id, const char* name, const char* category, int stock);
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
void adminOperations(Product** productList, User* userList, PurchaseRecord** purchaseList, SaleRecord** saleList);
void staffOperations(Product* productList, SaleRecord* saleList);
void sortAndDisplayBySales(Product* productList); // 新增函数声明

// 登录功能
int login(User* userList) {
    char username[MAX_NAME_LEN] = { 0 }, password[MAX_PASS_LEN] = { 0 };
    printf("请输入用户名: ");
    if (scanf("%99s", username) != 1) { // 修改此行
        printf("用户名输入失败!\n");
        return -1;
    }

    printf("请输入密码: ");
    if (scanf("%19s", password) != 1) { // 修改此行
        printf("密码输入失败!\n");
        return -1;
    }

    User* current = userList;
    while (current != NULL) {
        if (strcmp(current->username, username) == 0 && strcmp(current->password, password) == 0) {
            printf("登录成功!\n");
            return current->role;  // 返回用户的角色（0为管理员，1为仓库工作人员）
        }
        current = current->next;
    }

    printf("用户名或密码错误!\n");
    return -1; // 登录失败
}

// 增加产品
void addProduct(Product** productList, int id, const char* name, const char* category, int stock) {
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
            printf("库存数量: %d\n", current->stock);
            printf("已售数量: %d\n", current->sales);
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
    printf("--------------------------------------------------\n");
    printf("| %-5s | %-20s | %-15s | %-8s | %-8s |\n", "ID", "名称", "类别", "库存", "销售");
    printf("--------------------------------------------------\n");
    for (int i = 0; i < count; i++) {
        printf("| %-5d | %-20s | %-15s | %-8d | %-8d |\n",
            productArray[i]->id,
            productArray[i]->name,
            productArray[i]->category,
            productArray[i]->stock,
            productArray[i]->sales);
    }
    printf("--------------------------------------------------\n");

    free(productArray);
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
    FILE* file = fopen("system_data.txt", "r"); // 修改此行
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
            char name[MAX_NAME_LEN], category[MAX_NAME_LEN];
            if (sscanf(line, "%d,%99[^,],%99[^,],%d,%d", &id, name, category, &stock, &sales) == 5) { // 修改此行
                addProduct(productList, id, name, category, stock);
                // 设置sales
                Product* temp = *productList;
                while (temp != NULL) {
                    if (temp->id == id) {
                        temp->sales = sales;
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
    FILE* file = fopen("system_data.txt", "w"); // 修改此行
    if (file == NULL) { // 修改此行
        printf("无法打开文件进行保存!\n");
        return;
    }

    // 保存产品列表
    fprintf(file, "Products:\n");
    Product* currentProduct = productList;
    while (currentProduct != NULL) {
        fprintf(file, "%d,%s,%s,%d,%d\n", currentProduct->id, currentProduct->name, currentProduct->category, currentProduct->stock, currentProduct->sales);
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

// 显示管理员菜单
void showAdminMenu() {
    printf("\n管理员菜单:\n");
    printf("1. 添加产品\n");
    printf("2. 删除产品\n");
    printf("3. 修改产品\n");
    printf("4. 查询类别下的所有产品\n"); // 调整后的位置
    printf("5. 查询产品\n");                 // 原4号
    printf("6. 按销售量排序输出产品\n");       // 修改后的第6项
    printf("7. 进货管理\n");                 // 原6号
    printf("8. 销售管理\n");                 // 原7号
    printf("9. 保存数据\n");                 // 原8号
    printf("0. 退出\n");
}

// 显示仓库工作人员菜单
void showStaffMenu() {
    printf("\n仓库工作人员菜单:\n");
    printf("1. 查询产品\n");
    printf("2. 查询产品销售情况\n");
    printf("0. 退出\n");
}

// 管理员操作
void adminOperations(Product** productList, User* userList, PurchaseRecord** purchaseList, SaleRecord** saleList) {
    int choice;
    do {
        showAdminMenu();
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
            int id, stock;
            char name[MAX_NAME_LEN] = { 0 }, category[MAX_NAME_LEN] = { 0 };
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
            addProduct(productList, id, name, category, stock);
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
        case 7: { // 原6号进货管理
            int productId, quantity;
            char date[MAX_NAME_LEN] = { 0 };
            printf("请输入进货的产品ID: ");
            if (scanf("%d", &productId) != 1) { // 修改此行
                printf("输入错误!\n");
                // 清空输入缓冲区
                int ch;
                while ((ch = getchar()) != '\n' && ch != EOF);
                break;
            }
            printf("请输入进货数量: ");
            if (scanf("%d", &quantity) != 1) { // 修改此行
                printf("输入错误!\n");
                // 清空输入缓冲区
                int ch;
                while ((ch = getchar()) != '\n' && ch != EOF);
                break;
            }
            printf("请输入进货日期: ");
            if (scanf("%99s", date) != 1) { // 修改此行
                printf("输入错误!\n");
                break;
            }
            managePurchase(purchaseList, *productList, productId, quantity, date);
            break;
        }
        case 8: { // 原7号销售管理
            int productId, quantity;
            char date[MAX_NAME_LEN] = { 0 };
            printf("请输入销售的产品ID: ");
            if (scanf("%d", &productId) != 1) { // 修改此行
                printf("输入错误!\n");
                // 清空输入缓冲区
                int ch;
                while ((ch = getchar()) != '\n' && ch != EOF);
                break;
            }
            printf("请输入销售数量: ");
            if (scanf("%d", &quantity) != 1) { // 修改此行
                printf("输入错误!\n");
                // 清空输入缓冲区
                int ch;
                while ((ch = getchar()) != '\n' && ch != EOF);
                break;
            }
            printf("请输入销售日期: ");
            if (scanf("%99s", date) != 1) { // 修改此行
                printf("输入错误!\n");
                break;
            }
            manageSale(saleList, *productList, productId, quantity, date);
            break;
        }
        case 9: { // 原8号保存数据
            saveToFile(*productList, userList, *purchaseList, *saleList);
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
    int role = login(userList);
    if (role == -1) {
        printf("登录失败，程序退出。\n");
        return 0;  // 登录失败
    }

    // 根据角色进入不同的操作菜单
    if (role == 0) {
        // 管理员操作
        adminOperations(&productList, userList, &purchaseList, &saleList);
    }
    else if (role == 1) {
        // 仓库工作人员操作
        staffOperations(productList, saleList);
    }

    return 0;
}
