// Theme preview
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_USERS 8

typedef struct {
    uint64_t id;
    char name[32];
    int active;
} User;

typedef struct {
    User items[MAX_USERS];
    size_t count;
} Database;

static int add(Database *db, uint64_t id, const char *name, int active)
{
    if (db->count >= MAX_USERS || !name)
        return -1;
    User *user = &db->items[db->count++];
    user->id = id;
    user->active = active;
    snprintf(user->name, sizeof(user->name), "%s", name);
    return 0;
}

static User *find(Database *db, uint64_t id)
{
    for (size_t i = 0; i < db->count; ++i)
        if (db->items[i].id == id)
            return &db->items[i];
    return NULL;
}

int main(void)
{
    Database db = {0};
    add(&db, 1, "Alice", 1);
    add(&db, 2, "Bob", 0);
    add(&db, 3, "Carol", 1);
    User *user = find(&db, 1);
    if (user)
        user->active = 0;
    printf("count=%zu\n", db.count);
    return EXIT_SUCCESS;
}
