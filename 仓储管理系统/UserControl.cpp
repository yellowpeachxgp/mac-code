#include "UserControl.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 显示当前管理员的账户信息
void displayAdminInfo(User* currentUser) {
    printf("------ 管理员账户信息 ------\n");
    printf("用户名: %s\n", currentUser->username);
    printf("角色: %s\n", currentUser->role == 0 ? "管理员" : "仓库工作人员");
    printf("------------------------------\n");
}

void displayUserInfo(User* currentUser) {
    printf("\n------ 当前用户信息 ------\n");
    printf("用户名: %s\n", currentUser->username);
    printf("角色: %s\n", (currentUser->role == 0) ? "管理员" : "仓库工作人员");
    printf("--------------------------\n");
}

void displayAllUsers(User* userList) {
    printf("\n------ 系统所有用户信息 ------\n");
    User* current = userList;
    while (current != NULL) {
        printf("用户名: %s, 角色: %s\n",
               current->username,
               (current->role == 0) ? "管理员" : "仓库工作人员");
        current = current->next;
    }
    printf("--------------------------------\n");
}

// 修改当前管理员的密码
void modifyAdminPassword(User* currentUser) {
    char newPassword[MAX_PASS_LEN] = {0};
    printf("请输入新密码: ");
    if (scanf("%19s", newPassword) != 1) { // 修改此行
        printf("密码输入失败!\n");
        return;
    }
    strncpy(currentUser->password, newPassword, MAX_PASS_LEN - 1);
    currentUser->password[MAX_PASS_LEN - 1] = '\0';
    printf("密码修改成功!\n");
}

// 管理用户账户
void manageUserAccounts(User** userList) {
    int choice;
    do {
        printf("\n---- 用户账户管理 ----\n");
        printf("1. 添加用户\n");
        printf("2. 删除用户\n");
        printf("3. 修改用户密码\n");
        printf("0. 返回主菜单\n");
        printf("请选择操作: ");
        if (scanf("%d", &choice) != 1) { // 修改此行
            printf("输入错误!\n");
            // 清空输入缓冲区
            int ch;
            while ((ch = getchar()) != '\n' && ch != EOF);
            choice = -1; // 设置为无效选项
            continue;
        }

        switch (choice) {
            case 1: { // 添加用户
                char username[MAX_NAME_LEN] = {0}, password[MAX_PASS_LEN] = {0};
                int role;
                printf("请输入新用户的用户名: ");
                if (scanf("%99s", username) != 1) { // 修改此行
                    printf("输入错误!\n");
                    break;
                }
                printf("请输入新用户的密码: ");
                if (scanf("%19s", password) != 1) { // 修改此行
                    printf("输入错误!\n");
                    break;
                }
                printf("请输入用户角色 (0: 管理员, 1: 仓库工作人员): ");
                if (scanf("%d", &role) != 1) { // 修改此行
                    printf("输入错误!\n");
                    // 清空输入缓冲区
                    int ch;
                    while ((ch = getchar()) != '\n' && ch != EOF);
                    break;
                }
                // 检查用户名是否已存在
                User* current = *userList;
                int exists = 0;
                while (current != NULL) {
                    if (strcmp(current->username, username) == 0) {
                        exists = 1;
                        break;
                    }
                    current = current->next;
                }
                if (exists) {
                    printf("用户名已存在，无法添加!\n");
                    break;
                }
                // 添加新用户
                User* newUser = (User*)malloc(sizeof(User));
                if (newUser == NULL) {
                    printf("内存分配失败!\n");
                    break;
                }
                strncpy(newUser->username, username, MAX_NAME_LEN - 1);
                newUser->username[MAX_NAME_LEN - 1] = '\0';
                strncpy(newUser->password, password, MAX_PASS_LEN - 1);
                newUser->password[MAX_PASS_LEN - 1] = '\0';
                newUser->role = role;
                newUser->next = *userList;
                *userList = newUser;
                printf("用户 '%s' 添加成功!\n", username);
                break;
            }
            case 2: { // 删除用户
                char username[MAX_NAME_LEN] = {0};
                printf("请输入要删除的用户名: ");
                if (scanf("%99s", username) != 1) { // 修改此行
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
                        printf("用户 '%s' 删除成功!\n", username);
                        break;
                    }
                    previous = current;
                    current = current->next;
                }
                if (current == NULL) {
                    printf("未找到用户名为 '%s' 的用户!\n", username);
                }
                break;
            }
            case 3: { // 修改用户密码
                char username[MAX_NAME_LEN] = {0}, newPassword[MAX_PASS_LEN] = {0};
                printf("请输入要修改密码的用户名: ");
                if (scanf("%99s", username) != 1) { // 修改此行
                    printf("输入错误!\n");
                    break;
                }
                printf("请输入新密码: ");
                if (scanf("%19s", newPassword) != 1) { // 修改此行
                    printf("输入错误!\n");
                    break;
                }
                User* current = *userList;
                while (current != NULL) {
                    if (strcmp(current->username, username) == 0) {
                        strncpy(current->password, newPassword, MAX_PASS_LEN - 1);
                        current->password[MAX_PASS_LEN - 1] = '\0';
                        printf("用户 '%s' 的密码修改成功!\n", username);
                        break;
                    }
                    current = current->next;
                }
                if (current == NULL) {
                    printf("未找到用户名为 '%s' 的用户!\n", username);
                }
                break;
            }
            case 0:
                printf("返回主菜单!\n");
                break;
            default:
                printf("无效选项，请重新输入!\n");
        }
    } while (choice != 0);
}