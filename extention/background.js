// Event listener for web requests
chrome.webRequest.onCompleted.addListener(
    function(details) {
        const logData = {
            url: details.url,
            timestamp: new Date().toISOString(),
            method: details.method || 'UNKNOWN'
        };

        console.log('Sending log data:', logData);  // Debugging statement

        fetch('http://localhost:5000/api/log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(logData)
        }).catch(error => console.error('Error sending log:', error));
    },
    {urls: ["*://chatgpt.com/*"]}  // Ensure this matches the URL you want to monitor
);


// Optionally, log page visits
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status == 'complete') {
        const logData = {
            url: tab.url,
            timestamp: new Date().toISOString(),
            action: "Page Visit"
        };

        // Send log to server
        fetch('http://localhost:5000/api/log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(logData)
        }).catch(error => console.error('Error sending log:', error));
    }
});
