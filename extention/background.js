chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
        // Check if the request URL matches the desired endpoint psk rqnq bqghyin ghir http request ta3 les messages, ki nerslou message
        if (details.url === 'https://chatgpt.com/backend-api/conversation' && details.method === 'POST') {
            // Capture and parse the payload, message nl9ouh f payload ta3 http request (look at the payload.json tfham) 
            const requestBody = details.requestBody;
            if (requestBody && requestBody.raw) {
                const rawData = requestBody.raw.map(part => String.fromCharCode.apply(null, new Uint8Array(part.bytes))).join('');
                try {
                    const payload = JSON.parse(rawData);
                    console.log('Captured Payload:', payload);
                    
                    // Extract the message if it exists
                    if (payload.messages && payload.messages.length > 0) {
                        const userMessages = payload.messages
                            .filter(msg => msg.author.role === 'user')
                            .map(msg => msg.content.parts[0]);
                        console.log('User Messages:', userMessages);

                        // Fetch the student name from local storage
                        chrome.storage.local.get('studentName', function(data) {
                            const studentName = data.studentName || 'Unknown';

                            // Send the data to the server
                            fetch('http://localhost:5000/api/log', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    studentName: studentName,  // Use dynamic student name
                                    url: details.url,
                                    timestamp: new Date().toISOString(),
                                    method: details.method,
                                    userMessages: userMessages
                                })
                            }).catch(error => console.error('Error sending log:', error));
                        });
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
