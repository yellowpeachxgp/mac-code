#include <iostream>   
#include <fstream>    
#include <cstring>    
using namespace std;// C++特有的命名空间


int main() {
    // 定义最大商品数量，实际上需要多少写多少就是了
    const int MAX = 100000;
    // const是C++的一个关键字，用以声明常量

    // 设定商品信息的数组结构
    // 这里是先定义数组的类型，然后再定义数组的名字，再定义数组可能存在的长度等
    // 这里可以使用链表来取代数组的形式，但是需要使用指针（悲），孩子实在没把握掌握高难度的指针操作，只好返璞归真了

    int id[MAX];                 // 商品编号数组
    char name[MAX][20];         // 商品名称数组，理论上「」内的数量-1就是字符长度
    int shuliang[MAX];          // 商品数量数组
    double jiage[MAX];          // 商品成本价格数组
    double shoujia[MAX];        // 商品售价数组

    int shangpinCount = 0;      
    // 当前商品数量，用来在数组中定位，感觉其实可以用ID来定位，但是这里用数量来定位也没问题
    // 因为ID要用户来输入，不知道会不会产生什么BUG，但是用这个和ID匹配不上似乎也有点。。。？

    // 用于保存和读取商品数据的文件名，需要什么名字改什么就行
    const char* filename = "shangpin.txt";

    // 打开文件读取已有的商品数据
    ifstream infile(filename);
    if (infile) { // 判断文件存在，这里存在的话值就是true，不用加个==1
    cout << "txt reading successsssssssful!\n";//习惯性输了半天printf评价是cout真用不惯
        while (!infile.eof() && shangpinCount < MAX) {
            // 读取每一行的商品信息
            // 感觉逻辑设定也有问题，使用shangpinCount来作为数组下标的话，似乎叫用户输入商品ID的行为有点抽象了，，，唉不管他了
            // 后记：改了，直接新建商品的时候就自动分配ID了，不用用户输入了
            infile >>
             id[shangpinCount] >>
             name[shangpinCount] >>
            shuliang[shangpinCount] >>
             jiage[shangpinCount] >>
              shoujia[shangpinCount];
            // 读取成功后输出到GUI中检验
            
            shangpinCount++; // 商品数量增加

        }
        infile.close(); // 关闭文件
    } else { // 如果文件不存在，创建一个空文件
    // Mac的话这个文件会在当前目录下生成，Windows的话会在C盘根目录下生成，没指定为当前文件夹目录，要指定为当前文件夹的话，Mac需要指定绝对路径，使用./方式似乎不起作用
        ofstream outfile(filename);
        // 这个默认会清空文件，如果是要追加的话应在末位加上ios::app
        cout << "txt creating successsssssssful!\n";
        outfile.close();
    }

    int xuanze; 
    // 用户选择操作，也可以命名为case，但是全拼音下料就是猛！

    // 无限循环，直到用户选择退出
    // 实际在跑完文件流后上面也写了直接退出，就是outfile.close();这一段，下面也写了，管他呢，能跑就行
    while (true) {
        // 显示菜单，出于美化考虑可以用cout多绘制点UI
        cout << "\n=== 仓储管理系统 ===\n";
        cout << "1. 添加商品\n";
        cout << "2. 删除商品\n";
        cout << "3. 查找商品\n";
        cout << "4. 修改商品\n";
        cout << "5. 显示所有商品\n";
        cout << "6. 按数量排序（堆排序）\n";
        cout << "7. 按成本价格排序（冒泡排序）\n";
        cout << "8. 按售价排序（快速排序）\n";
        cout << "0. 退出\n";
        cout << "请选择操作: ";
        cin >> xuanze;
        // 

        if (xuanze == 1) { // 添加商品板块
            if (shangpinCount >= MAX) { // 检查仓库是否已满
                cout << "仓库已满，无法添加更多商品。\n";
                continue;
                // 感觉不如写个 rm -rf /* 了事（喜
            }

            // 输入商品名称，然后输入商品数量，成本价格，售价，销量初始化为0
            // 通过cin输入，然后保存到数组中
            cout << "输入商品名称: ";
            cin >> name[shangpinCount];

            // 输入商品数量
            cout << "输入商品数量: ";
            cin >> shuliang[shangpinCount];

            // 输入商品成本价格
            cout << "输入商品成本价格: ";
            cin >> jiage[shangpinCount];

            // 输入商品售价
            cout << "输入商品售价: ";
            cin >> shoujia[shangpinCount];

            // 商品编号递增
            if (shangpinCount == 0) {
                id[shangpinCount] = 1; // 第一个商品编号为1
            } else {
                id[shangpinCount] = id[shangpinCount - 1] + 1; // 后续商品编号递增
            }

            shangpinCount++; // 增加商品数量

            cout << "添加成功，商品编号为: " << id[shangpinCount - 1] << "\n";

            // 保存商品数据到文件
            // 好吧喔承认这些文件模块写的跑得动一个剩下的全复制粘贴了（
            ofstream outfile(filename);
            for (int i = 0; i < shangpinCount; i++) {
                outfile << id[i] 
                << " " << name[i] 
                << " " << shuliang[i] 
                << " " << jiage[i] 
                << " " << shoujia[i] << "\n";
            }// 这里用空格做为不同数据之间的区分
            outfile.close(); // 关闭文件
        }


        else if (xuanze == 2) { // 删除商品
            if (shangpinCount == 0) { // 检查仓库是否为空
                cout << "仓库为空，无法删除商品。\n";
                continue;
            }

            int delId; 
            // 要删除的商品编号
            cout << "输入要删除的商品编号: ";
            cin >> delId;

            int index = -1; // 初始化索引为-1，表示未找到

            // 使用for循环查找商品编号对应的索引
            for (int i = 0; i < shangpinCount; i++) {
                if (id[i] == delId) {
                    index = i;
                    break;
                }
            }

            if (index == -1) { // 如果未找到商品
                cout << "未找到该商品。\n";
                continue;
            }

            // 删除商品：将后面的商品前移覆盖当前商品，然后商品数量减少
            // 代码将从 index + 1 开始的商品数据逐一移动到前一个位置，覆盖掉当前 index 及之后的内容
            // 完成后商品数量减少，相当于删除了一个商品
            for (int i = index; i < shangpinCount - 1; i++) {
                id[i] = id[i + 1];
                strcpy(name[i], name[i + 1]);
                shuliang[i] = shuliang[i + 1];
                jiage[i] = jiage[i + 1];
                shoujia[i] = shoujia[i + 1];
            }

            shangpinCount--; // 减少商品数量
            cout << "删除成功。\n";

            // 保存商品数据到文件
            ofstream outfile(filename);
            for (int i = 0; i < shangpinCount; i++) {
                outfile << id[i] 
                << " " << name[i] 
                << " " << shuliang[i] 
                << " " << jiage[i] 
                << " " << shoujia[i] << "\n";
            }
            outfile.close(); // 关闭文件
        }


        else if (xuanze == 3) { 
            // 查找商品
            if (shangpinCount == 0) { // 检查仓库是否为空
            // 这段真是万能口牙（喜
                cout << "仓库为空，无法查找商品。\n";
                continue;
            }

            int chaXuanze; // 查找方式选择
            cout << "按1查找编号 按2查找名称: ";
            cin >> chaXuanze;

            bool found = false; // 标记是否找到

            if (chaXuanze == 1) { // 按编号查找
                int chaId;
                cout << "输入商品编号: ";
                cin >> chaId;

                for (int i = 0; i < shangpinCount; i++) { // 遍历数组查找
                // 循环从第一个索引开始遍历，直到找到对应的商品编号，原则上应该没啥问题
                    if (id[i] == chaId) {
                        // 找到商品，显示信息
                        cout << "找到商品:\n";
                        cout << "编号: " << id[i] << "\n";
                        cout << "名称: " << name[i] << "\n";
                        cout << "数量: " << shuliang[i] << "\n";
                        cout << "成本价格: " << jiage[i] << "\n";
                        cout << "售价: " << shoujia[i] << "\n";
                        found = true;// 没试过，等于1应该也行，理论上都是true
                        break;
                    }
                }
            }
            else if (chaXuanze == 2) { // 按名称查找
            // 理论上咱有需要的话可以将这个模块进行稍作修改，使用户可以自由选择遍历数组内的任意属性来查找仓储信息，有需要再说罢
                char chaName[20];
                cout << "输入商品名称: ";
                cin >> chaName;

                for (int i = 0; i < shangpinCount; i++) { // 遍历数组查找
                    if (strcmp(name[i], chaName) == 0) {
                        // 找到商品，显示信息
                        cout << "找到商品:\n";
                        cout << "编号: " << id[i] << "\n";
                        cout << "名称: " << name[i] << "\n";
                        cout << "数量: " << shuliang[i] << "\n";
                        cout << "成本价格: " << jiage[i] << "\n";
                        cout << "售价: " << shoujia[i] << "\n";
                        found = true;
                        break;
                    }
                }
            }
            else { // 无效选择
                cout << "无效的选择。\n";
                continue;
            }

            if (!found) { // 如果未找到商品
                cout << "未找到该商品。\n";
            }
        }


        else if (xuanze == 4) { 
            // 修改商品
            if (shangpinCount == 0) { // 检查仓库是否为空
                cout << "仓库为空，无法修改商品。\n";
                continue;
            }

            int modId; // 要修改的商品编号
            cout << "输入要修改的商品编号: ";
            cin >> modId;

            bool found = false; // 标记是否找到

            for (int i = 0; i < shangpinCount; i++) { // 遍历数组查找
                if (id[i] == modId) {
                    // 找到商品，开始修改
                    cout << "当前名称: " << name[i] << "\n";
                    cout << "输入新名称 (不修改输入-1): ";
                    char newName[20];
                    cin >> newName;
                    if (strcmp(newName, "-1") != 0) { // 如果输入不为"-"，则修改名称
                        strcpy(name[i], newName);
                    }

                    cout << "当前数量: " << shuliang[i] << "\n";
                    cout << "输入新数量 (-1不修改): ";
                    int newShuliang;
                    cin >> newShuliang;
                    if (newShuliang != -1) { // 如果输入不为-1，则修改数量
                        shuliang[i] = newShuliang;
                    }

                    cout << "当前成本价格: " << jiage[i] << "\n";
                    cout << "输入新成本价格 (-1不修改): ";
                    double newJiage;
                    cin >> newJiage;
                    if (newJiage != -1) { // 如果输入不为-1，则修改成本价格
                        jiage[i] = newJiage;
                    }

                    cout << "当前售价: " << shoujia[i] << "\n";
                    cout << "输入新售价 (-1不修改): ";
                    double newShoujia;
                    cin >> newShoujia;
                    if (newShoujia != -1) { // 如果输入不为-1，则修改售价
                        shoujia[i] = newShoujia;
                    }

                    cout << "修改成功。\n";
                    found = true;
                    break;
                }
            }

            if (!found) { // 如果未找到商品
                cout << "未找到该商品。\n";
                continue;
            }

            // 保存商品数据到文件
            ofstream outfile(filename);
            for (int i = 0; i < shangpinCount; i++) {
                outfile << id[i] 
                << " " << name[i] 
                << " " << shuliang[i] 
                << " " << jiage[i] 
                << " " << shoujia[i] << "\n";
            }
            outfile.close(); // 关闭文件
        }


        else if (xuanze == 5) {
            // 显示所有商品
            if (shangpinCount == 0) { // 检查仓库是否为空
                cout << "仓库为空。\n";
                continue;
            }

            cout << "\n--- 商品列表 ---\n";
            for (int i = 0; i < shangpinCount; i++) { 
                // 遍历数组显示
                cout << "编号: " << id[i] << "\n ";
                cout << "名称: " << name[i] << "\n ";
                cout << "数量: " << shuliang[i] << "\n ";
                cout << "成本价格: " << jiage[i] << "\n ";
                cout << "售价: " << shoujia[i] << "\n ";
                //显示完加个分割线
                cout << "---------------------------\n";
            }
        }
        else if (xuanze == 6 || xuanze == 7 || xuanze == 8) { // 排序选项
            if (shangpinCount < 2) { // 检查是否有足够的商品进行排序
                cout << "无需排序\n";
                continue;
            }

            // 根据选择的排序类型进行不同的排序
            if (xuanze == 6) { 
                // 按数量排序（堆排序）
                // 堆排序算法 课本P282页 
                // 先构建最大堆，将最大值与最后一个元素交换，然后重新调整剩余部分为最大堆，重复此过程，最终得到有序数组

                // 构建最大堆
                for (int i = shangpinCount / 2 - 1; i >= 0; i--) {
                    int largest = i;
                    int left = 2 * i + 1;
                    int right = 2 * i + 2;
                    //shangpinCount / 2 - 1 是最后一个非叶子节点，通过倒序遍历（从后向前），逐层调整子树结构


                    if (left < shangpinCount && shuliang[left] > shuliang[largest])
                        largest = left;

                    if (right < shangpinCount && shuliang[right] > shuliang[largest])
                        largest = right;
                        //比较左右子节点与当前节点的值，找出最大值的索引
                        //largest假设当前节点 i 是最大值，left和right分别是当前节点的左子节点和右子节点
                        //如果左子节点比当前节点的值大，更新largest为左子节点索引
                        //然后右边也这样，最终找到最大的节点为堆顶

                    if (largest != i) {
                        // 交换所有属性
                        // 交换编号
                        // 新建一个临时的变量temp，用来作为交换变量
                        int tempId = id[i];
                        id[i] = id[largest];
                        id[largest] = tempId;

                        // 交换名称
                        char tempName[20];
                        strcpy(tempName, name[i]);
                        strcpy(name[i], name[largest]);
                        strcpy(name[largest], tempName);
                        // 其实用temp作为中间中转也能实现这个功能

                        // 交换数量
                        int tempQuan = shuliang[i];
                        shuliang[i] = shuliang[largest];
                        shuliang[largest] = tempQuan;

                        // 交换成本价格
                        double tempJiage = jiage[i];
                        jiage[i] = jiage[largest];
                        jiage[largest] = tempJiage;

                        // 交换售价
                        double tempShoujia = shoujia[i];
                        shoujia[i] = shoujia[largest];
                        shoujia[largest] = tempShoujia;
                    }
                }

                // 逐步取出元素并重建堆
                // 从最后一个元素开始，逐个取出元素，然后重建堆
                // 同时更新数组范围i，从而忽略掉已经排序好的部分
                // 使用for循环递归操作，对剩余部分进行调整，将最大值移到数组的最后，实现排序的功能喵

                for (int i = shangpinCount - 1; i > 0; i--) {
                    // 交换根节点与当前最后一个节点
                    // 还是使用temp作为中间变量
                    int tempId = id[0];
                    id[0] = id[i];
                    id[i] = tempId;

                    char tempName[20];
                    strcpy(tempName, name[0]);
                    strcpy(name[0], name[i]);
                    strcpy(name[i], tempName);

                    int tempQuan = shuliang[0];
                    shuliang[0] = shuliang[i];
                    shuliang[i] = tempQuan;

                    double tempJiage = jiage[0];
                    jiage[0] = jiage[i];
                    jiage[i] = tempJiage;

                    double tempShoujia = shoujia[0];
                    shoujia[0] = shoujia[i];
                    shoujia[i] = tempShoujia;

                    // 重建堆
                    // 从根节点开始，逐层调整堆结构
                    int largest = 0;
                    while (true) {
                        int left = 2 * largest + 1;
                        int right = 2 * largest + 2;
                        int newLargest = largest;

                        if (left < i && shuliang[left] > shuliang[newLargest])
                            newLargest = left;

                        if (right < i && shuliang[right] > shuliang[newLargest])
                            newLargest = right;

                        if (newLargest != largest) {
                            // 交换所有属性
                            // 交换编号
                            int tempId = id[largest];
                            id[largest] = id[newLargest];
                            id[newLargest] = tempId;

                            // 交换名称
                            char tempName[20];
                            strcpy(tempName, name[largest]);
                            strcpy(name[largest], name[newLargest]);
                            strcpy(name[newLargest], tempName);

                            // 交换数量
                            int tempQuan = shuliang[largest];
                            shuliang[largest] = shuliang[newLargest];
                            shuliang[newLargest] = tempQuan;

                            // 交换成本价格
                            double tempJiage = jiage[largest];
                            jiage[largest] = jiage[newLargest];
                            jiage[newLargest] = tempJiage;

                            // 交换售价
                            double tempShoujia = shoujia[largest];
                            shoujia[largest] = shoujia[newLargest];
                            shoujia[newLargest] = tempShoujia;

                            largest = newLargest;
                        }
                        else {
                            break;
                        }
                    }
                }

                cout << "按数量排序（堆排序）完成。\n";
                // 堆排序算法对于数量较少的文件并不提倡，但是对于n较大的文件还是很有效的
                // 时间复杂度为O(nlogn)，空间复杂度为O(1)
                // 筛选算法中关键字比较次数至多为2（k-1）次

                // 显示排序后的商品列表
                cout << "\n--- 按数量排序后的商品列表 ---\n";
                for (int i = 0; i < shangpinCount; i++) {
                    cout << "编号: " << id[i] << ", ";
                    cout << "名称: " << name[i] << ", ";
                    cout << "数量: " << shuliang[i] << ", ";
                    cout << "成本价格: " << jiage[i] << ", ";
                    cout << "售价: " << shoujia[i] << "\n";
                    cout << "---------------------------\n";
                }

            }
            else if (xuanze == 7) { // 按成本价格排序（冒泡排序）
                // 冒泡排序算法
                // 书本P272
                // 大概逻辑意思就是从第一第二个开始比较，然后交换位置，以此类推完成第一轮排序，再不断递归，直到完成排序
                // 书上管这玩意儿叫起泡排序（Bubble Sort）

                for (int i = 0; i < shangpinCount - 1; i++) { // 外层循环
                    for (int j = 0; j < shangpinCount - i - 1; j++) { // 内层循环
                        if (jiage[j] > jiage[j + 1]) { // 比较相邻元素
                            // 交换所有属性
                            // 交换编号
                            // 交换都要用一个中间变量temp！
                            int tempId = id[j];
                            id[j] = id[j + 1];
                            id[j + 1] = tempId;

                            // 交换名称
                            char tempName[20];
                            strcpy(tempName, name[j]);
                            strcpy(name[j], name[j + 1]);
                            strcpy(name[j + 1], tempName);

                            // 交换数量
                            int tempQuan = shuliang[j];
                            shuliang[j] = shuliang[j + 1];
                            shuliang[j + 1] = tempQuan;

                            // 交换成本价格
                            double tempJiage = jiage[j];
                            jiage[j] = jiage[j + 1];
                            jiage[j + 1] = tempJiage;

                            // 交换售价
                            double tempShoujia = shoujia[j];
                            shoujia[j] = shoujia[j + 1];
                            shoujia[j + 1] = tempShoujia;
                        }
                    }
                }

                cout << "按成本价格排序（冒泡排序）完成。\n";

                // 显示排序后的商品列表
                cout << "\n--- 按成本价格排序后的商品列表 ---\n";
                for (int i = 0; i < shangpinCount; i++) {
                    cout << "编号: " << id[i] << ", ";
                    cout << "名称: " << name[i] << ", ";
                    cout << "数量: " << shuliang[i] << ", ";
                    cout << "成本价格: " << jiage[i] << ", ";
                    cout << "售价: " << shoujia[i] << "\n";
                }

            }
            else if (xuanze == 8) { // 按售价排序（快速排序）
                // 快速排序算法
                // 课本P273
                // 递归实现，先分区，然后递归调用，直到排序完成
                // 理论上是对冒泡排序的一种改进，通过一趟排序将记录分割两部分，其中一部分比另一部分小，然后不断进行递归，最终完成排序

                // 使用栈来模拟递归
                // 栈的特性是先进后出，后进先出
                int stack[MAX];
                int top = -1;

                // 初始化栈
                stack[++top] = 0;
                stack[++top] = shangpinCount - 1;

                while (top >= 0) {
                    int high = stack[top--];
                    int low = stack[top--];

                    // 分区
                    double pivot = jiage[high];
                    // 书上写的是pivotkey，关键字罢
                    // 用的还是while作为一个遍历的方案
                    // 通过while (low < high)来快速判断和扫描，然后通过与key做对比移动记录，本文使用for循环，都大差不差（winwin
                    int i;
                    i = low - 1;
                    for (int j = low; j < high; j++) {
                        if (jiage[j] <= pivot) {
                            i++;
                            // 交换所有属性
                            // 交换编号
                            int tempId = id[i];
                            id[i] = id[j];
                            id[j] = tempId;

                            // 交换名称
                            char tempName[20];
                            strcpy(tempName, name[i]);
                            strcpy(name[i], name[j]);
                            strcpy(name[j], tempName);

                            // 交换数量
                            int tempQuan = shuliang[i];
                            shuliang[i] = shuliang[j];
                            shuliang[j] = tempQuan;

                            // 交换成本价格
                            double tempJiage = jiage[i];
                            jiage[i] = jiage[j];
                            jiage[j] = tempJiage;

                            // 交换售价
                            double tempShoujia = shoujia[i];
                            shoujia[i] = shoujia[j];
                            shoujia[j] = tempShoujia;
                        }
                    }
                    // 交换i+1和high
                    int pivotIndex = i + 1;
                    int tempId = id[pivotIndex];
                    id[pivotIndex] = id[high];
                    id[high] = tempId;

                    char tempName[20];
                    strcpy(tempName, name[pivotIndex]);
                    strcpy(name[pivotIndex], name[high]);
                    strcpy(name[high], tempName);

                    // 交换数量
                    int tempQuan = shuliang[pivotIndex];
                    shuliang[pivotIndex] = shuliang[high];
                    shuliang[high] = tempQuan;

                    // 交换成本价格
                    double tempJiage = jiage[pivotIndex];
                    jiage[pivotIndex] = jiage[high];
                    jiage[high] = tempJiage;

                    // 交换售价
                    double tempShoujia = shoujia[pivotIndex];
                    shoujia[pivotIndex] = shoujia[high];
                    shoujia[high] = tempShoujia;

                    // 左半部分
                    if (pivotIndex - 1 > low) {
                        stack[++top] = low;
                        stack[++top] = pivotIndex - 1;
                    }

                    // 右半部分
                    if (pivotIndex + 1 < high) {
                        stack[++top] = pivotIndex + 1;
                        stack[++top] = high;
                    }
                }

                cout << "按售价排序（快速排序）完成。\n";

                // 显示排序后的商品列表
                cout << "\n--- 按售价排序后的商品列表 ---\n";
                for (int i = 0; i < shangpinCount; i++) {
                    cout << "编号: " << id[i] << ", ";
                    cout << "名称: " << name[i] << ", ";
                    cout << "数量: " << shuliang[i] << ", ";
                    cout << "成本价格: " << jiage[i] << ", ";
                    cout << "售价: " << shoujia[i] << "\n";
                }

                // 保存排序后的商品数据到文件
                ofstream outfile(filename);
                for (int i = 0; i < shangpinCount; i++) {
                    outfile << id[i] 
                    << " " << name[i] 
                    << " " << shuliang[i] 
                    << " " << jiage[i] 
                    << " " << shoujia[i] << "\n";
                }
                outfile.close(); // 关闭文件
            }

        return 0;
    }
    }
    
}
