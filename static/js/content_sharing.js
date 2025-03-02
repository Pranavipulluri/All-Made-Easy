// Get the modal and buttons
const newContentModal = document.getElementById('newContentModal');
const newContentBtn = document.getElementById('newContentBtn');
const closeModalBtn = document.getElementById('closeModalBtn');

// Open the modal when the user clicks the "New Content" button
newContentBtn.onclick = function() {
    newContentModal.style.display = "block";
}

// Close the modal when the user clicks the "X" button
closeModalBtn.onclick = function() {
    newContentModal.style.display = "none";
}

// Close the modal if the user clicks anywhere outside the modal
window.onclick = function(event) {
    if (event.target == newContentModal) {
        newContentModal.style.display = "none";
    }
}

// Handle the form submission (you can replace this with actual backend logic)
document.getElementById('newContentForm').onsubmit = function(e) {
    e.preventDefault();
    // Form submission logic (e.g., AJAX request to server)
    alert("New content uploaded!");
    newContentModal.style.display = "none";
}
