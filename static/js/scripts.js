document.addEventListener("DOMContentLoaded", () => {
    const addTaskBtn = document.getElementById("add-task-btn");
    const modal = document.getElementById("modal");
    const closeModal = document.getElementById("close-modal");
    const filter = document.getElementById("filter");

    // Open modal
    addTaskBtn.addEventListener("click", () => {
        modal.classList.add("active");
    });

    // Close modal
    closeModal.addEventListener("click", () => {
        modal.classList.remove("active");
    });

    // Filter tasks by category
    filter.addEventListener("change", () => {
        const filterValue = filter.value;
        const taskItems = document.querySelectorAll("#tasks li");

        taskItems.forEach((item) => {
            const category = item.getAttribute("data-category");
            if (filterValue === "all" || filterValue === category) {
                item.style.display = "flex";
            } else {
                item.style.display = "none";
            }
        });
    });
});
