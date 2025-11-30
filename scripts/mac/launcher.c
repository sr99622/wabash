#include <unistd.h>

int main(int argc, char* argv[]) {
    return execv("/Applications/wabash.app/Contents/MacOS/Python/Library/Frameworks/Python.framework/Versions/Current/env/bin/wabash", NULL);
}