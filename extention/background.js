chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
        // Check if the request URL matches the desired endpoint
        if (details.url === 'https://chatgpt.com/backend-api/conversation' && details.method === 'POST') {
            // Capture and parse the payload
            const requestBody = details.requestBody;
            if (requestBody && requestBody.raw) {
                const rawData = requestBody.raw.map(part => String.fromCharCode.apply(null, new Uint8Array(part.bytes))).join('');
                try {
                    const payload = JSON.parse(rawData);
                    console.log('Captured Payload:', payload);
                    // Extract the message if it exists
                    if (payload.messages && payload.messages.length > 0) {
                        const userMessages = payload.messages.filter(msg => msg.author.role === 'user').map(msg => msg.content.parts[0]);
                        console.log('User Messages:', userMessages);
                        
                        // Send the data to the server
                        fetch('http://localhost:5000/api/log', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                studentName: 'ishak',  // You might want to replace this with dynamic data
                                url: details.url,
                                timestamp: new Date().toISOString(),
                                method: details.method,
                                userMessages: userMessages
                            })
                        }).catch(error => console.error('Error sending log:', error));
                    }
                } catch (e) {
                    console.error('Error parsing payload:', e);
                }
            }
        }
    },
    {urls: ["*://chatgpt.com/backend-api/conversation"]},
    ['requestBody']
);

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete') {
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
