# 添加解释性注释:
# CXX: 指定C++编译器
# CXXFLAGS: 指定编译选项(版本/警告等)
# SRCS, OBJS, TARGET: 表示源文件列表、目标文件和最终可执行文件名

CXX = g++
CXXFLAGS = -std=c++11 -Wall

SRCS = \
	仓储管理系统.cpp

OBJS = $(SRCS:.cpp=.o)

TARGET = 仓储管理系统

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $<

clean:
	rm -f $(OBJS) $(TARGET)

# 建议在编译时分别编译各模块(.cpp/.h)文件，以支持更好的模块化管理

# 新增注释：
# 1. 此 Makefile 通过指定编译目标 (如 main 可执行文件) 来管理多文件编译依赖。
# 2. 常用规则：目标: 依赖项
#              <TAB> 执行命令
# 3. 便于在较大型项目中自动化编译与链接，通过在命令行执行 make 命令实现在 Linux/Unix 环境下的快速构建。