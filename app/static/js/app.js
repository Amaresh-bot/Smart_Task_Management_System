/* ==========================================================================
   Smart Task Manager - Frontend Controller
   Integrates REST APIs, AJAX Form Handling, and Real-time Socket.IO Sync
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {
    // ---------------------------------------------------------
    // 1. Global Setup & State Management
    // ---------------------------------------------------------
    let socket = null;
    const isDashboard = document.getElementById("tasks-container") !== null;

    // Initialize Socket.IO connection if user is logged in
    // (Jinja2 loads socketio library in base.html)
    if (typeof io !== "undefined") {
        socket = io();
        
        // Setup WebSockets event listeners for real-time dashboard updates
        if (socket && isDashboard) {
            socket.on("connect", () => {
                console.log("Connected to WebSocket sync server");
            });

            socket.on("task_event", (data) => {
                console.log("WebSocket event received:", data);
                // Dynamically sync dashboard tasks and statistics on change events
                fetchTasks(); 
                showToastNotification(data);
            });
        }
    }

    // ---------------------------------------------------------
    // 2. Authentication Form Handling (AJAX)
    // ---------------------------------------------------------
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const alertDiv = document.getElementById("auth-alert");
    const alertMsg = document.getElementById("auth-alert-message");

    function showAuthAlert(message, isSuccess = false) {
        if (!alertDiv || !alertMsg) return;
        alertMsg.innerText = message;
        alertDiv.className = `alert ${isSuccess ? "alert-success" : "alert-danger"} animate-fade-in`;
        alertDiv.classList.remove("d-none");
    }

    // Login Submission Handler
    if (loginForm) {
        loginForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const submitBtn = document.getElementById("login-submit-btn");
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Authenticating...`;

            const formData = new FormData(loginForm);
            const payload = Object.fromEntries(formData.entries());

            fetch(loginForm.action, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    showAuthAlert(data.message, true);
                    // Redirect to dashboard on successful login
                    setTimeout(() => {
                        window.location.href = "/dashboard";
                    }, 800);
                } else {
                    showAuthAlert(data.message || "Invalid credentials. Please try again.");
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = `<span>Log In</span><i class="fa-solid fa-arrow-right animate-arrow"></i>`;
                }
            })
            .catch(err => {
                console.error("Login error:", err);
                showAuthAlert("An error occurred. Check server connection.");
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<span>Log In</span><i class="fa-solid fa-arrow-right animate-arrow"></i>`;
            });
        });
    }

    // Registration Submission Handler
    if (registerForm) {
        registerForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirm-password").value;

            if (password !== confirmPassword) {
                showAuthAlert("Passwords do not match!");
                return;
            }

            const submitBtn = document.getElementById("register-submit-btn");
            submitBtn.disabled = true;
            submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Registering...`;

            const formData = new FormData(registerForm);
            const payload = Object.fromEntries(formData.entries());

            fetch(registerForm.action, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    showAuthAlert(data.message, true);
                    // Redirect to login page on successful registration
                    setTimeout(() => {
                        window.location.href = "/login";
                    }, 1500);
                } else {
                    showAuthAlert(data.message || "Registration failed. Try again.");
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = `<span>Create Account</span><i class="fa-solid fa-arrow-right animate-arrow"></i>`;
                }
            })
            .catch(err => {
                console.error("Register error:", err);
                showAuthAlert("An error occurred. Check server connection.");
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<span>Create Account</span><i class="fa-solid fa-arrow-right animate-arrow"></i>`;
            });
        });
    }

    // ---------------------------------------------------------
    // 3. Task Management Section (Dashboard AJAX Operations)
    // ---------------------------------------------------------
    if (isDashboard) {
        const tasksContainer = document.getElementById("tasks-container");
        const addTaskForm = document.getElementById("add-task-form");
        const editTaskForm = document.getElementById("edit-task-form");

        // Filter Elements
        const filterSearch = document.getElementById("filter-search");
        const filterStatus = document.getElementById("filter-status");
        const filterPriority = document.getElementById("filter-priority");
        const resetFiltersBtn = document.getElementById("btn-reset-filters");

        // Initial task retrieve
        fetchTasks();

        // ---------------------------------------------
        // Fetch and Render Tasks with Filters
        // ---------------------------------------------
        function fetchTasks() {
            let url = "/api/tasks?";
            if (filterSearch && filterSearch.value) {
                url += `search=${encodeURIComponent(filterSearch.value.trim())}&`;
            }
            if (filterStatus && filterStatus.value) {
                url += `status=${filterStatus.value}&`;
            }
            if (filterPriority && filterPriority.value) {
                url += `priority=${filterPriority.value}&`;
            }

            fetch(url)
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        renderTaskList(data.tasks);
                        updateQuickStats(data.tasks);
                    }
                })
                .catch(err => {
                    console.error("Fetch tasks error:", err);
                    tasksContainer.innerHTML = `
                        <div class="col-12 text-center text-danger py-4">
                            <i class="fa-solid fa-triangle-exclamation fa-2x mb-2"></i>
                            <p class="small mb-0">Failed to sync database. Check local postgres instance.</p>
                        </div>
                    `;
                });
        }

        // Debounced text search to prevent multiple hits
        let searchTimeout;
        if (filterSearch) {
            filterSearch.addEventListener("input", () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(fetchTasks, 300);
            });
        }

        if (filterStatus) filterStatus.addEventListener("change", fetchTasks);
        if (filterPriority) filterPriority.addEventListener("change", fetchTasks);
        
        if (resetFiltersBtn) {
            resetFiltersBtn.addEventListener("click", () => {
                if (filterSearch) filterSearch.value = "";
                if (filterStatus) filterStatus.value = "";
                if (filterPriority) filterPriority.value = "";
                fetchTasks();
            });
        }

        // Render Tasks to DOM
        function renderTaskList(tasks) {
            if (!tasksContainer) return;
            tasksContainer.innerHTML = "";

            if (tasks.length === 0) {
                tasksContainer.innerHTML = `
                    <div class="col-12 text-center py-5 animate-fade-in">
                        <div class="text-muted mb-3">
                            <i class="fa-regular fa-folder-open fa-3x"></i>
                        </div>
                        <h5 class="text-white mb-1">No Tasks Found</h5>
                        <p class="text-muted small">Try modifying your filters or add a new task to get started.</p>
                    </div>
                `;
                return;
            }

            tasks.forEach(task => {
                const dateObj = new Date(task.created_at);
                const formattedDate = dateObj.toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                });

                const cardHTML = `
                    <div class="col-md-6 col-lg-4 animate-scale-in" id="task-card-${task.id}">
                        <div class="card task-card bg-glass rounded-3 p-3 h-100 d-flex flex-column justify-content-between">
                            <div>
                                <div class="d-flex justify-content-between align-items-start gap-2 mb-2">
                                    <h5 class="card-title text-white fs-6 mb-0 text-truncate" title="${escapeHTML(task.title)}">${escapeHTML(task.title)}</h5>
                                    <span class="badge ${getPriorityBadgeClass(task.priority)} fs-xs">${task.priority}</span>
                                </div>
                                <p class="card-text text-muted small mb-3 description-text" style="display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden;">
                                    ${task.description ? escapeHTML(task.description) : '<em class="text-slate-600">No additional details.</em>'}
                                </p>
                            </div>
                            
                            <div class="border-top border-dark-glow pt-2 mt-auto d-flex justify-content-between align-items-center">
                                <div class="d-flex align-items-center gap-1.5">
                                    <span class="badge ${getStatusBadgeClass(task.status)}">${formatStatus(task.status)}</span>
                                    <span class="text-slate-500 text-xs" style="font-size: 0.75rem;"><i class="fa-regular fa-calendar me-1"></i>${formattedDate}</span>
                                </div>
                                <div class="d-flex gap-2">
                                    <!-- Edit Trigger -->
                                    <button class="btn btn-link text-accent-cyan p-0 fs-5 btn-edit-task" data-id="${task.id}" aria-label="Edit Task">
                                        <i class="fa-regular fa-pen-to-square"></i>
                                    </button>
                                    <!-- Delete Trigger -->
                                    <button class="btn btn-link text-danger p-0 fs-5 btn-delete-task" data-id="${task.id}" aria-label="Delete Task">
                                        <i class="fa-regular fa-trash-can"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                tasksContainer.insertAdjacentHTML("beforeend", cardHTML);
            });

            // Bind Event Listeners on newly rendered buttons
            document.querySelectorAll(".btn-delete-task").forEach(btn => {
                btn.addEventListener("click", function() {
                    const id = this.getAttribute("data-id");
                    if (confirm("Are you sure you want to delete this task?")) {
                        deleteTask(id);
                    }
                });
            });

            document.querySelectorAll(".btn-edit-task").forEach(btn => {
                btn.addEventListener("click", function() {
                    const id = this.getAttribute("data-id");
                    openEditModal(id);
                });
            });
        }

        // ---------------------------------------------
        // Quick Count Calculations
        // ---------------------------------------------
        function updateQuickStats(tasks) {
            const totalCount = tasks.length;
            const completedCount = tasks.filter(t => t.status === "COMPLETED").length;
            const pendingCount = tasks.filter(t => t.status === "PENDING").length;

            const totalEl = document.getElementById("stat-total-count");
            const pendingEl = document.getElementById("stat-pending-count");
            const completedEl = document.getElementById("stat-completed-count");
            const progressEl = document.getElementById("stat-completion-pct");

            if (totalEl) totalEl.innerText = totalCount;
            if (pendingEl) pendingEl.innerText = pendingCount;
            if (completedEl) completedEl.innerText = completedCount;

            if (progressEl) {
                const pct = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
                progressEl.innerText = pct + "%";
            }
        }

        // ---------------------------------------------
        // CRUD Operations
        // ---------------------------------------------
        
        // Add Task Submission
        if (addTaskForm) {
            addTaskForm.addEventListener("submit", function (e) {
                e.preventDefault();
                const saveBtn = document.getElementById("btn-save-task");
                saveBtn.disabled = true;
                saveBtn.innerText = "Creating...";

                const payload = {
                    title: document.getElementById("task-title").value,
                    description: document.getElementById("task-description").value,
                    priority: document.getElementById("task-priority").value,
                    status: document.getElementById("task-status").value,
                };

                fetch("/api/tasks", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(payload),
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        // Close Modal
                        const modalEl = document.getElementById("addTaskModal");
                        const modal = bootstrap.Modal.getInstance(modalEl);
                        modal.hide();

                        // Clear input fields
                        addTaskForm.reset();
                        
                        // Sync tasks (Local trigger, socket will also catch it if active)
                        fetchTasks();
                    }
                    saveBtn.disabled = false;
                    saveBtn.innerText = "Create Task";
                })
                .catch(err => {
                    console.error("Create task error:", err);
                    saveBtn.disabled = false;
                    saveBtn.innerText = "Create Task";
                });
            });
        }

        // Open Edit Modal Populate
        function openEditModal(id) {
            fetch(`/api/tasks`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        const task = data.tasks.find(t => t.id == id);
                        if (task) {
                            document.getElementById("edit-task-id").value = task.id;
                            document.getElementById("edit-task-title").value = task.title;
                            document.getElementById("edit-task-description").value = task.description || "";
                            document.getElementById("edit-task-priority").value = task.priority;
                            document.getElementById("edit-task-status").value = task.status;

                            const modal = new bootstrap.Modal(document.getElementById("editTaskModal"));
                            modal.show();
                        }
                    }
                });
        }

        // Edit Task Submission
        if (editTaskForm) {
            editTaskForm.addEventListener("submit", function (e) {
                e.preventDefault();
                const updateBtn = document.getElementById("btn-update-task");
                updateBtn.disabled = true;
                updateBtn.innerText = "Saving...";

                const id = document.getElementById("edit-task-id").value;
                const payload = {
                    title: document.getElementById("edit-task-title").value,
                    description: document.getElementById("edit-task-description").value,
                    priority: document.getElementById("edit-task-priority").value,
                    status: document.getElementById("edit-task-status").value,
                };

                fetch(`/api/tasks/${id}`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(payload),
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        // Close Modal
                        const modalEl = document.getElementById("editTaskModal");
                        const modal = bootstrap.Modal.getInstance(modalEl);
                        modal.hide();

                        fetchTasks();
                    }
                    updateBtn.disabled = false;
                    updateBtn.innerText = "Save Changes";
                })
                .catch(err => {
                    console.error("Update task error:", err);
                    updateBtn.disabled = false;
                    updateBtn.innerText = "Save Changes";
                });
            });
        }

        // Delete Task Action
        function deleteTask(id) {
            fetch(`/api/tasks/${id}`, {
                method: "DELETE",
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    fetchTasks();
                }
            })
            .catch(err => console.error("Delete task error:", err));
        }
    }

    // ---------------------------------------------------------
    // 4. Utility Helper Formatting Routines
    // ---------------------------------------------------------
    
    function getPriorityBadgeClass(priority) {
        switch (priority) {
            case "HIGH": return "badge-priority-high";
            case "MEDIUM": return "badge-priority-medium";
            case "LOW": return "badge-priority-low";
            default: return "badge-secondary";
        }
    }

    function getStatusBadgeClass(status) {
        switch (status) {
            case "COMPLETED": return "badge-completed";
            case "IN_PROGRESS": return "badge-inprogress";
            case "PENDING": return "badge-pending";
            default: return "badge-secondary";
        }
    }

    function formatStatus(status) {
        if (status === "IN_PROGRESS") return "In Progress";
        return status.charAt(0) + status.slice(1).toLowerCase();
    }

    function escapeHTML(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // ---------------------------------------------------------
    // 5. Toast Live Socket Notifications helper
    // ---------------------------------------------------------
    function showToastNotification(eventData) {
        const bodyEl = document.body;
        const toastContainer = document.getElementById("flash-message-container");
        if (!toastContainer) return;

        let message = "";
        let iconClass = "fa-circle-info";
        let bgClass = "bg-primary";

        if (eventData.action === "create") {
            message = `Task Created: "${escapeHTML(eventData.task.title)}"`;
            iconClass = "fa-circle-plus";
            bgClass = "bg-success";
        } else if (eventData.action === "update") {
            message = `Task Updated: "${escapeHTML(eventData.task.title)}"`;
            iconClass = "fa-circle-check";
            bgClass = "bg-info";
        } else if (eventData.action === "delete") {
            message = `Task deleted successfully`;
            iconClass = "fa-trash-can";
            bgClass = "bg-danger";
        } else {
            return;
        }

        const toastHTML = `
            <div class="toast show align-items-center text-white border-0 ${bgClass} shadow-lg animate-fade-in" role="alert" aria-live="assertive" aria-atomic="true" style="margin-top: 10px;">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fa-solid ${iconClass} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML("beforeend", toastHTML);
        
        // Auto-remove toast after 4 seconds
        const toasts = toastContainer.querySelectorAll(".toast");
        const latestToast = toasts[toasts.length - 1];
        setTimeout(() => {
            if (latestToast) latestToast.remove();
        }, 4000);
    }
});
