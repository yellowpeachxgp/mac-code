# ...existing code...

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