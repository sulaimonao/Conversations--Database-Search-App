// static/js/search.js

document.addEventListener("DOMContentLoaded", function () {
    const searchButton = document.getElementById("search-button");
    const searchForm = document.getElementById("search-form");
    const searchResultsContainer = document.getElementById("search-results");

    searchButton.addEventListener("click", function () {
        const query = document.getElementById("search-query").value.trim();

        if (!query) {
            alert("Please enter a search query.");
            return;
        }

        // Clear previous results and show a loading message
        searchResultsContainer.innerHTML = "<p>Loading results...</p>";

        fetch(`/search?query=${encodeURIComponent(query)}`)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Search failed with status ${response.status}.`);
                }
                return response.json();
            })
            .then((results) => {
                // Clear previous results
                searchResultsContainer.innerHTML = "";

                if (results.length === 0) {
                    searchResultsContainer.innerHTML = "<p>No results found.</p>";
                    return;
                }

                // Display search results
                results.forEach((result) => {
                    const resultElement = document.createElement("div");
                    resultElement.className = "search-result";

                    if (result.type === "conversation") {
                        resultElement.innerHTML = `
                            <h4>${result.title}</h4>
                            <p><strong>ID:</strong> ${result.conversation_id}</p>
                            <p><strong>Snippet:</strong> ${result.content_snippet}</p>
                            <p><strong>Timestamp:</strong> ${result.timestamp}</p>
                            <a href="/conversation/${result.conversation_id}" class="view-details">
                                View Conversation
                            </a>
                        `;
                    } else if (result.type === "message") {
                        resultElement.innerHTML = `
                            <h4>Message Details</h4>
                            <p><strong>Message ID:</strong> ${result.match.message_id}</p>
                            <p><strong>Content:</strong> ${result.match.content}</p>
                            <p><strong>Author:</strong> ${result.match.author_role}</p>
                            <p><strong>Timestamp:</strong> ${result.match.timestamp}</p>
                            <a href="/conversation/${result.match.conversation_id}" class="view-details">
                                View Conversation
                            </a>
                        `;

                        // Include surrounding messages for context
                        if (result.context && result.context.length > 0) {
                            const contextList = document.createElement("ul");
                            contextList.className = "context-messages";

                            result.context.forEach((contextMessage) => {
                                const contextItem = document.createElement("li");
                                contextItem.innerHTML = `
                                    <strong>${contextMessage.author_role}:</strong> 
                                    ${contextMessage.content} 
                                    (${contextMessage.timestamp})
                                `;
                                contextList.appendChild(contextItem);
                            });

                            const contextWrapper = document.createElement("div");
                            contextWrapper.innerHTML = "<h5>Surrounding Messages:</h5>";
                            contextWrapper.appendChild(contextList);
                            resultElement.appendChild(contextWrapper);
                        }
                    }

                    searchResultsContainer.appendChild(resultElement);
                });
            })
            .catch((error) => {
                console.error("Error during search:", error);
                searchResultsContainer.innerHTML = "<p>An error occurred. Please try again later.</p>";
            });
    });
});
