# ...existing code...

CC = gcc
CFLAGS = -Wall -g

# 只保留项目中真正存在的 .cpp 文件
SRCS = 仓储管理系统.cpp UserControl.cpp
OBJS = $(SRCS:.cpp=.o)
TARGET = 仓储管理系统

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS)

%.o: %.cpp
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

# ...existing code...