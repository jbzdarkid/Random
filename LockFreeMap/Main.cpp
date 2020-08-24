#include "WRRMMap.h"
#include <thread>
#include <string>
#include <mutex>
#include <iostream>
#include <vector>
#include "Windows.h"

using namespace std;

int N = 100;

int main() {
    WRRMMap<int, wstring> map;

    vector<thread> threads;
    for (int i=0; i<N; i++) {
        threads.push_back(thread([&map, i]{
            this_thread::sleep_for(chrono::milliseconds(10 + rand() % 10));
            map.Update(i, L"Value " + to_wstring(i));
        }));
    }
    for (auto& thread : threads) thread.join();
    wstring mapSize = std::to_wstring(map.Size()) + L'\n';
    OutputDebugString(mapSize.c_str());

    wstring totalOutput;
    mutex outputMutex;

    threads.clear();
    for (int i=0; i<N; i++) {
        threads.push_back(thread([&outputMutex, &totalOutput, &map, i]{
            this_thread::sleep_for(chrono::milliseconds(100 + rand() % 1000));
            wstring output = to_wstring(i) + L": ";

            wstring value;
            if (map.Lookup(i, value)) {
                output += value;
            } else {
                output += L"Not found";
            }
            lock_guard<mutex> l(outputMutex);
            totalOutput += output + L'\n';
        }));
    }
    for (auto& thread : threads) thread.join();
    OutputDebugString(totalOutput.c_str());

    map.Clear();
    mapSize = std::to_wstring(map.Size()) + L'\n';
    OutputDebugString(mapSize.c_str());

}
