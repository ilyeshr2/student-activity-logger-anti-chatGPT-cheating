document.getElementById('saveButton').addEventListener('click', function() {
    const studentName = document.getElementById('studentName').value;
    
    if (studentName) {
        chrome.storage.local.set({ studentName: studentName }, function() {
            alert('Student name saved successfully!');
        });
    } else {
        alert('Please enter a valid name.');
    }
});
