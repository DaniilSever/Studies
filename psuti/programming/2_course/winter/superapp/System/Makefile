.PHONY: build run rebuild clean

build:
	cmake -S . -B build -G Ninja
	cmake --build build -j$$(nproc)

run: build
	./build/superapp

rebuild: clean build

clean:
	rm -rf build
