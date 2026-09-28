// Theme preview
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>

struct User {
    std::uint64_t id;
    std::string name;
    bool active;

    auto operator<=>(const User&) const = default;
};

class Repository {
public:
    bool insert(User user) {
        return users_.emplace(user.id, std::move(user)).second;
    }

    User* find(std::uint64_t id) {
        auto it = users_.find(id);
        return it == users_.end() ? nullptr : &it->second;
    }

    std::vector<User> active() const {
        std::vector<User> result;
        for (const auto& [id, user] : users_) {
            if (user.active)
                result.push_back(user);
        }
        return result;
    }

private:
    std::unordered_map<std::uint64_t, User> users_;
};

int main() {
    Repository repository;
    repository.insert({1, "Alice", true});
    repository.insert({2, "Bob", false});
    repository.insert({3, "Carol", true});

    if (auto* user = repository.find(1))
        user->name = "Alice Cooper";

    for (const auto& user : repository.active())
        std::cout << user.id << ": " << user.name << '\n';
}