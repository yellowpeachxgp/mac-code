#ifndef USER_H
#define USER_H

#define MAX_NAME_LEN 100
#define MAX_PASS_LEN 20

// Forward declarations
typedef struct Product Product;
typedef struct PurchaseRecord PurchaseRecord;
typedef struct SaleRecord SaleRecord;
typedef struct Category Category;

typedef struct User {
    char username[MAX_NAME_LEN];  // 用户名
    char password[MAX_PASS_LEN];  // 密码
    int role;                     // 0:管理员, 1:仓库工作人员
    struct User* next;            // 链表的下一个用户
} User;

// 函数声明
int login(User* userList);
void addProduct(Product** productList, int id, const char* name, const char* category, int stock);
void deleteProduct(Product** productList, int id);
void modifyProduct(Product* productList, int id);
void queryProduct(Product* productList, int id);
void querySales(Product* productList, SaleRecord* saleList, int id);
void queryByCategory(Product* productList, const char* category);
void managePurchase(PurchaseRecord** purchaseList, Product* productList, int productId, int quantity, const char* date);
void manageSale(SaleRecord** saleList, Product* productList, int productId, int quantity, const char* date);
void loadFromFile(Product** productList, User** userList, PurchaseRecord** purchaseList, SaleRecord** saleList);
void saveToFile(Product* productList, User* userList, PurchaseRecord* purchaseList, SaleRecord* saleList);
void showAdminMenu();
void showStaffMenu();
void adminOperations(Product** productList, User* userList, PurchaseRecord** purchaseList, SaleRecord** saleList);
void staffOperations(Product* productList, SaleRecord* saleList);
void displayAllProducts(Product* productList);

// ...existing code...

#endif // USER_H