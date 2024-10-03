function generateDescription(taskId) {
    const textarea = document.getElementById(`textarea-${taskId}`);
    const aiButton = textarea.nextElementSibling;
    
    aiButton.disabled = true;
    aiButton.innerHTML = '⏳';  // Loading indicator
    
    fetch(`/generate_description/${taskId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            textarea.value = data.description;
            autoResize(textarea);
        })
        .catch(error => {
            alert(`Error: ${error.message}`);
        })
        .finally(() => {
            aiButton.disabled = false;
            aiButton.innerHTML = '✨';
        });
}