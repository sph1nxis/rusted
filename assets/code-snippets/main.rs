// Theme preview
use std::collections::HashMap;

#[derive(Clone, Debug)]
struct User {
    id: u64,
    name: String,
    active: bool,
}

enum Command {
    Create(User),
    Rename(u64, String),
    Remove(u64),
    Toggle(u64),
}

fn process(command: Command, users: &mut HashMap<u64, User>) {
    match command {
        Command::Create(user) => { users.insert(user.id, user); }
        Command::Rename(id, name) => {
            if let Some(user) = users.get_mut(&id) {
                user.name = name;
            }
        }
        Command::Remove(id) => { users.remove(&id); }
        Command::Toggle(id) => {
            if let Some(user) = users.get_mut(&id) {
                user.active = !user.active;
            }
        }
    }
}

fn main() {
    let mut users = HashMap::new();
    process(Command::Create(User { id: 1, name: "Alice".into(), active: true }), &mut users);
    process(Command::Create(User { id: 2, name: "Bob".into(), active: false }), &mut users);
    process(Command::Rename(1, "Alice Cooper".into()), &mut users);
    process(Command::Toggle(2), &mut users);
    for user in users.values() {
        println!("{user:?}");
    }
}
