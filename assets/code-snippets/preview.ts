// Theme preview
type UserId = number;
type Status = "active" | "inactive" | "blocked";

interface User {
    id: UserId;
    name: string;
    status: Status;
    tags: string[];
}

class Repository<T extends { id: UserId }> {
    private readonly users = new Map<UserId, T>();

    add(user: T): void {
        if (this.users.has(user.id))
            throw new Error(`duplicate id: ${user.id}`);
        this.users.set(user.id, user);
    }

    get(id: UserId): T | undefined {
        return this.users.get(id);
    }

    filter(predicate: (user: T) => boolean): T[] {
        return [...this.users.values()].filter(predicate);
    }
}

async function loadUser(id: UserId): Promise<User> {
    await new Promise(resolve => setTimeout(resolve, 10));
    return {
        id,
        name: id === 1 ? "Alice" : "Unknown",
        status: "active",
        tags: ["typescript", "linux"],
    };
}

const repository = new Repository<User>();

repository.add({ id: 1, name: "Alice", status: "active", tags: ["admin"] });
repository.add({ id: 2, name: "Bob", status: "inactive", tags: ["guest"] });
repository.add({ id: 3, name: "Carol", status: "blocked", tags: ["security"] });

const active = repository.filter(user => user.status === "active");
const names = active.map(user => user.name);
console.log(JSON.stringify({ active, names }, null, 2));