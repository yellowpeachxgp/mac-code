// 文件用途: 声明或控制与用户管理相关的函数
// 主要知识点: 函数原型, C/C++头文件的使用, 头文件保护

#ifndef USERCONTROL_H
#define USERCONTROL_H

// 新增注释：
// 1. 此头文件主要申明了对用户的控制操作函数，如显示、修改以及管理账户等。
// 2. 使用了函数原型声明的方式，让用户控制的实现可以在对应的 .cpp 文件中实现，从而体现了头文件和实现文件的分离。
// 3. 大部分涉及指针参数 (User**) 是为了在函数中可以修改指向的链表头指针，运用了 C++ 函数传参机制。

void UserModule_manageAccounts(User** users);
void UserModule_modifyAdminPassword(User* currentUser);
void UserModule_displayInfo(User* currentUser);
void UserModule_displayAll(User* users);

#endif // USERCONTROL_H