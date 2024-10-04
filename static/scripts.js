function generateBreakdown(taskId) {
    fetch(`/generate_breakdown/${taskId}`, {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`textarea-${taskId}`).value = data.breakdown;
                autoResize(document.getElementById(`textarea-${taskId}`));
            } else {
                alert('Failed to generate breakdown. Please try again.');
            }
        })
        .catch(error => console.error('Error:', error));
}