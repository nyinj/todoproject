document.addEventListener('DOMContentLoaded', () => {
  getTasks();

  // attach logout handler if button present
  const logoutButton = document.querySelector('.logout-button');
  if (logoutButton) {
    logoutButton.addEventListener('click', () => doLogout());
  }

  // add listeners
  const todoButton = document.querySelector('.todo-button');
  const todoList = document.querySelector('.todo-list');
  const filterSelect = document.querySelector('.filter-todo');
  const clearAllBtn = document.querySelector('.clear-all-btn');

  if (todoButton) todoButton.addEventListener('click', addTodo);
  if (todoList) todoList.addEventListener('click', deleteCheck);
  if (filterSelect) filterSelect.addEventListener('change', filterTodos);
  if (clearAllBtn) clearAllBtn.addEventListener('click', clearAllTodos);
});

/* -------------------- AUTH HELPERS -------------------- */
function getAccessToken() {
  return localStorage.getItem('access_token');
}

function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

async function apiFetch(url, options = {}) {
  const token = getAccessToken();
  options.headers = options.headers || {};
  if (token) options.headers['Authorization'] = 'Bearer ' + token;

  const res = await fetch(url, options);
  if (res.status === 401) {
    clearTokens();
    window.location.href = '/login/';
    return;
  }
  return res;
}

/* -------------------- TODO LOGIC -------------------- */
const todoInput = document.querySelector('.todo-input');
const todoList = document.querySelector('.todo-list');

async function getTasks() {
  const res = await apiFetch('/api/tasks/');
  if (!res) return;
  const tasks = await res.json();

  todoList.innerHTML = '';
  tasks.forEach(createTodoElement);
  updateCounters();
}

function createTodoElement(task) {
  const todoDiv = document.createElement('div');
  todoDiv.classList.add('todo');
  todoDiv.dataset.id = task.id;
  if (task.completed) todoDiv.classList.add('completed');

  const newTodo = document.createElement('li');
  newTodo.innerText = task.title;
  newTodo.classList.add('todo-item');
  todoDiv.appendChild(newTodo);

  const completedButton = document.createElement('button');
  completedButton.innerHTML = '<i class="fas fa-check-circle"></i>';
  completedButton.classList.add('complete-btn');
  todoDiv.appendChild(completedButton);

  const trashButton = document.createElement('button');
  trashButton.innerHTML = '<i class="fas fa-trash"></i>';
  trashButton.classList.add('trash-btn');
  todoDiv.appendChild(trashButton);

  todoList.appendChild(todoDiv);
}

async function addTodo(e) {
  e.preventDefault();
  const value = todoInput.value.trim();
  if (!value) {
    alert('Please enter a task.');
    return;
  }

  const res = await apiFetch('/api/tasks/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: value })
  });

  if (res && res.ok) {
    const task = await res.json();
    createTodoElement(task);
    todoInput.value = '';
    updateCounters();
  } else {
    console.error('Failed to create task', res && await res.text());
  }
}

async function deleteCheck(e) {
  const button = e.target.closest('button');
  if (!button) return;

  const todo = button.parentElement;
  const id = todo.dataset.id;

  if (button.classList.contains('trash-btn')) {
    const res = await apiFetch(`/api/tasks/${id}/`, { method: 'DELETE' });
    if (res && (res.ok || res.status === 204)) {
      todo.classList.add('slide');
      todo.addEventListener('transitionend', () => {
        todo.remove();
        updateCounters();
      });
    } else {
      console.error('Failed to delete', res && await res.text());
    }
  }

  if (button.classList.contains('complete-btn')) {
    const completed = todo.classList.toggle('completed');
    await apiFetch(`/api/tasks/${id}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed })
    });
    updateCounters();
  }
}

/* -------------------- FILTERING -------------------- */
function filterTodos(e) {
  const filter = e.target.value;
  const todos = document.querySelectorAll('.todo');

  todos.forEach(todo => {
    switch (filter) {
      case 'all':
        todo.style.display = 'flex';
        break;
      case 'completed':
        todo.style.display = todo.classList.contains('completed') ? 'flex' : 'none';
        break;
      case 'incomplete':
        todo.style.display = !todo.classList.contains('completed') ? 'flex' : 'none';
        break;
    }
  });
}

/* -------------------- CLEAR ALL -------------------- */
async function clearAllTodos() {
  const todos = document.querySelectorAll('.todo');
  for (const todo of todos) {
    const id = todo.dataset.id;
    await apiFetch(`/api/tasks/${id}/`, { method: 'DELETE' });
  }
  todoList.innerHTML = '';
  updateCounters();
}

/* -------------------- LOGOUT -------------------- */
function doLogout() {
  clearTokens();
  window.location.href = '/login/';
}

/* -------------------- COUNTER -------------------- */
function updateCounters() {
  const total = document.querySelectorAll('.todo').length;
  const completed = document.querySelectorAll('.todo.completed').length;
  const uncompleted = total - completed;

  const completedCounter = document.getElementById('completed-counter');
  const uncompletedCounter = document.getElementById('uncompleted-counter');

  if (completedCounter && uncompletedCounter) {
    completedCounter.innerText = completed;
    uncompletedCounter.innerText = uncompleted;
  }
}
