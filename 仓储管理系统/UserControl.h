#ifndef USERCONTROL_H
#define USERCONTROL_H

#include "User.h"

// 显示当前管理员的账户信息
void displayAdminInfo(User* currentUser);

// 修改当前管理员的密码
void modifyAdminPassword(User* currentUser);

// 管理用户账户
void manageUserAccounts(User** userList);

void displayUserInfo(User* currentUser);

void displayAllUsers(User* userList);

#endif // USERCONTROL_H