// // Attach a listener to the query form
// document.getElementById("queryForm").addEventListener("submit", async function (event) {
//     event.preventDefault();

//     // Get user input
//     const userInput = document.getElementById("queryInput").value.trim();

//     // Containers for results
//     const resultsContainer = document.getElementById("resultsContainer");
//     const resultsSection = document.getElementById("resultsSection");

//     // Clear previous results
//     resultsContainer.innerHTML = "";

//     // Show loading message
//     resultsContainer.innerHTML = "<p>Loading...</p>";
//     resultsSection.style.display = "block";

//     try {
//         // Make POST request to Flask API
//         const response = await fetch("http://127.0.0.1:8000/ask", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json",
//             },
//             body: JSON.stringify({ query: userInput }),
//         });

//         // Parse the response
//         if (!response.ok) {
//             throw new Error("Failed to fetch data from the server.");
//         }
//         const data = await response.json();

//         // Display results in the results container
//         if (data.error) {
//             resultsContainer.innerHTML = `<p>Error: ${data.error}</p>`;
//         } else {
//             resultsContainer.innerHTML = `
//                 <p><strong>Response:</strong> ${data.response}</p>
//                 <p><strong>Context:</strong> ${data.context}</p>
//             `;
//         }
//     } catch (error) {
//         // Handle errors
//         resultsContainer.innerHTML = `<p>An error occurred: ${error.message}</p>`;
//     }

//     // Clear the input field
//     document.getElementById("queryInput").value = "";
// });



// Working code - commenting out for testing some other functionality - 19th jan 2025
document.getElementById("queryForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    // Get user input
    const userInput = document.getElementById("queryInput").value.trim();
    const sendButton = document.querySelector("button[type='submit']");
    if (!userInput) return;

    // Disable the send button and change its style
    sendButton.disabled = true;

    // Clear input field immediately after submission
    document.getElementById("queryInput").value = "";

    // Chat window
    const chatWindow = document.getElementById("chatWindow");

    // Append user message
    appendMessage("user", userInput);

    // Append "typing" animation for the bot
    const typingMessage = appendTypingAnimation();

    try {
        // Make POST request to the backend
        const response = await fetch("http://127.0.0.1:8000/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query: userInput }),
        });

        const data = await response.json();

        // Remove "typing" animation
        typingMessage.remove();

        // Append bot response
        if (data.error) {
            appendMessage("bot", `Error: ${data.error}`);
        } else {
            appendMessage("bot", data.response);
        }
    } catch (error) {
        typingMessage.remove();
        appendMessage("bot", `An error occurred: ${error.message}`);
    } finally {
        // Re-enable the send button
        sendButton.disabled = false;
    }

    // Clear input field
    document.getElementById("queryInput").value = "";
});

function appendMessage(sender, message) {
    const chatWindow = document.getElementById("chatWindow");
    const messageDiv = document.createElement("div");
    messageDiv.className = `chat-message ${sender}-message`;

    if (sender === "bot") {
        // Handle structured messages (e.g., lists or multiline text)
        if (message.startsWith("1.") || message.includes("\n")) {
            const pre = document.createElement("div"); // Use <div> for flexibility
            pre.style.whiteSpace = "pre-wrap"; // Preserve formatting with wrapping
            pre.style.wordBreak = "break-word"; // Handle long words
            pre.style.margin = "0"; // Reset margins
            pre.style.fontFamily = "inherit"; // Match font with UI
            pre.style.fontSize = "0.95rem"; // Smaller for readability
            pre.style.lineHeight = "1.2"; // Add line spacing for readability

            // Split the message into lines for processing
            const lines = message.split("\n");
            let index = 0;

            let typingInterval = setInterval(() => {
                if (index < lines.length) {
                    const line = lines[index].trim();

                    // Add spacing between job entries
                    if (/^\d+\.\s/.test(line) && index !== 0) {
                        pre.appendChild(document.createElement("br")); // Extra spacing for clarity
                        pre.appendChild(document.createElement("br"));
                    }

                    // Detect job titles (bold numbered list items)
                    if (/^\d+\.\s/.test(line)) {
                        const [title, ...rest] = line.split(":");
                        const titleSpan = document.createElement("strong");
                        titleSpan.textContent = title.trim(); // Bold job title
                        pre.appendChild(titleSpan);

                        const restSpan = document.createElement("span");
                        restSpan.textContent = ": " + rest.join(":").trim();
                        pre.appendChild(restSpan);
                    } else {
                        // Regular lines
                        const lineSpan = document.createElement("span");
                        lineSpan.textContent = line;
                        pre.appendChild(lineSpan);
                    }

                    pre.appendChild(document.createElement("br")); // Line break after each line
                    chatWindow.scrollTop = chatWindow.scrollHeight;
                    index++;
                } else {
                    clearInterval(typingInterval);
                }
            }, 100); // Typing speed

            messageDiv.appendChild(pre);
        } else {
            // Regular bot message with word-by-word typing
            let words = message.split(" ");
            let index = 0;
            let typingInterval = setInterval(() => {
                if (index < words.length) {
                    messageDiv.textContent += words[index] + " ";
                    chatWindow.scrollTop = chatWindow.scrollHeight;
                    index++;
                } else {
                    clearInterval(typingInterval);
                }
            }, 100); // Typing speed
        }
    } else {
        // For user messages (no typing animation needed)
        messageDiv.textContent = message;
    }

    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function appendTypingAnimation() {
    const chatWindow = document.getElementById("chatWindow");
    const typingDiv = document.createElement("div");
    typingDiv.className = "chat-message bot-message typing";
    typingDiv.innerHTML = `<span>.</span><span>.</span><span>.</span>`;
    chatWindow.appendChild(typingDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return typingDiv;
}


// document.getElementById("queryForm").addEventListener("submit", async function (event) {
//     event.preventDefault();

//     // Get user input
//     const userInput = document.getElementById("queryInput").value.trim();
//     const sendButton = document.querySelector("button[type='submit']");
//     if (!userInput) return;

//     // Disable the send button and clear the input field
//     sendButton.disabled = true;
//     document.getElementById("queryInput").value = "";

//     // Chat window
//     const chatWindow = document.getElementById("chatWindow");

//     // Append user message
//     appendMessage("user", userInput);

//     // Append "typing" animation for the bot
//     const typingMessage = appendTypingAnimation();

//     try {
//         // Decide whether to stream or use non-streaming mode
//         const isStreaming = true; // Set this flag to toggle between streaming or not

//         if (isStreaming) {
//             // STREAMING RESPONSE MODE
//             const response = await fetch("http://127.0.0.1:8000/ask", {
//                 method: "POST",
//                 headers: {
//                     "Content-Type": "application/json",
//                 },
//                 body: JSON.stringify({ query: userInput, as_stream: true }),
//             });

//             // Check if the response is ok
//             if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

//             // Process the streamed response
//             const reader = response.body.getReader();
//             const decoder = new TextDecoder("utf-8");
//             let botResponse = "";

//             while (true) {
//                 const { done, value } = await reader.read();
//                 if (done) break;

//                 // Decode the chunk and process it
//                 const chunk = decoder.decode(value, { stream: true });

//                 // Parse SSE format: Strip "data: " prefix
//                 const cleanedChunk = chunk
//                     .split("\n")
//                     .filter((line) => line.startsWith("data:")) // Only process lines with "data:"
//                     .map((line) => line.replace("data:", "").trim()) // Remove the "data:" prefix
//                     .join(" ");

//                 // Append the cleaned chunk to the bot's response
//                 botResponse += cleanedChunk + " ";

//                 // Update the bot's response dynamically
//                 updateTypingMessage(typingMessage, botResponse);
//             }

//             // Replace the typing message with the final response
//             typingMessage.remove();
//             appendMessage("bot", botResponse.trim());
//         } else {
//             // NON-STREAMING RESPONSE MODE
//             const response = await fetch("http://127.0.0.1:8000/ask", {
//                 method: "POST",
//                 headers: {
//                     "Content-Type": "application/json",
//                 },
//                 body: JSON.stringify({ query: userInput, as_stream: false }),
//             });

//             const data = await response.json();

//             // Remove "typing" animation
//             typingMessage.remove();

//             // Append bot response
//             if (data.error) {
//                 appendMessage("bot", `Error: ${data.error}`);
//             } else {
//                 appendMessage("bot", data.response);
//             }
//         }
//     } catch (error) {
//         typingMessage.remove();
//         appendMessage("bot", `An error occurred: ${error.message}`);
//     } finally {
//         // Re-enable the send button
//         sendButton.disabled = false;
//     }
// });

// // Append user or bot messages
// function appendMessage(sender, message) {
//     const chatWindow = document.getElementById("chatWindow");
//     const messageDiv = document.createElement("div");
//     messageDiv.className = `chat-message ${sender}-message`;
//     messageDiv.textContent = message;
//     chatWindow.appendChild(messageDiv);
//     chatWindow.scrollTop = chatWindow.scrollHeight;
// }

// // Append "typing" animation
// function appendTypingAnimation() {
//     const chatWindow = document.getElementById("chatWindow");
//     const typingDiv = document.createElement("div");
//     typingDiv.className = "chat-message bot-message typing";
//     typingDiv.innerHTML = `<span>.</span><span>.</span><span>.</span>`;
//     chatWindow.appendChild(typingDiv);
//     chatWindow.scrollTop = chatWindow.scrollHeight;
//     return typingDiv;
// }

// // Update typing message dynamically during streaming
// function updateTypingMessage(typingElement, message) {
//     typingElement.textContent = message; // Update the content of the typing message
//     const chatWindow = document.getElementById("chatWindow");
//     chatWindow.scrollTop = chatWindow.scrollHeight; // Keep scrolling to the bottom
// }
