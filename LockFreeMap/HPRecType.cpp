#include "HPRecType.h"
#include "Util.h"
#include <set>
#include <vector>

using namespace std;

atomic<HazardPointer::Node*> HazardPointer::s_head;

thread_local std::vector<void*> _retiredList;

void HazardPointer::Retire(void* pOld) {
    _retiredList.push_back(pOld);
    if (_retiredList.size() >= 100) { // Maximum retired list size
        Scan();
    }
}

void HazardPointer::Scan() {
    // Stage 1: Scan the hazard pointers list, collecting all nonnull ptrs
    std::set<void*> hazardPointers;
    for (auto* node = s_head.load(); node != nullptr; node = node->next) {
        if (node->ptr) hazardPointers.insert(node->ptr);
    }

    // Stage 2 (sort the list) isn't required when using std::set.

    // Stage 3: Search for them!
    for (auto it = _retiredList.begin(); it != _retiredList.end(); ) {
        if (hazardPointers.find(*it) != hazardPointers.end()) {
            delete *it;
            it = _retiredList.erase(it);
        } else {
            ++it;
        }
    }
}

HazardPointer::HazardPointer() {
    // Try to reuse a retired node
    for (_node = s_head.load(); _node != nullptr; _node = _node->next) {
        if (!CAS(_node->active, false, true)) continue;
        return;
    }

    // Else, there are no free nodes, create a new one
    _node = new HazardPointer::Node();
    HazardPointer::Node* old = s_head.load();
    do {
        _node->next = old;
    } while (!CAS(s_head, old, _node));
    return;
}

HazardPointer::HazardPointer(HazardPointer&& other) noexcept {
    std::swap(_node, other._node);
}

HazardPointer::~HazardPointer() {
    if (_node) {
        _node->ptr = nullptr;
        _node->active = false;
    }
}

HazardPointer& HazardPointer::operator=(HazardPointer&& other) noexcept {
    std::swap(_node, other._node);
    return other;
}
