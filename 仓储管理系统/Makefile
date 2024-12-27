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

# ...existing code...