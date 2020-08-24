#include "WRRMMap.h"
#include <thread>
#include <string>
#include <mutex>
#include <iostream>
#include <vector>
#include "Windows.h"

using namespace std;

int main() {
    WRRMMap<int, string> map;

    vector<thread> threads;
    for (int i=0; i<100; i++) {
        threads.push_back(thread([&map, i]{
            this_thread::sleep_for(chrono::milliseconds(10 + rand() % 10));
            map.Update(i, "Value " + to_string(i));
        }));
    }
    for (auto& thread : threads) thread.join();
    wstring mapSize = std::to_wstring(map.Size()) + L'\n';
    OutputDebugString(mapSize.c_str());

    string totalOutput;
    mutex outputMutex;

    threads.clear();
    for (int i=0; i<100; i++) {
        threads.push_back(thread([&outputMutex, &totalOutput, &map, i]{
            this_thread::sleep_for(chrono::milliseconds(100 + rand() % 1000));
            string output = to_string(i) + ": ";

            string value;
            if (map.Lookup(i, value)) {
                output += value;
            } else {
                output += "Not found";
            }
            lock_guard<mutex> l(outputMutex);
            totalOutput += output + "\n";
        }));
    }
    for (auto& thread : threads) thread.join();
    OutputDebugStringA(totalOutput.c_str());
}
