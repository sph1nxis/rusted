// Theme preview
package main

import (
	"encoding/json"
	"log"
	"net/http"
	"sort"
	"sync"
)

type User struct {
	ID     uint64 `json:"id"`
	Name   string `json:"name"`
	Active bool   `json:"active"`
}
type Store struct {
	mu    sync.RWMutex
	users map[uint64]User
}

func NewStore() *Store {
	return &Store{users: make(map[uint64]User)}
}

func (s *Store) Put(user User) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.users[user.ID] = user
}

func (s *Store) List() []User {
	s.mu.RLock()
	defer s.mu.RUnlock()
	result := make([]User, 0, len(s.users))
	for _, user := range s.users {
		result = append(result, user)
	}
	sort.Slice(result, func(i, j int) bool {
		return result[i].ID < result[j].ID
	})
	return result
}

func main() {
	store := NewStore()
	store.Put(User{ID: 1, Name: "Alice", Active: true})
	store.Put(User{ID: 2, Name: "Bob", Active: false})
	http.HandleFunc("/users", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(store.List())
	})
	log.Fatal(http.ListenAndServe(":8080", nil))
}
