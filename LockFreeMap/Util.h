#pragma once
#include <atomic>

template<typename T>
bool CAS(std::atomic<T>& atom, T expected, T desired) {
    return atom.compare_exchange_strong(expected, desired);
}
