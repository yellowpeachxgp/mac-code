#ifndef USER_H
#define USER_H

#define MAX_NAME_LEN 100
#define MAX_PASS_LEN 20

// 文件用途: 定义用户结构体, 包含用户名/密码/角色等信息
// 主要知识点: 结构体定义, 字符数组管理, 指针链表

// Forward declarations
typedef struct Product Product;
typedef struct PurchaseRecord PurchaseRecord;
typedef struct SaleRecord SaleRecord;
typedef struct Category Category;

// 新增注释：
// 1. 这里定义了 User 结构体，包含用户名、密码、角色等信息。
// 2. 用 struct User* next 实现链表链接，让多个用户首尾相连，便于在内存中动态创建或删除用户。
// 3. 注意在函数中需要使用动态内存分配 (malloc 或 new) 来创建新的 User 结构体。

// 新增一个枚举类型，定义管理员与工作人员两种角色
enum Role {
    ROLE_ADMIN = 0,
    ROLE_STAFF = 1
};

typedef struct User {
    char username[MAX_NAME_LEN];  // 用户名
    char password[MAX_PASS_LEN];  // 密码
    int role;                     // 0:管理员, 1:仓库工作人员
    struct User* next;            // 链表的下一个用户
} User;

// 函数声明
User* login(User* users);
void addProduct(Product** productList, int id, const char* name, const char* category, int stock);
void deleteProduct(Product** productList, int id);
void modifyProduct(Product* productList, int id);
void queryProduct(Product* productList, int id);
void querySales(Product* productList, SaleRecord* saleList, int id);
void queryByCategory(Product* productList, const char* category);
void managePurchase(PurchaseRecord** purchaseList, Product* productList, int productId, int quantity, const char* date);
void manageSale(SaleRecord** saleList, Product* productList, int productId, int quantity, const char* date);
void loadFromFile(Product** productList, User** users, PurchaseRecord** purchaseList, SaleRecord** saleList);
void saveToFile(Product* productList, User* users, PurchaseRecord* purchaseList, SaleRecord* saleList);
void showAdminMenu();
void showStaffMenu();
void adminOperations(Product** productList, User* users, PurchaseRecord** purchaseList, SaleRecord** saleList);
void staffOperations(Product* productList, SaleRecord* saleList);
void displayAllProducts(Product* productList);

// 新增以下函数原型
void displayUserInfo(User* currentUser);
void manageUserAccounts(User** users);
void modifyAdminPassword(User* currentUser);
void displayAdminInfo(User* currentUser);
void displayAllUsers(User* users);

// ...existing code...

#endif // USER_H