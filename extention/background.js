chrome.webRequest.onCompleted.addListener(
    function(details) {
        // Fetch the student name from local storage
        chrome.storage.local.get('studentName', function(data) {
            const logData = {
                studentName: data.studentName || 'Unknown',
                url: details.url,
                timestamp: new Date().toISOString(),
                method: details.method || 'UNKNOWN'
            };

            console.log('Sending log data:', logData);

            fetch('http://localhost:5000/api/log', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(logData)
            }).catch(error => console.error('Error sending log:', error));
        });
    },
    {urls: ["*://chatgpt.com/*"]}
);



chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status == 'complete') {
        const logData = {
            url: tab.url,
            timestamp: new Date().toISOString(),
            action: "Page Visit"
        };

        
        fetch('http://localhost:5000/api/log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(logData)
        }).catch(error => console.error('Error sending log:', error));
    }
});
